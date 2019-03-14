from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Snippet


class SnippetAdmin(ModelAdmin):
    model = Snippet
    list_filter = [
        'page',
    ]

modeladmin_register(SnippetAdmin)
