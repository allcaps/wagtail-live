import json

from asgiref.sync import async_to_sync
from django.db import models
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from website.blocks import Embed

BLOCK_TYPES = [
    ('embed', Embed()),
]


class LiveBlog(Page):
    body = StreamField(BLOCK_TYPES)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]


class Snippet(models.Model):
    page = models.ForeignKey(
        LiveBlog,
        on_delete=models.CASCADE,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(
        max_length=255,
    )

    def save(self, *args, **kwags):
        super(Snippet, self).save(*args, **kwags)
        # from websocket import create_connection
        # ws = create_connection("ws://127.0.0.1:6379")
        # ws.send("Hello, World")


class HomePage(Page):
    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx.update({
            'pages': LiveBlog.objects.live()
        })
        return ctx
