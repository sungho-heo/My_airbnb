from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):

    """ Command to Definition """

    help = "This command auto create users "

    def handle(self, *args, **options):
        admin = User.objects.get_or_none(username="ebadmin")
        if not admin:
            User.objects.create_superuser("ebadmin", "hurgj123kr@daum.net", "153123")
            self.stdout.write(self.style.SUCCESS(f"Superuser Created"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser Exists"))


