from django.contrib.auth.models import User
from urllib3 import request

from lapd.models import *
import pandas as pd
import numpy as np
from datetime import date,time

def extract_MO_Codes():
    csv_file_path = 'scripts/mocodes.csv'
    df = pd.read_csv(csv_file_path)
    mocodes =[]
    for index, row in df.iterrows():
        # Create or get the Category instance
        mc = MoCodes(
            mo_code=row['MO CODES'],
            description=str(row['NUMERICAL'])
        )
        if(mc in mocodes):
            continue
        mocodes.append(mc)
    MoCodes.objects.bulk_create(mocodes,batch_size=100)

def extract_Descent_Codes():
    csv_file_path = 'scripts/descentcodes.csv'
    df = pd.read_csv(csv_file_path)
    vds =[]
    for index, row in df.iterrows():
        # Create or get the Category instance
        vd = VictimDescent(
            descent_code=row['Descent Code'],
            description=row['Description']
        )
        if(vd in vds):
            continue
        vds.append(vd)
    VictimDescent.objects.bulk_create(vds,batch_size=100)

def extract_Areas():
    csv_file_path = 'scripts/areanames.csv'
    df = pd.read_csv(csv_file_path)
    areas = []
    for index, row in df.iterrows():
        # Create or get the Category instance
        area = Areas(
            area_code=row['AREA CODE'],
            area_name=row['AREA NAME']
        )
        if (area in areas):
            continue
        areas.append(area)
    Areas.objects.bulk_create(areas, batch_size=100)

def add_weapons(row,listWeapons):
    flag = False
    if not np.isnan(row['Weapon Used Cd']):
        flag = True
        my_str = str(row['Weapon Used Cd'])[:-2]
        weapon = Weapons(
            weapon_cd=my_str,
            weapon_description=row['Weapon Desc']
        )

        if weapon not in listWeapons:
            listWeapons.append(weapon)

    if flag:
        return [weapon,listWeapons]
    return 0,listWeapons

def add_case_statuses(row,listCaseStatuses):
    #if not np.isnan(row['Status']):
        status = CaseStatus(
            status_code=row['Status'],
            description=row['Status Desc']
        )
        if status not in listCaseStatuses:
            listCaseStatuses.append(status)
        return status,listCaseStatuses

def add_premises(row,listPremises):
    if not pd.isnull(row['Premis Cd']):
        premise = Premises(
            premis_cd=row['Premis Cd'],
            premis_desc=row['Premis Desc']
        )
        if premise not in listPremises:
            listPremises.append(premise)
        return premise,listPremises
    return 0,listPremises


def add_Victims(row, listOfVictims,vic_id,dict):
    flag = False
    if isinstance(row['Vict Sex'],str) and isinstance(row['Vict Descent'],str):
        flag = True
        victim = Victims(
            age = int(row['Vict Age']),
            descent_code = dict.get(str(row['Vict Descent'])),
            sex = row['Vict Sex'],
            id = vic_id
        )

        if victim not in listOfVictims:
            listOfVictims.append(victim)
    if flag:
        return [victim,listOfVictims]
    return 0,listOfVictims


def getDicDescentCodes():
    table = VictimDescent.objects.all()
    dict ={}
    for row in table:
        dict[row.descent_code] = row
    return dict


def getDictAreas():
    table = Areas.objects.all()
    dict = {}
    for row in table:
        dict[row.area_code] = row
    return dict


def getMODict():
    table = MoCodes.objects.all()
    dict = {}
    for row in table:
        dict[row.mo_code] = row
    return dict

def fixDateFormat(date1):
    date1 = date1.split(' ')
    date1 = date1[0].split('/')
    date1 = date(int(date1[2]),int(date1[0]),int(date1[1]))
    return date1

def fixTimeFormat(time1):
    time1 = list(time1)
    if len(time1) != 4:
        zeros = 4-len(time1)
        for i in range(zeros):
            time1.insert(0,'0')
    hour = time1[0] + time1[1]
    minute = time1[2] + time1[3]
    return time(int(hour), int(minute))


def extract_Statuses():
    csv_file_path = 'scripts/casestatus.csv'
    df = pd.read_csv(csv_file_path)
    statuses = []
    for index, row in df.iterrows():
        # Create or get the Category instance
        status = CaseStatus(
            status_code=row['StatusCode'],
            description=row['Description']
        )
        if (status in statuses):
            continue
        statuses.append(status)
    CaseStatus.objects.bulk_create(statuses, batch_size=100)


def extract_CrimeCodes():
    csv_file_path = 'scripts/crimecodes.csv'
    df = pd.read_csv(csv_file_path)
    cds = []
    for index, row in df.iterrows():
        # Create or get the Category instance
        cd = CrimesCodes(
            crime_code=row['Crm Cd'],
            description=row['Crm Cd Desc']
        )
        if (cd in cds):
            continue
        cds.append(cd)
    CrimesCodes.objects.bulk_create(cds, batch_size=100)


def getCMDict():
    table = CrimesCodes.objects.all()
    dict = {}
    for row in table:
        dict[row.crime_code] = row
    return dict


def run():
    # Read CSV file into a DataFrame
    csv_file_path = 'scripts/crime_data.csv'
    df = pd.read_csv(csv_file_path)
    vic_id = 32391
    #extract data from other sources
    #extract_MO_Codes()
    #extract_Descent_Codes()
    #extract_Areas()
    #extract_Statuses()
    #extract_CrimeCodes()
    #initialize lists for extract data from csv
    listWeapons = []
    listCaseStatus = []
    listPremises = []
    listOfVictims =[]
    listCases =[]
    i=0
    dictDC = getDicDescentCodes()
    dictAreas = getDictAreas()
    dictMO = getMODict()
    dictCrimeCodes = getCMDict()
    # Iterate through the DataFrame and create model instances
    for index, row in df.iterrows():

            weapon,listWeapons = add_weapons(row,listWeapons)
            status,listCaseStatus = add_case_statuses(row,listCaseStatus)
            premis,listPremises = add_premises(row,listPremises)
            victim,listOfVictims = add_Victims(row,listOfVictims,vic_id,dictDC)
            vic_id += 1
            i=i+1
            listCrimes = []

            if premis != 0:
                premis.save()
            status.save()
            case = Cases(
                date_rptd = fixDateFormat(str(row['Date Rptd'])),
                premis_cd = premis if premis != 0 else None,
                rpt_dist_no = row['Rpt Dist No'],
                dr_no = row['DR_NO'],
                location = row['LOCATION'],
                time_occ = fixTimeFormat(str(row['TIME OCC'])),
                status_code = status,
                date_occ=fixDateFormat(str(row['DATE OCC'])),
                cross_street = row['Cross Street'] if not pd.isnull(row['Cross Street']) else '-',
                coordinates=str(row['LAT']) +','+ str(row['LON']),
                area_code = dictAreas.get(row['AREA']),
            )
            case.save()
            if victim!=0:
                victim.save()
                case.victims.add(victim)
            if weapon!=0:
                weapon.save()
                case.weapons.add(weapon)
            if not pd.isnull(row['Mocodes']):
                mocodes_row = str(row['Mocodes']).split(' ')
                if mocodes_row and not pd.isnull(mocodes_row).any():
                    for mocode in mocodes_row:
                        if mocode in dictMO:
                            CasesMoCodes.objects.create(
                                MOCode=dictMO.get(str(int(mocode))),
                                DR_NO=case
                            )
            CasesCrimeCodes.objects.create(
                DR_NO=case,
                CrimeCode=dictCrimeCodes.get(row['Crm Cd']),
                CrimeLevel=1
            )
            if not pd.isnull(row['Crm Cd 2']):
                if dictCrimeCodes.get(row['Crm Cd 2']):
                    CasesCrimeCodes.objects.create(
                        DR_NO = case,
                        CrimeCode=dictCrimeCodes.get(row['Crm Cd 2']),
                        CrimeLevel=2
                    )
                else:
                    cc = CrimesCodes(
                        crime_code = row['Crm Cd 2'],
                        description = '-'
                    )
                    cc.save()
                    CasesCrimeCodes.objects.create(
                        DR_NO=case,
                        CrimeCode=cc,
                        CrimeLevel=2
                    )
                if not pd.isnull(row['Crm Cd 3']):
                    if dictCrimeCodes.get(row['Crm Cd 3']):
                        CasesCrimeCodes.objects.create(
                            DR_NO=case,
                            CrimeCode=dictCrimeCodes.get(row['Crm Cd 3']),
                            CrimeLevel=3
                        )
                    else:
                        cc = CrimesCodes(
                            crime_code=row['Crm Cd 3'],
                            description='-'
                        )
                        cc.save()
                        CasesCrimeCodes.objects.create(
                            DR_NO=case,
                            CrimeCode=cc,
                            CrimeLevel=3
                        )
                    if not pd.isnull(row['Crm Cd 4']):
                        if dictCrimeCodes.get(row['Crm Cd 4']):
                            CasesCrimeCodes.objects.create(
                                DR_NO=case,
                                CrimeCode=dictCrimeCodes.get(row['Crm Cd 4']),
                                CrimeLevel=4
                            )
                        else:
                            cc = CrimesCodes(
                                crime_code=row['Crm Cd 4'],
                                description='-'
                            )
                            cc.save()
                            CasesCrimeCodes.objects.create(
                                DR_NO=case,
                                CrimeCode=cc,
                                CrimeLevel=4
                            )
    #Victims.objects.bulk_create(listOfVictims,batch_size=100)
    #Weapons.objects.bulk_create(listWeapons, batch_size=100)
    #CaseStatus.objects.bulk_create(listCaseStatus, batch_size=100)
    #Premises.objects.bulk_create(listPremises, batch_size=100)