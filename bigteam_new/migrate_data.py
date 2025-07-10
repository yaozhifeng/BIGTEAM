#!/usr/bin/env python
"""
Data migration script for BigTeam Django upgrade.
This script helps migrate data from the old Django 1.x version to Django 4.2.
"""

import os
import sys
import django
import sqlite3
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigteam.settings')
django.setup()

from commits.models import Repository, Author, CommitLog


def migrate_data_from_old_db(old_db_path):
    """
    Migrate data from old BigTeam database to new structure.
    """
    print(f"Starting data migration from {old_db_path}")
    
    # Connect to old database
    old_conn = sqlite3.connect(old_db_path)
    old_conn.row_factory = sqlite3.Row  # Enable column access by name
    old_cursor = old_conn.cursor()
    
    try:
        # Migrate repositories
        print("Migrating repositories...")
        old_cursor.execute("SELECT * FROM commits_repository")
        old_repos = old_cursor.fetchall()
        
        for old_repo in old_repos:
            repo, created = Repository.objects.get_or_create(
                id=old_repo['id'],
                defaults={
                    'name': old_repo['name'],
                    'desc': old_repo['desc'] or '',
                    'url': old_repo['url'],
                    'vcs_type': 'svn',  # Old repos were SVN
                    'username': old_repo['username'] or '',
                    'password': old_repo['password'] or '',
                    'sourceview': old_repo['sourceview'] or '',
                }
            )
            if created:
                print(f"  Created repository: {repo.name}")
            else:
                print(f"  Repository already exists: {repo.name}")
        
        # Migrate authors
        print("Migrating authors...")
        old_cursor.execute("SELECT * FROM commits_author")
        old_authors = old_cursor.fetchall()
        
        for old_author in old_authors:
            author, created = Author.objects.get_or_create(
                id=old_author['id'],
                defaults={
                    'account': old_author['account'],
                    'display': old_author['display'] or old_author['account'],
                    'email': '',  # Old model didn't have email
                }
            )
            if created:
                print(f"  Created author: {author.account}")
        
        # Migrate commit logs
        print("Migrating commit logs...")
        old_cursor.execute("SELECT * FROM commits_commitlog")
        old_commits = old_cursor.fetchall()
        
        commit_count = 0
        for old_commit in old_commits:
            try:
                # Get related objects
                repository = Repository.objects.get(id=old_commit['repository_id'])
                author = Author.objects.get(id=old_commit['author_id'])
                
                commit_log, created = CommitLog.objects.get_or_create(
                    id=old_commit['id'],
                    defaults={
                        'repository': repository,
                        'revision': str(old_commit['revision']),  # Convert to string
                        'time': old_commit['time'],
                        'author': author,
                        'comment': old_commit['comment'],
                    }
                )
                if created:
                    commit_count += 1
                    if commit_count % 100 == 0:
                        print(f"  Migrated {commit_count} commits...")
                        
            except Exception as e:
                print(f"  Error migrating commit {old_commit['id']}: {e}")
        
        print(f"  Total commits migrated: {commit_count}")
        
        # Print summary
        print("\nMigration Summary:")
        print(f"  Repositories: {Repository.objects.count()}")
        print(f"  Authors: {Author.objects.count()}")
        print(f"  Commits: {CommitLog.objects.count()}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise
    finally:
        old_conn.close()


def update_existing_data():
    """
    Update existing data to match new model requirements.
    """
    print("Updating existing data...")
    
    # Update repositories without VCS type
    svn_repos = Repository.objects.filter(vcs_type='')
    if svn_repos.exists():
        svn_repos.update(vcs_type='svn')
        print(f"  Updated {svn_repos.count()} repositories to SVN type")
    
    # Update authors without display names
    authors_without_display = Author.objects.filter(display='')
    for author in authors_without_display:
        author.display = author.account
        author.save()
    print(f"  Updated {authors_without_display.count()} authors with display names")
    
    # Update commit revisions to strings if needed
    commits_to_update = CommitLog.objects.filter(revision__isnull=True)
    if commits_to_update.exists():
        print(f"  Found {commits_to_update.count()} commits with null revisions")


def verify_migration():
    """
    Verify that the migration was successful.
    """
    print("\nVerifying migration...")
    
    # Check basic counts
    repo_count = Repository.objects.count()
    author_count = Author.objects.count()
    commit_count = CommitLog.objects.count()
    
    print(f"  Repositories: {repo_count}")
    print(f"  Authors: {author_count}")
    print(f"  Commits: {commit_count}")
    
    # Check for any data issues
    repos_without_vcs = Repository.objects.filter(vcs_type='')
    if repos_without_vcs.exists():
        print(f"  WARNING: {repos_without_vcs.count()} repositories without VCS type")
    
    authors_without_display = Author.objects.filter(display='')
    if authors_without_display.exists():
        print(f"  WARNING: {authors_without_display.count()} authors without display names")
    
    commits_without_revision = CommitLog.objects.filter(revision='')
    if commits_without_revision.exists():
        print(f"  WARNING: {commits_without_revision.count()} commits without revision")
    
    print("Migration verification complete!")


def main():
    """
    Main migration function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate BigTeam data to Django 4.2')
    parser.add_argument('--old-db', help='Path to old bigteam.db file')
    parser.add_argument('--update-only', action='store_true', 
                       help='Only update existing data, do not migrate from old DB')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify existing data')
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_migration()
        return
    
    if args.update_only:
        update_existing_data()
        verify_migration()
        return
    
    if not args.old_db:
        print("Please provide the path to the old database file using --old-db")
        return
    
    if not os.path.exists(args.old_db):
        print(f"Old database file not found: {args.old_db}")
        return
    
    try:
        # Run migrations first
        print("Running Django migrations...")
        os.system("python manage.py migrate")
        
        # Migrate data
        migrate_data_from_old_db(args.old_db)
        
        # Update existing data
        update_existing_data()
        
        # Verify migration
        verify_migration()
        
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the application: python manage.py runserver")
        print("2. Create a superuser: python manage.py createsuperuser")
        print("3. Access admin at: http://localhost:8000/admin/")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()