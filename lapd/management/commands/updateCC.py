import csv
import os
from django.core.management.base import BaseCommand
from lapd.models import CrimesCodes  # Update this import based on your actual app name and model

class Command(BaseCommand):
    help = 'Update CrimesCodes descriptions from a CSV file'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(os.path.dirname(__file__), 'crimecodes.csv')

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                updated_count = 0
                not_found_count = 0

                for row in reader:
                    crime_code = row['Crm Cd'].strip()
                    description = row['Crm Cd Desc'].strip()

                    try:
                        crime_entry = CrimesCodes.objects.get(crime_code=crime_code)
                        crime_entry.description = description
                        crime_entry.save()
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Updated Crime Code {crime_code} with description '{description}'"))
                    except CrimesCodes.DoesNotExist:
                        not_found_count += 1
                        self.stdout.write(self.style.WARNING(f"Crime Code {crime_code} not found in the database."))

                self.stdout.write(self.style.SUCCESS(f"Update completed. {updated_count} entries updated, {not_found_count} entries not found."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
