from django.db import models
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Repository(models.Model):
    """
    Repository model supporting both SVN and Git version control systems.
    """
    
    VCS_CHOICES = [
        ('svn', 'Subversion'),
        ('git', 'Git'),
    ]
    
    # Basic repository information
    name = models.CharField('name', max_length=50)
    desc = models.CharField('description', max_length=250, null=True, blank=True)
    url = models.CharField('repository url', max_length=500)
    
    # VCS type and configuration
    vcs_type = models.CharField('VCS Type', max_length=10, choices=VCS_CHOICES, default='svn')
    branch = models.CharField('Branch', max_length=100, default='main', blank=True,
                             help_text='Git branch to monitor (default: main)')
    
    # Authentication (common for both SVN and Git)
    username = models.CharField('username', max_length=50, blank=True)
    password = models.CharField('password', max_length=50, blank=True)
    
    # Git-specific authentication
    ssh_key_path = models.CharField('SSH Key Path', max_length=500, blank=True,
                                   help_text='Path to SSH private key for Git repositories')
    access_token = models.CharField('Access Token', max_length=500, blank=True,
                                   help_text='GitHub/GitLab access token')
    
    # Optional source view URL
    sourceview = models.CharField('source view', max_length=500, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'commits_repository'
        verbose_name = 'Repository'
        verbose_name_plural = 'Repositories'

    def __str__(self):
        return f"{self.name} ({self.vcs_type.upper()})"

    def get_vcs_client(self):
        """
        Get the appropriate VCS client based on the repository type.
        """
        if self.vcs_type == 'svn':
            from .vcs.svn_client import SVNClient
            return SVNClient(
                repo_url=self.url,
                username=self.username,
                password=self.password
            )
        elif self.vcs_type == 'git':
            from .vcs.git_client import GitClient
            return GitClient(
                repo_url=self.url,
                branch=self.branch or 'main',
                username=self.username,
                password=self.password,
                ssh_key_path=self.ssh_key_path,
                access_token=self.access_token
            )
        else:
            raise ValueError(f"Unsupported VCS type: {self.vcs_type}")

    def clear(self):
        """Clear all commits for this repository."""
        CommitLog.objects.filter(repository=self).delete()

    def update(self):
        """
        Update the repository by fetching new commits.
        """
        try:
            client = self.get_vcs_client()
            
            # Test connection first
            if not client.test_connection():
                logger.error(f'Connection test failed for repository {self.name}')
                return False
            
            # Get last stored revision/commit
            last_stored_rev = self.getLastStoredRev()
            
            # Get new commits
            if self.vcs_type == 'svn':
                latest_rev = client.get_latest_revision()
                start_rev = max(1, int(last_stored_rev or '0') + 1)
                end_rev = int(latest_rev)
                
                if start_rev <= end_rev:
                    commits = client.get_commits(
                        start_revision=str(start_rev),
                        end_revision=str(end_rev)
                    )
                else:
                    commits = []
            else:  # Git
                commits = client.get_new_commits(last_stored_rev)
            
            # Store new commits
            new_commits_count = 0
            for commit in commits:
                if self.store_commit(commit):
                    new_commits_count += 1
            
            # Update last sync time
            self.last_sync = datetime.now()
            self.save(update_fields=['last_sync'])
            
            logger.info(f'Updated repository {self.name}: {new_commits_count} new commits')
            return True
            
        except Exception as e:
            logger.error(f'Exception updating repository {self.name}: {e}')
            return False

    def store_commit(self, vcs_commit):
        """
        Store a VCS commit in the database.
        
        Args:
            vcs_commit: VCSCommit object from the VCS client
            
        Returns:
            bool: True if commit was stored successfully
        """
        try:
            # Get or create author
            author = self.get_or_create_author(
                vcs_commit.author, 
                vcs_commit.author_email
            )
            
            # Check if commit already exists
            if CommitLog.objects.filter(
                repository=self,
                revision=vcs_commit.revision
            ).exists():
                return False  # Already exists
            
            # Create new commit log
            commit_log = CommitLog(
                repository=self,
                revision=vcs_commit.revision,
                time=vcs_commit.timestamp,
                author=author,
                comment=vcs_commit.message
            )
            commit_log.save()
            
            logger.debug(f'Stored commit {vcs_commit.revision} for {self.name}')
            return True
            
        except Exception as e:
            logger.error(f'Error storing commit {vcs_commit.revision}: {e}')
            return False

    def get_or_create_author(self, account, email=''):
        """
        Get or create an author record.
        """
        try:
            # Try to find by account name first
            author = Author.objects.get(account=account)
        except Author.DoesNotExist:
            # Try to find by email if provided
            if email:
                try:
                    author = Author.objects.get(email=email)
                    # Update account name if different
                    if author.account != account:
                        author.account = account
                        author.save()
                except Author.DoesNotExist:
                    author = None
            
            if not author:
                # Create new author
                author = Author(
                    account=account,
                    display=account,  # Default display name
                    email=email
                )
                author.save()
        
        return author

    def getLastStoredRev(self):
        """
        Get the last stored revision/commit hash.
        """
        try:
            last_commit = self.commits.order_by('-id').first()
            if last_commit:
                return last_commit.revision
            return None
        except Exception:
            return None


class Author(models.Model):
    """
    Author model for tracking commit authors across VCS.
    """
    account = models.CharField('account name', max_length=50)
    display = models.CharField('display name', max_length=50, blank=True)
    email = models.EmailField('email address', max_length=254, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'commits_author'
        unique_together = [['account', 'email']]
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        if self.display:
            return self.display
        return self.account

    def save(self, *args, **kwargs):
        # Auto-generate display name if not provided
        if not self.display:
            self.display = self.account
        super().save(*args, **kwargs)


class CommitLog(models.Model):
    """
    Commit log model for storing VCS commits.
    """
    repository = models.ForeignKey(Repository, related_name='commits', on_delete=models.CASCADE)
    revision = models.CharField('revision/commit hash', max_length=100)  # Supports both SVN rev numbers and Git hashes
    time = models.DateTimeField('commit time')
    author = models.ForeignKey(Author, related_name='commits', on_delete=models.CASCADE)
    comment = models.TextField('commit comment')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'commits_commitlog'
        unique_together = [['repository', 'revision']]
        indexes = [
            models.Index(fields=['repository', 'time']),
            models.Index(fields=['author', 'time']),
            models.Index(fields=['time']),
        ]
        verbose_name = 'Commit Log'
        verbose_name_plural = 'Commit Logs'
        ordering = ['-time']

    def __str__(self):
        if self.repository.vcs_type == 'svn':
            return f'r{self.revision}'
        else:
            return f'{self.revision[:8]}...'  # Show first 8 chars of Git hash

    def get_short_revision(self):
        """Get a short version of the revision for display."""
        if self.repository.vcs_type == 'svn':
            return f'r{self.revision}'
        else:
            return self.revision[:8]

    def get_commit_url(self):
        """Generate commit URL if sourceview is configured."""
        if not self.repository.sourceview:
            return None
        
        if self.repository.vcs_type == 'svn':
            return f"{self.repository.sourceview}?view=revision&revision={self.revision}"
        else:
            # Assume GitHub/GitLab style URLs
            return f"{self.repository.sourceview}/commit/{self.revision}"


def UpdateRepositories():
    """
    Update all repositories by fetching new commits.
    """
    updated_count = 0
    failed_count = 0
    
    for repo in Repository.objects.all():
        try:
            if repo.update():
                updated_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(f'Failed to update repository {repo.name}: {e}')
            failed_count += 1
    
    logger.info(f'Repository update completed: {updated_count} successful, {failed_count} failed')
    return updated_count, failed_count
