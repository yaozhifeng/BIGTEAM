"""
Git VCS client implementation.
"""

import os
import tempfile
import shutil
from datetime import datetime
from typing import List, Optional
import logging

try:
    import git
    from git import Repo, InvalidGitRepositoryError, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

from .base import BaseVCSClient, VCSCommit

logger = logging.getLogger(__name__)


class GitClient(BaseVCSClient):
    """
    Git repository client implementation.
    """
    
    def __init__(self, repo_url: str, branch: str = 'main', 
                 username: str = '', password: str = '',
                 ssh_key_path: str = '', access_token: str = ''):
        super().__init__(repo_url, username, password)
        self.branch = branch or 'main'
        self.ssh_key_path = ssh_key_path
        self.access_token = access_token
        self.local_path = None
        self.repo = None
        
        if not GIT_AVAILABLE:
            raise ImportError("GitPython is required for Git support. Install it with: pip install GitPython")
    
    def _get_auth_url(self) -> str:
        """
        Get URL with authentication embedded for HTTPS repositories.
        """
        if self.access_token:
            # For GitHub/GitLab token authentication
            if 'github.com' in self.repo_url:
                return self.repo_url.replace('https://', f'https://{self.access_token}@')
            elif 'gitlab.com' in self.repo_url:
                return self.repo_url.replace('https://', f'https://oauth2:{self.access_token}@')
        
        if self.username and self.password:
            return self.repo_url.replace('https://', f'https://{self.username}:{self.password}@')
        
        return self.repo_url
    
    def _setup_local_repo(self):
        """
        Set up local repository for operations.
        """
        if self.local_path and os.path.exists(self.local_path):
            try:
                self.repo = Repo(self.local_path)
                return
            except InvalidGitRepositoryError:
                # Clean up and re-clone
                shutil.rmtree(self.local_path)
        
        # Create temporary directory for repository
        self.local_path = tempfile.mkdtemp(prefix='bigteam_git_')
        
        try:
            auth_url = self._get_auth_url()
            self.logger.info(f"Cloning repository: {self.repo_url}")
            
            # Clone the repository
            self.repo = Repo.clone_from(auth_url, self.local_path, branch=self.branch)
            
        except GitCommandError as e:
            self.logger.error(f"Failed to clone repository: {e}")
            if self.local_path and os.path.exists(self.local_path):
                shutil.rmtree(self.local_path)
            raise
    
    def authenticate(self) -> bool:
        """
        Test authentication by attempting to access the repository.
        """
        try:
            self._setup_local_repo()
            return True
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def get_latest_revision(self) -> str:
        """
        Get the latest commit SHA from the specified branch.
        """
        if not self.repo:
            self._setup_local_repo()
        
        try:
            # Update to latest
            origin = self.repo.remotes.origin
            origin.pull(self.branch)
            
            # Get latest commit SHA
            latest_commit = self.repo.head.commit
            return latest_commit.hexsha
            
        except GitCommandError as e:
            self.logger.error(f"Failed to get latest revision: {e}")
            raise
    
    def get_commits(self, 
                   start_revision: str = None, 
                   end_revision: str = None,
                   since_date: datetime = None) -> List[VCSCommit]:
        """
        Get commits from the Git repository.
        """
        if not self.repo:
            self._setup_local_repo()
        
        commits = []
        
        try:
            # Update repository
            origin = self.repo.remotes.origin
            origin.pull(self.branch)
            
            # Build revision range
            rev_range = self.branch
            if start_revision and end_revision:
                rev_range = f"{start_revision}..{end_revision}"
            elif end_revision:
                rev_range = end_revision
            elif since_date:
                # Git uses ISO format for --since
                since_str = since_date.strftime('%Y-%m-%d')
                rev_range = f"{self.branch} --since='{since_str}'"
            
            # Get commits
            for commit in self.repo.iter_commits(rev_range, max_count=1000):
                vcs_commit = VCSCommit(
                    revision=commit.hexsha,
                    author=self.normalize_author(commit.author.name, commit.author.email),
                    author_email=commit.author.email,
                    timestamp=datetime.fromtimestamp(commit.committed_date),
                    message=commit.message.strip(),
                    files_changed=[item.a_path or item.b_path for item in commit.stats.files.keys()]
                )
                commits.append(vcs_commit)
            
            self.logger.info(f"Retrieved {len(commits)} commits from Git repository")
            return commits
            
        except GitCommandError as e:
            self.logger.error(f"Failed to get commits: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test connection to the Git repository.
        """
        try:
            # Try to list remote refs
            auth_url = self._get_auth_url()
            refs = git.cmd.Git().ls_remote(auth_url)
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def cleanup(self):
        """
        Clean up temporary local repository.
        """
        if self.local_path and os.path.exists(self.local_path):
            try:
                shutil.rmtree(self.local_path)
                self.local_path = None
                self.repo = None
            except Exception as e:
                self.logger.error(f"Failed to cleanup local repository: {e}")
    
    def __del__(self):
        """
        Ensure cleanup on object destruction.
        """
        self.cleanup()