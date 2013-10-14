from django.core.management.base import BaseCommand
from django.db.models import get_models, get_app
from django.contrib.auth.management import create_permissions

class Command(BaseCommand):
    args = '<app app ...>'
    help = 'Sync new permissions for specified apps with the database, or all apps if no args are specified'

    def handle(self, *args, **options):

        verbosity = options.get('verbosity')
        verbose = False if verbosity == '0' else True
        apps = []

        if not args:
            for model in get_models():
                apps.append(get_app(model._meta.app_label))
        else:
            for arg in args:
                apps.append(get_app(arg))

        apps = set(apps)

        for app in apps:
            if verbose:
                print '.'.join(app.__name__.split('.')[:-1]),

            create_permissions(app, get_models(), options.get('verbosity', 0))

            if verbose:
                print ' [OK]'