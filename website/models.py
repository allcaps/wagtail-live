from django.db import models
from django.template.defaultfilters import truncatewords
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from website.blocks import Embed

BLOCK_TYPES = [
    ('embed', Embed()),
]


class LiveBlog(Page):
    body = StreamField(BLOCK_TYPES, blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    @property
    def group_name(self):
        return 'liveblog-{}'.format(self.pk)


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

    def __str__(self):
        return truncatewords(self.message, 20)


class HomePage(Page):
    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx.update({
            'pages': LiveBlog.objects.live()
        })
        return ctx
