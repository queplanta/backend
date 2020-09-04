import csv
from django.core.management.base import BaseCommand, CommandError
from accounts.models import User

class Command(BaseCommand):
    help = 'Export contacts to CSV sendgrid'

    def handle(self, *args, **options):
        w = csv.writer(self.stdout)

        w.writerow(["email", "first_name", "last_name", "address_line_1", "address_line_2", "city", "state_province_region", "postal_code", "country"])
        for user in User.objects.all():
            if user.email:
                w.writerow([user.email, user.first_name, user.last_name, "", "", "", "", "", ""])
