from django.apps import AppConfig


class ImageprocessorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'imageprocessor'

    def ready(self):
        print('ready')
        from . import image_processor
        image_processor.run_preprocessing()
        
