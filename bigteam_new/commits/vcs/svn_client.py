"""
SVN VCS client implementation - wrapper around existing SVN code.
"""

from datetime import datetime
from typing import List, Optional
import logging

try:
    from ..svnclient.svnlogclient import SVNLogClient as OriginalSVNClient
    from ..svnclient.svnlogiter import SVNRevLogIter
    SVN_AVAILABLE = True
except ImportError:
    SVN_AVAILABLE = False

from .base import BaseVCSClient, VCSCommit

logger = logging.getLogger(__name__)


class SVNClient(BaseVCSClient):
    """
    SVN repository client implementation - wraps existing SVN functionality.
    """
    
    def __init__(self, repo_url: str, username: str = '', password: str = ''):
        super().__init__(repo_url, username, password)
        self.svn_client = None
        
        if not SVN_AVAILABLE:
            raise ImportError("SVN client modules are not available")
    
    def _get_svn_client(self):
        """
        Get or create SVN client instance.
        """
        if not self.svn_client:
            self.svn_client = OriginalSVNClient(
                self.repo_url, 
                username=self.username, 
                password=self.password
            )
        return self.svn_client
    
    def authenticate(self) -> bool:
        """
        Test authentication with SVN server.
        """
        try:
            client = self._get_svn_client()
            # Try to get head revision as authentication test
            client.getHeadRevNo()
            return True
        except Exception as e:
            self.logger.error(f"SVN authentication failed: {e}")
            return False
    
    def get_latest_revision(self) -> str:
        """
        Get the latest revision number from SVN.
        """
        try:
            client = self._get_svn_client()
            rev_no = client.getHeadRevNo()
            return str(rev_no)
        except Exception as e:
            self.logger.error(f"Failed to get latest SVN revision: {e}")
            raise
    
    def get_commits(self, 
                   start_revision: Optional[str] = None, 
                   end_revision: Optional[str] = None,
                   since_date: Optional[datetime] = None) -> List[VCSCommit]:
        """
        Get commits from SVN repository.
        """
        commits = []
        
        try:
            client = self._get_svn_client()
            
            # Convert string revisions to integers
            start_rev = int(start_revision) if start_revision else None
            end_rev = int(end_revision) if end_revision else None
            
            if not start_rev and not end_rev:
                # Get recent commits if no range specified
                latest_rev = client.getHeadRevNo()
                start_rev = max(1, latest_rev - 100)  # Last 100 commits
                end_rev = latest_rev
            elif not start_rev:
                start_rev = 1
            elif not end_rev:
                end_rev = client.getHeadRevNo()
            
                         # Use existing SVN iterator
             svn_logs = SVNRevLogIter(client, start_rev, end_rev)
             
             for rev_log in svn_logs:
                 if rev_log.isvalid():
                     # Get changed file paths
                     changed_files = []
                     try:
                         for change_entry in rev_log.getChangeEntries():
                             changed_files.append(change_entry.filepath())
                     except:
                         changed_files = []
                     
                     # Convert SVN log to VCSCommit
                     vcs_commit = VCSCommit(
                         revision=str(rev_log.revno),
                         author=self.normalize_author(str(rev_log.author)),
                         author_email='',  # SVN doesn't typically have emails
                         timestamp=rev_log.date,
                         message=str(rev_log.message),
                         files_changed=changed_files
                     )
                     commits.append(vcs_commit)
            
            self.logger.info(f"Retrieved {len(commits)} commits from SVN repository")
            return commits
            
        except Exception as e:
            self.logger.error(f"Failed to get SVN commits: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test connection to SVN repository.
        """
        try:
            client = self._get_svn_client()
            # Try to get repository info
            client.getHeadRevNo()
            return True
        except Exception as e:
            self.logger.error(f"SVN connection test failed: {e}")
            return False