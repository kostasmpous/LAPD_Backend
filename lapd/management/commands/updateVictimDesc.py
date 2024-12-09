import csv
import os
from django.core.management.base import BaseCommand
from lapd.models import VictimDescent  # Update the import based on your actual app name and model

class Command(BaseCommand):
    help = 'Update VictimDescent descriptions from a CSV file'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(os.path.dirname(__file__), 'victim_desc.csv')

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                updated_count = 0
                not_found_count = 0

                for row in reader:
                    descent_code = row['Descent Code'].strip()
                    description = row['Description'].strip()

                    try:
                        descent_entry = VictimDescent.objects.get(descent_code=descent_code)
                        descent_entry.description = description
                        descent_entry.save()
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Updated Descent Code {descent_code} with description '{description}'"))
                    except VictimDescent.DoesNotExist:
                        not_found_count += 1
                        self.stdout.write(self.style.WARNING(f"Descent Code {descent_code} not found in the database."))

                self.stdout.write(self.style.SUCCESS(f"Update completed. {updated_count} entries updated, {not_found_count} entries not found."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
