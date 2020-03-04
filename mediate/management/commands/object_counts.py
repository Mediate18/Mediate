from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Counts objects of the specified models.'

    def add_arguments(self, parser):
        # Positional
        parser.add_argument('model', type=str, nargs='+',
                            help='One or more string references of a model of the form <app name>__<model name>')

    def handle(self, *args, **kwargs):
        # Get the command line arguments
        models = kwargs['model']
        for model_string in models:
            app, model_name = model_string.split('__', 1)
            try:
                count = apps.get_model(app, model_name).objects.count()
                print("App {}, model {}: {}".format(app, model_name, count))
            except:
                print("Count not process model {} in app {}".format(model_name, app))
