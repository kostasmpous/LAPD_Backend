from lapd.models import *
import pandas as pd
import numpy as np

def run():
    # Read CSV file into a DataFrame
    csv_file_path = 'scripts/crime_data.csv'
    df = pd.read_csv(csv_file_path)
    i=0
    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():
        # Create or get the Category instance
        if not np.isnan(row['Weapon Used Cd']) :
            my_str = str(row['Weapon Used Cd'])[:-2]
            i=i+1
            weapon = Weapons.objects.get_or_create(
                weapon_cd=my_str,
                weapon_description=row['Weapon Desc']
            )
            if i==5:
                break

