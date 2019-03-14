from django.conf.urls import url

from .api import Event
from . import views

urlpatterns = [
    url(r'^event/$', Event.as_view()),
    url(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),
]
