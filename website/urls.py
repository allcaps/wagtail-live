from django.conf.urls import url

from .api import Event

urlpatterns = [
    url(r'^event/$', Event.as_view()),
]
