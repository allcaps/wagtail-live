from datetime import datetime

from django.db import models
from django.db.models.signals import ModelSignal
from django.template.defaultfilters import truncatewords
from django.utils.timezone import now
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import StreamFieldPanel, InlinePanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from website.blocks import Embed, TextUpdate

BLOCK_TYPES = [
    ('embed', Embed()),
    ('text', TextUpdate()),
]

blog_update = ModelSignal(providing_args=['instance', 'num_updates'],
                          use_caching=True)


class LiveBlog(Page):
    body = StreamField(BLOCK_TYPES, blank=True)
    last_updated = models.DateTimeField(default=datetime.min)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        InlinePanel('live_updates'),
    ]

    def update(self):
        """ apply all pending updates """
        def get_pending_updates():
            return PendingUpdate.objects.filter(
                live_blog=self,
                timestamp__gt=self.last_updated).order_by('timestamp')

        if self.locked:
            return

        # Set lock
        self.locked = True
        self.save()

        try:
            # Apply updates
            pending_updates = get_pending_updates()
            items = self.body.stream_data
            for update in pending_updates:
                items.append({
                    'type': 'text',
                    'value': {
                        'message_id': update.slack_id,
                        'timestamp': update.timestamp,
                        'message': update.raw_update,
                    }
                })
            self.last_updated = now()
            self.save()
            num_updates = int(pending_updates.count())
            # These are handled
            pending_updates.delete()

            blog_update.send(sender=LiveBlog, instance=self,
                             num_updates=num_updates)
        finally:
            # Unset lock
            self.locked = False
            self.save()

        # Test if there were new updates while the page was locked and
        # publishing. This would still be the moment to handle them
        pending_updates = get_pending_updates()
        if pending_updates:
            self.update()

    @property
    def group_name(self):
        return 'liveblog-{}'.format(self.pk)


class Snippet(ClusterableModel):
    page = ParentalKey(
        LiveBlog,
        related_name='live_updates',
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


class PendingUpdate(models.Model):
    """ Pending updates will be added asap! """
    live_blog = models.ForeignKey(LiveBlog, on_delete=models.CASCADE)
    slack_id = models.CharField(max_length=40)
    raw_update = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class HomePage(Page):
    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx.update({
            'pages': LiveBlog.objects.live()
        })
        return ctx
