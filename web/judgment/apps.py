from django.apps import AppConfig


class JudgmentConfig(AppConfig):
    name = 'judgment'

    def ready(self):
        import judgment.signals
