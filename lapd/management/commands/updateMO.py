import csv
from django.core.management.base import BaseCommand
from lapd.models import MoCodes
import os
class Command(BaseCommand):
    help = 'Update MoCodes descriptions from a CSV file'

    def handle(self, *args, **options):


        csv_file_path = os.path.join(os.path.dirname(__file__), 'mocodes.csv')
        # Replace with the actual path to your CSV file

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                updated_count = 0
                not_found_count = 0

                for row in reader:
                    mocode = row['MO CODES'].strip()
                    description = row['desc'].strip()

                    try:
                        mo_code_entry = MoCodes.objects.get(mo_code=mocode)
                        mo_code_entry.description = description
                        mo_code_entry.save()
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Updated MO Code {mocode} with description '{description}'"))
                    except MoCodes.DoesNotExist:
                        not_found_count += 1
                        self.stdout.write(self.style.WARNING(f"MO Code {mocode} not found in the database."))

                self.stdout.write(self.style.SUCCESS(f"Update completed. {updated_count} entries updated, {not_found_count} entries not found."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
