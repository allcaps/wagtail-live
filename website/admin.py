from django.contrib import admin

from website.models import Snippet


@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = [
        'message'
    ]
