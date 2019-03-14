import json

import channels.layers
from asgiref.sync import async_to_sync

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Snippet


def send_message(event):
    """
    Call back function to send message to the browser
    """
    message = event['text']
    channel_layer = channels.layers.get_channel_layer()
    # Send message to WebSocket
    async_to_sync(channel_layer.send)(text_data=json.dumps(
        message
    ))


@receiver(post_save, sender=Snippet)
def update_job_status_listeners(sender, instance, **kwargs):
    """
    Sends job status to the browser when a Job is modified
    """
    group_name = instance.page.group_name

    message = {
        'type': 'chat_message',
        'message': instance.message
    }

    channel_layer = channels.layers.get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'chat_message',
            'message': message
        }
    )
