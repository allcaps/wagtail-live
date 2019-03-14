from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    name = 'website'
    verbose_name = "Website"

    def ready(self):
        from . import signals  # noqa
