"""
Abstract base class for Version Control System clients.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VCSCommit:
    """
    Standard commit representation across different VCS.
    """
    def __init__(self, 
                 revision: str,
                 author: str,
                 author_email: str = '',
                 timestamp: Optional[datetime] = None,
                 message: str = '',
                 files_changed: Optional[List[str]] = None):
        self.revision = revision
        self.author = author
        self.author_email = author_email
        self.timestamp = timestamp or datetime.now()
        self.message = message
        self.files_changed = files_changed or []
    
    def __str__(self):
        return f"{self.revision}: {self.message[:50]}..."
    
    def __repr__(self):
        return f"VCSCommit(revision='{self.revision}', author='{self.author}')"


class BaseVCSClient(ABC):
    """
    Abstract base class for all VCS clients.
    """
    
    def __init__(self, repo_url: str, username: str = '', password: str = ''):
        self.repo_url = repo_url
        self.username = username
        self.password = password
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the VCS server.
        Returns True if authentication is successful.
        """
        pass
    
    @abstractmethod
    def get_latest_revision(self) -> str:
        """
        Get the latest revision identifier.
        """
        pass
    
    @abstractmethod
    def get_commits(self, 
                   start_revision: Optional[str] = None, 
                   end_revision: Optional[str] = None,
                   since_date: Optional[datetime] = None) -> List[VCSCommit]:
        """
        Get commits from the repository.
        
        Args:
            start_revision: Starting revision (inclusive)
            end_revision: Ending revision (inclusive)
            since_date: Get commits since this date
            
        Returns:
            List of VCSCommit objects
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if the connection to the repository is working.
        """
        pass
    
    def get_new_commits(self, last_known_revision: Optional[str] = None) -> List[VCSCommit]:
        """
        Get new commits since the last known revision.
        """
        try:
            latest = self.get_latest_revision()
            if not last_known_revision:
                # If no last known revision, get recent commits
                return self.get_commits(end_revision=latest)
            
            if last_known_revision == latest:
                return []  # No new commits
            
            return self.get_commits(start_revision=last_known_revision, 
                                  end_revision=latest)
        except Exception as e:
            self.logger.error(f"Error getting new commits: {e}")
            return []
    
    def normalize_author(self, author: str, email: str = '') -> str:
        """
        Normalize author name for consistency across VCS.
        """
        if email and '@' in email:
            # Extract username from email if no separate author name
            if not author or author == email:
                author = email.split('@')[0]
        
        # Clean up author name
        author = author.strip()
        if author.startswith('<') and author.endswith('>'):
            author = author[1:-1]
        
        return author or 'unknown'