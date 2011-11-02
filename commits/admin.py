from models import Repository, CommitLog, Author
from django.contrib import admin

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'desc', 'url']
    actions = ['update']

    def update(self, request, queryset):
        for rep in queryset:
            rep.update()

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['account', 'display']

class CommitAdmin(admin.ModelAdmin):
    list_display = ['revision', 'time', 'author', 'comment']
    list_filter = ['repository', 'author']

admin.site.register(Repository, RepositoryAdmin)
admin.site.register(CommitLog, CommitAdmin)
admin.site.register(Author, AuthorAdmin)

