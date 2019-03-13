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


class HomePage(Page):
    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx.update({
            'pages': LiveBlog.objects.live()
        })
        return ctx
