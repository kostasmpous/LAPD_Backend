# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import uuid

from django.db import models



class Areas(models.Model):
    area_code = models.SmallIntegerField(db_column='Area_Code', primary_key=True)  # Field name made lowercase.
    area_name = models.CharField(db_column='Area_Name', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        
        db_table = 'Areas'



class CaseStatus(models.Model):
    status_code = models.CharField(db_column='Status_code', primary_key=True, max_length=4)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Case_Status'

class CrimesCodes(models.Model):
    crime_code = models.CharField(db_column='Crime_Code', primary_key=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Crimes_Codes'


class MoCodes(models.Model):
    mo_code = models.CharField(db_column='MO_Code', primary_key=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        
        db_table = 'MO_Codes'


class Premises(models.Model):
    premis_cd = models.SmallIntegerField(db_column='Premis_Cd', primary_key=True)  # Field name made lowercase.
    premis_desc = models.CharField(db_column='Premis_Desc', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        
        db_table = 'Premises'


class VictimDescent(models.Model):
    descent_code = models.CharField(db_column='Descent_Code', primary_key=True)  # Field name made lowercase. This field type is a guess.
    description = models.CharField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        
        db_table = 'Victim Descent'


class Victims(models.Model):
    age = models.SmallIntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    victim_id = models.IntegerField(db_column='Victim_Id', primary_key=True,db_index=True)  # Field name made lowercase.
    descent_code = models.ForeignKey(VictimDescent, models.DO_NOTHING, db_column='Descent_code', blank=True, null=True)  # Field name made lowercase.
    sex = models.CharField(db_column='Sex', blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        
        db_table = 'Victims'



class Weapons(models.Model):
    weapon_cd = models.CharField(primary_key=True, max_length=4)
    weapon_description = models.CharField(blank=True, null=True)

    class Meta:
        
        db_table = 'Weapons'

class Cases(models.Model):
    date_rptd = models.DateField()
    premis_cd = models.ForeignKey('Premises', models.DO_NOTHING, db_column='premis_cd')
    rpt_dist_no = models.CharField(max_length=4, blank=True, null=True)
    dr_no = models.CharField(primary_key=True, max_length=9)
    location = models.CharField(max_length=45, blank=True, null=True)
    time_occ = models.TimeField(blank=True, null=True)
    status_code = models.ForeignKey(CaseStatus, models.DO_NOTHING, db_column='Status_Code', blank=True, null=True)  # Field name made lowercase.
    date_occ = models.DateField(db_column='Date_Occ', blank=True, null=True)  # Field name made lowercase.
    cross_street = models.CharField(db_column='Cross Street', max_length=45, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    lat = models.CharField(db_column='lat', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    long = models.CharField(db_column='long', blank=True, null=True)
    area_code = models.ForeignKey(Areas, models.DO_NOTHING, db_column='Area_code', blank=True, null=True)  # Field name made lowercase.
    victims = models.ManyToManyField(Victims)
    weapons = models.ManyToManyField(Weapons)
    mocodes = models.ManyToManyField(MoCodes,through = "CasesMoCodes")
    crimecodes = models.ManyToManyField(CrimesCodes,through="CasesCrimeCodes")
    class Meta:
        db_table = 'Cases'

class CasesMoCodes(models.Model):
    MOCode = models.ForeignKey(MoCodes, on_delete=models.CASCADE)
    DR_NO = models.ForeignKey(Cases, on_delete=models.CASCADE)
    class Meta:
        db_table = 'Cases_Mo_Codes'
        unique_together = ('MOCode', 'DR_NO')

class CasesCrimeCodes(models.Model):
    DR_NO = models.ForeignKey(Cases, on_delete=models.CASCADE)
    CrimeCode = models.ForeignKey(CrimesCodes,on_delete=models.CASCADE)
    CrimeLevel = models.IntegerField()
    class Meta:
        db_table = 'Cases_Crime_Codes'
        unique_together = ('CrimeCode', 'DR_NO')

