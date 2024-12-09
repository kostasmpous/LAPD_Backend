import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from lapd.models import Cases, Areas, CaseStatus, CrimesCodes, MoCodes, Premises, Victims, Weapons, CasesMoCodes, \
    CasesCrimeCodes, VictimDescent


class Command(BaseCommand):
    help = 'Import cases from a CSV file'

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, 'crime_data.csv')
        batch_size = 1000  # Adjust batch size based on your system's capacity

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            cases_to_create = []
            cases_mo_codes_to_create = []
            cases_crime_codes_to_create = []

            for idx, row in enumerate(reader):
                try:
                    # 1. Create or get related objects
                    area, _ = Areas.objects.get_or_create(
                        area_code=int(row['AREA']),
                        area_name=row['AREA NAME']
                    )

                    premise, _ = Premises.objects.get_or_create(
                        premis_cd=int(row['Premis Cd']),
                        premis_desc=row['Premis Desc']
                    )

                    status, _ = CaseStatus.objects.get_or_create(
                        status_code=row['Status'],
                        description=row['Status Desc']
                    )

                    weapon, _ = Weapons.objects.get_or_create(
                        weapon_cd=row['Weapon Used Cd'],
                        weapon_description=row['Weapon Desc']
                    )

                    # Fetch or create the VictimDescent instance
                    descent_code_str = row['Vict Descent']
                    descent_code_obj, _ = VictimDescent.objects.get_or_create(
                        descent_code=descent_code_str
                    )

                    # Create or get the Victims instance
                    victim, _ = Victims.objects.get_or_create(
                        victim_id=idx + 1,  # Simple unique ID (consider a better unique identifier)
                        age=int(row['Vict Age']) if row['Vict Age'] else None,
                        descent_code=descent_code_obj,  # Assign the VictimDescent instance
                        sex=row['Vict Sex']
                    )

                    # 2. Parse dates and times
                    date_rptd = datetime.strptime(row['Date Rptd'], '%m/%d/%Y').date()
                    date_occ = datetime.strptime(row['DATE OCC'], '%m/%d/%Y').date()
                    time_occ = datetime.strptime(row['TIME OCC'], '%H%M').time()

                    # 3. Create the Case instance
                    case = Cases(
                        dr_no=row['DR_NO'],
                        date_rptd=date_rptd,
                        date_occ=date_occ,
                        time_occ=time_occ,
                        premis_cd=premise,
                        status_code=status,
                        area_code=area,
                        rpt_dist_no=row['Rpt Dist No'],
                        location=row['LOCATION'],
                        cross_street=row['Cross Street'],
                        lat=row['LAT'],
                        long=row['LON']
                    )
                    cases_to_create.append(case)

                    # 4. Prepare Many-to-Many relationships for MoCodes
                    mo_codes_str = row['Mocodes']
                    mo_codes = mo_codes_str.split()  # Split by spaces to get individual MO Codes
                    for mo_code in mo_codes:
                        mo_code_obj, _ = MoCodes.objects.get_or_create(mo_code=mo_code)
                        cases_mo_codes_to_create.append(CasesMoCodes(MOCode=mo_code_obj, DR_NO=case))

                    # 5. Prepare Many-to-Many relationships for CrimesCodes
                    crime_codes = [row['Crm Cd 1'], row['Crm Cd 2'], row['Crm Cd 3'], row['Crm Cd 4']]
                    for crime_code in filter(None, crime_codes):
                        crime_code_obj, _ = CrimesCodes.objects.get_or_create(crime_code=crime_code)
                        cases_crime_codes_to_create.append(
                            CasesCrimeCodes(CrimeCode=crime_code_obj, DR_NO=case, CrimeLevel=1))

                    # Bulk insert every batch_size rows
                    if len(cases_to_create) >= batch_size:
                        Cases.objects.bulk_create(cases_to_create)
                        CasesMoCodes.objects.bulk_create(cases_mo_codes_to_create)
                        CasesCrimeCodes.objects.bulk_create(cases_crime_codes_to_create)
                        self.stdout.write(f'Inserted {idx + 1} rows')

                        cases_to_create = []
                        cases_mo_codes_to_create = []
                        cases_crime_codes_to_create = []


                except Exception as e:

                    self.stderr.write(f'Error at row {idx + 1}: {e}')

                    self.stderr.write(f'Problematic row: {row}')

                    break  # Stop the loop to debug the issue

            # Insert any remaining rows
            if cases_to_create:
                Cases.objects.bulk_create(cases_to_create)
                CasesMoCodes.objects.bulk_create(cases_mo_codes_to_create)
                CasesCrimeCodes.objects.bulk_create(cases_crime_codes_to_create)
                self.stdout.write('Final batch inserted')

        self.stdout.write(self.style.SUCCESS('CSV data imported successfully'))