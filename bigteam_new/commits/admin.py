from django.contrib import admin
from .models import Repository, CommitLog, Author


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'vcs_type', 'url', 'last_sync', 'commit_count')
    list_filter = ('vcs_type', 'created_at', 'last_sync')
    search_fields = ('name', 'desc', 'url')
    readonly_fields = ('created_at', 'updated_at', 'last_sync')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'desc', 'url', 'sourceview')
        }),
        ('VCS Configuration', {
            'fields': ('vcs_type', 'branch'),
            'description': 'Version Control System settings'
        }),
        ('Authentication', {
            'fields': ('username', 'password', 'ssh_key_path', 'access_token'),
            'classes': ('collapse',),
            'description': 'Authentication credentials for repository access'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_sync'),
            'classes': ('collapse',),
        }),
    )
    
    def commit_count(self, obj):
        return obj.commits.count()
    commit_count.short_description = 'Commits'
    
    actions = ['update_repositories']
    
    def update_repositories(self, request, queryset):
        updated_count = 0
        for repo in queryset:
            if repo.update():
                updated_count += 1
        
        self.message_user(
            request,
            f'Successfully updated {updated_count} of {queryset.count()} repositories.'
        )
    update_repositories.short_description = 'Update selected repositories'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('account', 'display', 'email', 'commit_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('account', 'display', 'email')
    readonly_fields = ('created_at',)
    
    def commit_count(self, obj):
        return obj.commits.count()
    commit_count.short_description = 'Commits'


@admin.register(CommitLog)
class CommitLogAdmin(admin.ModelAdmin):
    list_display = ('get_short_revision', 'repository', 'author', 'time', 'short_comment')
    list_filter = ('repository', 'time', 'repository__vcs_type')
    search_fields = ('revision', 'comment', 'author__account', 'author__display')
    readonly_fields = ('created_at',)
    date_hierarchy = 'time'
    
    def get_short_revision(self, obj):
        return obj.get_short_revision()
    get_short_revision.short_description = 'Revision'
    
    def short_comment(self, obj):
        if len(obj.comment) > 50:
            return obj.comment[:50] + '...'
        return obj.comment
    short_comment.short_description = 'Comment'
    
    def get_queryset(self, request):
        # Optimize queries by selecting related objects
        return super().get_queryset(request).select_related('repository', 'author')

