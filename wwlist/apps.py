from django.apps import AppConfig


class WwlistConfig(AppConfig):
    name = 'wwlist'

    def ready(self):
        import wwlist.signals
