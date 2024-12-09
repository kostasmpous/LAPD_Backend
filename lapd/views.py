from django.contrib import messages
from django.db import connection
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Max

from lapd.forms import CrimeReportFilterForm, CaseForm, VictimFormSet, CasesCrimeCodesFormSet, CasesWeaponsFormSet
from lapd.models import CrimesCodes, Areas, Victims, CasesCrimeCodes, Cases


@login_required(login_url='login')
def home_page_view(request,*args,**kwargs):
    my_title = "LAPD Crime Database"
    my_context = {
        "page_title": my_title,
    }
    html_template = "LandingPage.html"
    return render(request,html_template,my_context)

VALID_CODE= "abc123"
def pw_protected_view(request,*args,**kwargs):
    is_allowed = False
    if request.method == "POST":
        user_pw_sent = request.POST.get("code") or None
        if user_pw_sent == VALID_CODE:
            is_allowed = True
    if is_allowed:
        return render(request,"protected/view.html",{})
    return render(request,"protected/entry.html",{})

from django.db import connection
from django.shortcuts import render

def search_crime(request):
    area_name = request.GET.get('area_name','')
    area_names = Areas.objects.values_list('area_name', flat=True).distinct()

    table_headers=[]
    table_data=[]

    query = """
    SELECT date_rptd,dr_no,location,time_occ,"Date_Occ",premis_cd,"Status_Code"
    FROM "Cases" JOIN public."Areas" A on "Cases"."Area_code" = A."Area_Code"
    WHERE A."Area_Name" = %s
    """
    table_headers = ['Date Reported', 'DR_NO', 'Location','Time Occurred','Date Occurred','Premise Code','Status Code']
    with connection.cursor() as cursor:
        cursor.execute(query, [area_name])
        table_data = cursor.fetchall()
    return render(request, 'SearchCrime.html', {
        'table_headers': table_headers,
        'table_data': table_data,
        "area_names": area_names
    })


def create_case(request):
    if request.method == 'POST':
        case_form = CaseForm(request.POST)
        victim_formset = VictimFormSet(request.POST)
        crime_formset = CasesCrimeCodesFormSet(request.POST, queryset=CasesCrimeCodes.objects.none())
        weapon_formset = CasesWeaponsFormSet(request.POST, queryset=Cases.weapons.through.objects.none())

        if case_form.is_valid() and victim_formset.is_valid() and crime_formset.is_valid() and weapon_formset.is_valid():
            # Save the case
            case = case_form.save()
            mo_codes = case_form.cleaned_data['mo_codes']
            case.mocodes.set(mo_codes)
            # Save the victims and associate them with the case
            victims = victim_formset.save(commit=False)
            for victim in victims:
                if not victim.victim_id:
                    # Assign the next available victim_id
                    last_victim = Victims.objects.order_by('-victim_id').first()
                    next_victim_id = (last_victim.victim_id + 1) if last_victim else 1
                    victim.victim_id = next_victim_id

                victim.save()
                case.victims.add(victim)

            # Save the crime codes with levels and associate them with the case
            crimes = crime_formset.save(commit=False)
            for crime in crimes:
                if crime.CrimeLevel is not None:
                    crime.DR_NO = case
                    crime.save()
                else:
                    print("discard crime code")
            # Save the weapons and associate them with the case
            weapons = weapon_formset.save(commit=False)
            for weapon in weapons:
                weapon.cases = case
                weapon.save()

            messages.success(request, 'Case created successfully!')

            return redirect('case_list')  # Redirect to a success page or list view
    else:
        case_form = CaseForm()
        victim_formset = VictimFormSet(queryset=Victims.objects.none())
        crime_formset = CasesCrimeCodesFormSet(queryset=CasesCrimeCodes.objects.none())
        weapon_formset = CasesWeaponsFormSet(queryset=Cases.weapons.through.objects.none())

    return render(request, 'NewCase.html', {
        'case_form': case_form,
        'victim_formset': victim_formset,
        'crime_formset': crime_formset,
        'weapon_formset': weapon_formset,
    })


def crime_database_view(request):
    query_type = request.GET.get('query_type', 'crime_report')
    start_date = request.GET.get('start_date', '2020-01-01')
    end_date = request.GET.get('end_date', '2020-04-12')
    crm_cd = request.GET.get('crm_cd','')
    crm_cd2 = request.GET.get('crm_cd2','')
    crm_cd3 = request.GET.get('crm_cd3','')
    crime_desc = CrimesCodes.objects.values_list('description', flat=True).distinct()
    crime_codes = CrimesCodes.objects.values_list('crime_code', flat=True).distinct()
    start_time = request.GET.get('start_time', '00:00:00')
    end_time = request.GET.get('end_time', '00:00:00')
    lat_min = request.GET.get('lat_min')
    lat_max = request.GET.get('lat_max')
    lng_min = request.GET.get('lng_min')
    lng_max = request.GET.get('lng_max')
    n = request.GET.get('n_times')

    table_headers = []
    table_data = []

    if query_type == 'total_reports_per_crmcd':
        query = """
        SELECT "CrimeCode_id", COUNT("DR_NO_id") AS Total_Reports
        FROM "Cases"
        JOIN public."Cases_Crime_Codes" CCC
            ON "Cases".dr_no = CCC."DR_NO_id"
        WHERE "Date_Occ" <= %s
        AND "Date_Occ" >= %s
        GROUP BY "CrimeCode_id"
        ORDER BY Total_Reports DESC
        """
        table_headers = ['Crime Code', 'Total Reports']
        with connection.cursor() as cursor:
            cursor.execute(query, [end_date, start_date])
            table_data = cursor.fetchall()

    elif query_type == 'total_reports_per_day':
        query = """
        SELECT "date_rptd",count(*) AS Total_Request
	FROM "Cases" JOIN
	    public."Cases_Crime_Codes" CCC on "Cases".dr_no = CCC."DR_NO_id"
	WHERE "CrimeCode_id" = %s AND time_occ BETWEEN  %s AND %s
	GROUP BY "date_rptd"
        """
        table_headers = ['Date Reported', 'Total Requests']
        with connection.cursor() as cursor:
            cursor.execute(query, [crm_cd,start_time, end_time])
            table_data = cursor.fetchall()
    elif query_type == 'most_common_crime_per_area':
        query = """
                WITH CrimeCounts as
            (SELECT "Area_Name","CrimeCode_id",count("CrimeCode_id") AS Occurence
            FROM "Cases" JOIN public."Areas" A on "Cases"."Area_code" = A."Area_Code"
                JOIN public."Cases_Crime_Codes" CCC on "Cases".dr_no = CCC."DR_NO_id"
            WHERE "Date_Occ" = %s
            GROUP BY "Area_Name","CrimeCode_id"),
        RankedCrimes as
            (SELECT "Area_Name","CrimeCode_id",Occurence,
                    rank() OVER (PARTITION BY "Area_Name" ORDER BY Occurence DESC) AS CrimeRank
             FROM CrimeCounts)
        SELECT "Area_Name","CrimeCode_id",Occurence
        FROM RankedCrimes
        WHERE CrimeRank = 1
        """
        table_headers = ['Area Name', 'Crime Code','Occurence']
        with connection.cursor() as cursor:
            cursor.execute(query, [start_date])
            table_data = cursor.fetchall()
    # Execute the selected query
    elif query_type == 'average_crimes_per_hour':
        query = """
        SELECT
            extract(HOUR FROM time_occ) AS HourOfTheDay,
            COUNT(*) / (
                SELECT EXTRACT(EPOCH FROM ('2020-10-20'::timestamp - '2020-10-10'::timestamp)) / 3600
            ) AS AvgCrimesPerHour
        FROM
            "Cases"
        WHERE
            Date_Rptd BETWEEN %s AND %s
        GROUP BY
            HourOfTheDay
        ORDER BY
            HourOfTheDay;
            """
        table_headers = ['Hours of Day', 'Average Crimes per Hour']
        with connection.cursor() as cursor:
            cursor.execute(query, [start_date, end_date])
            table_data = cursor.fetchall()
    elif query_type == 'top5_areas_by_crimes_a':
        query = """
        SELECT "Area_Name",COUNT(*) AS TotalCrime
            FROM "Cases" JOIN public."Areas" A on "Cases"."Area_code" = A."Area_Code"
            WHERE "Date_Occ" BETWEEN %s AND %s
            GROUP BY "Area_Name"
            ORDER BY TotalCrime DESC
            LIMIT 5
        """
        table_headers = ['Area Name','Total Crimes']
        with connection.cursor() as cursor:
            cursor.execute(query, [start_date, end_date])
            table_data = cursor.fetchall()
    elif query_type == 'top5_areas_by_crimes_b':
        query = """
            SELECT rpt_dist_no,COUNT(*) AS TotalCrime
                FROM "Cases" JOIN public."Areas" A on "Cases"."Area_code" = A."Area_Code"
                WHERE "Date_Occ" BETWEEN %s AND %s
                GROUP BY rpt_dist_no
                ORDER BY TotalCrime DESC
                LIMIT 5
        """
        table_headers = ['Rpt dist no','Total Crimes']
        with connection.cursor() as cursor:
            cursor.execute(query, [start_date, end_date])
            table_data = cursor.fetchall()
    elif query_type == 'co_occurred_crimes':
        query = """
            WITH CaseCrimeCode AS(
            SELECT *
                FROM "Cases" JOIN public."Cases_Crime_Codes" CCC on "Cases".dr_no = CCC."DR_NO_id" JOIN public."Areas" A ON A."Area_Code" = "Cases"."Area_code" JOIN public."Crimes_Codes" CC on CC."Crime_Code" = CCC."CrimeCode_id"
        ),
        CrimeCodePairs AS(
            SELECT ccc1."CrimeCode_id" AS CrimeCode1,ccc1."Description" AS DescCrime1,ccc2."CrimeCode_id" AS CrimeCode2,ccc2."Description" AS DescCrime2
            FROM CaseCrimeCode ccc1 JOIN CaseCrimeCode ccc2 ON ccc1.date_rptd = ccc2.date_rptd AND ccc1.dr_no <> ccc2.dr_no
            WHERE ccc1."Area_Name" = (
                    SELECT "Area_Name"
                    FROM "Cases" JOIN public."Areas" A on A."Area_Code" = "Cases"."Area_code"
                    WHERE "date_rptd" BETWEEN %s AND %s
                    GROUP BY "Area_Name"
                    ORDER BY count(*) DESC
                    LIMIT 1
            )
            AND ccc1.date_rptd between %s AND %s
        )
        SELECT CrimeCode1,DescCrime1,CrimeCode2,DescCrime2, count(*) AS CountPair
        FROM CrimeCodePairs
        GROUP BY CrimeCode1,CrimeCode2,DescCrime1,DescCrime2
        ORDER BY CountPair DESC
        LIMIT 1
        """
        table_headers = ['Crime Code 1','Description CC 1','Crime Code 2','Description CC 2','Count']
        with connection.cursor() as cursor:
            cursor.execute(query, [start_date, end_date, start_date, end_date])
            table_data = cursor.fetchall()
    elif query_type == 'second_most_common_cooccurred_crime':
        query = """
        WITH CaseCrimeCode AS(
                SELECT *
                    FROM "Cases" JOIN public."Cases_Crime_Codes" CCC on "Cases".dr_no = CCC."DR_NO_id" JOIN public."Areas" A ON A."Area_Code" = "Cases"."Area_code" JOIN public."Crimes_Codes" CC on CC."Crime_Code" = CCC."CrimeCode_id"
            ),
            CrimeCodePairs AS(
                SELECT ccc1."CrimeCode_id" AS CrimeCode1,ccc1."Description" AS DescCrime1,ccc2."CrimeCode_id" AS CrimeCode2,ccc2."Description" AS DescCrime2
                FROM CaseCrimeCode ccc1 JOIN CaseCrimeCode ccc2 ON ccc1.date_rptd = ccc2.date_rptd AND ccc1.dr_no <> ccc2.dr_no
                WHERE ccc1."CrimeCode_id" = %s
                AND ccc1.date_rptd between %s AND %s
            )
            SELECT CrimeCode2 AS CrimeCode,DescCrime2 AS Description
            FROM CrimeCodePairs
            WHERE CrimeCode2 <> %s
            GROUP BY CrimeCode2,DescCrime2
            ORDER BY count(*) DESC
            LIMIT 1 OFFSET 1
        """
        table_headers = ['Crime Code','Description']
        with connection.cursor() as cursor:
            cursor.execute(query, [crm_cd,start_date, end_date,crm_cd])
            table_data = cursor.fetchall()

    elif query_type == 'common_weapon_by_age_group':
        query = """
        WITH AgeGroups AS(
        SELECT "Victims"."Victim_Id" AS VictimID,
                CASE WHEN "Victims"."Age">= 0 AND "Victims"."Age"<5 THEN '0-4'
                WHEN "Victims"."Age">=5 AND "Victims"."Age"< 10 THEN '5-9'
                WHEN "Victims"."Age" >= 10 AND "Victims"."Age"<15 THEN '10-14'
                WHEN "Victims"."Age">=15 AND "Victims"."Age"<20 THEN '15-19'
                WHEN "Victims"."Age">=20 AND "Victims"."Age"<25 THEN '20-24'
                WHEN "Victims"."Age">=25 AND "Victims"."Age"<30 THEN '25-29'
                WHEN "Victims"."Age">=30 AND "Victims"."Age"<35 THEN '30-34'
                WHEN "Victims"."Age">=35 AND "Victims"."Age"<40 THEN '35-39'
                WHEN "Victims"."Age">=40 AND "Victims"."Age"<45 THEN '40-44'
                WHEN "Victims"."Age">=45 AND "Victims"."Age"<50 THEN '45-49'
                WHEN "Victims"."Age">=50 AND "Victims"."Age"<55 THEN '50-54'
                WHEN "Victims"."Age">=55 AND "Victims"."Age"<60 THEN '55-59'
                WHEN "Victims"."Age">=60 AND "Victims"."Age"<65 THEN '60-64'
                WHEN "Victims"."Age">=65 AND "Victims"."Age"<70 THEN '65-69'
                WHEN "Victims"."Age">=70 AND "Victims"."Age"<75 THEN '70-74'
                WHEN "Victims"."Age">=75 AND "Victims"."Age"<80 THEN '75-79'
                WHEN "Victims"."Age">=80 AND "Victims"."Age"<85 THEN '80-84'
                WHEN "Victims"."Age">=85 AND "Victims"."Age"<90 THEN '85-89'
                WHEN "Victims"."Age">=90 AND "Victims"."Age"<95 THEN '90-94'
                WHEN "Victims"."Age">=95 AND "Victims"."Age"<100 THEN '95-99'
            ELSE '>=100'
            END AS AgeGroup
            FROM "Victims"),
        WeaponUsage AS(
            SELECT ag.AgeGroup,w.weapon_description,count(*) AS WeaponCount
            FROM "Cases_victims" cv JOIN "Cases" ON cv.cases_id = "Cases".dr_no
            JOIN "Cases_weapons" cw ON "Cases".dr_no = cw.cases_id
            JOIN "Weapons" w ON cw.weapons_id = w.weapon_cd
            JOIN AgeGroups ag ON cv.victims_id = ag.VictimID
            GROUP BY ag.AgeGroup,w.weapon_description
            )
            SELECT AgeGroup,weapon_description
            FROM WeaponUsage
            WHERE (AgeGroup,WeaponCount) IN (
                SELECT AgeGroup, MAX(WeaponCount)
                FROM WeaponUsage
                GROUP BY AgeGroup
            )
            ORDER BY AgeGroup ASC;
        """
        table_headers = ['Age Group','Weapon Description']
        with connection.cursor() as cursor:
            cursor.execute(query)
            table_data = cursor.fetchall()
    elif query_type == 'longest_time_without_crime':
        query = """
                   WITH TimeGaps AS (
          SELECT
            a."Area_Name" AS AreaName,
            c."Date_Occ",
            LAG(c."Date_Occ") OVER (PARTITION BY a."Area_Name" ORDER BY c."Date_Occ") AS PreviousDate,
            c."Date_Occ" - LAG(c."Date_Occ") OVER (PARTITION BY a."Area_Name" ORDER BY c."Date_Occ") AS TimeDifference
          FROM "Cases" c
          JOIN "Areas" a ON c."Area_code" = a."Area_Code"
          JOIN public."Cases_Crime_Codes" CCC on c.dr_no = CCC."DR_NO_id"
          WHERE CCC."CrimeCode_id" = %s -- Replace with the target crime code
        ), MaxGaps AS (
          SELECT
            AreaName,
            MAX(TimeDifference) as MaxTimeDifference
          FROM TimeGaps
          GROUP BY AreaName
        )
        SELECT
          mg.AreaName,
          mg.MaxTimeDifference,
          tg.PreviousDate AS StartDate,
          tg."Date_Occ" AS EndDate
          
        FROM MaxGaps mg
        JOIN TimeGaps tg ON mg.AreaName = tg.AreaName AND mg.MaxTimeDifference = tg.TimeDifference
        ORDER BY mg.MaxTimeDifference DESC
        LIMIT 1;
        """
        table_headers = ['Area_Name','Max Timed Difference','Start Date','End Date']
        with connection.cursor() as cursor:
            cursor.execute(query, [crm_cd])
            table_data = cursor.fetchall()
    elif query_type == 'areas_with_two_crimes':
        query = """
           WITH Crime1 AS(
            SELECT "Area_Name","date_rptd",count(*)
            FROM "Cases" JOIN public."Areas" A on A."Area_Code" = "Cases"."Area_code"
            JOIN public."Cases_Crime_Codes" CCC on "Cases".dr_no = CCC."DR_NO_id"
            JOIN public."Crimes_Codes" CC on CCC."CrimeCode_id" = CC."Crime_Code"
            WHERE "Description" = %s
            GROUP BY "Area_Name",date_rptd
            HAVING COUNT(*)>1
        ),
        Crime2 AS(
            SELECT "Area_Name","date_rptd"
            FROM "Cases" JOIN public."Areas" A on A."Area_Code" = "Cases"."Area_code"
            JOIN public."Cases_Crime_Codes" CCC on "Cases".dr_no = CCC."DR_NO_id"
            JOIN public."Crimes_Codes" CC on CCC."CrimeCode_id" = CC."Crime_Code"
            WHERE "Description" = %s
            GROUP BY "Area_Name",date_rptd
            HAVING COUNT(*)>1
        )
        SELECT DISTINCT Crime1."Area_Name"
        FROM Crime1 JOIN Crime2 ON Crime1.date_rptd = Crime2.date_rptd 
        AND Crime1."Area_Name" = Crime2."Area_Name"
        """
        table_headers = ['Area_Name']
        with connection.cursor() as cursor:
            cursor.execute(query, [crm_cd2,crm_cd3])
            table_data = cursor.fetchall()
    elif query_type == 'divisions_with_same_weapon':
        query = """
         WITH TotalRecords AS(
            SELECT *
            FROM "Cases" c JOIN public."Areas" A
            ON A."Area_Code" = c."Area_code"
            JOIN public."Cases_weapons" Cw
            ON c.dr_no = Cw.cases_id
        )
        SELECT DISTINCT t1.dr_no
        FROM TotalRecords t1
        JOIN TotalRecords t2 ON t1.weapons_id = t2.weapons_id
        AND t1.date_rptd = t2.date_rptd
        AND t1."Area_code" <> t2."Area_code"
        WHERE t1.time_occ BETWEEN %s AND %s
        """
        table_headers = ['dr_no']
        with connection.cursor() as cursor:
            cursor.execute(query, [start_time,end_time])
            table_data = cursor.fetchall()
    elif query_type == 'crimes_occurred_n_times':
        query ="""
            SELECT
          dr_no,
          "Area_Name",
          "Description",
          weapon_description
        FROM
          "Cases" JOIN "Areas" ON "Cases"."Area_code" = "Areas"."Area_Code"
        JOIN
          "Cases_Crime_Codes" ON "Cases".dr_no = "Cases_Crime_Codes"."DR_NO_id"
        JOIN "Crimes_Codes" ON "Cases_Crime_Codes"."CrimeCode_id" = "Crimes_Codes"."Crime_Code"
        JOIN "Cases_weapons" ON "Cases".dr_no = "Cases_weapons".cases_id
        JOIN
          "Weapons" ON "Cases_weapons".weapons_id = "Weapons".weapon_cd
        WHERE
          "Date_Occ" BETWEEN %s AND %s -- replace with actual date range
        GROUP BY
          dr_no,
          "Area_Name",
          "Description",
          weapon_description
        HAVING
          COUNT(*) = %s
        """
        table_headers = ['dr_no','Area_Name','Description','Weapon']
        with connection.cursor() as cursor:
            cursor.execute(query, [start_date,end_date,n])
            table_data = cursor.fetchall()
    elif query_type == 'common_crmcd_in_bounding_box':
        query = """
                SELECT cc."Crime_Code", COUNT(*) AS crime_count
        FROM "Cases" c
        JOIN "Cases_Crime_Codes" ccc ON c.dr_no = ccc."DR_NO_id"
        JOIN "Crimes_Codes" cc ON ccc."CrimeCode_id" = cc."Crime_Code"
        WHERE
            c."Date_Occ" = %s -- Replace with your specific date
            AND CAST(
                CONCAT(
                    LEFT(REPLACE(c.lat, '.', ''), 2), '.', SUBSTRING(REPLACE(c.lat, '.', ''), 3)
                ) AS FLOAT
            ) BETWEEN %s AND %s -- Correct bounding box for latitude
            AND CAST(
                CONCAT(
                    LEFT(REPLACE(c.long, '.', ''), 4), '.', SUBSTRING(REPLACE(c.long, '.', ''), 5)
                ) AS FLOAT
            ) BETWEEN %s AND %s -- Correct bounding box for longitude
        GROUP BY cc."Crime_Code"
        ORDER BY crime_count DESC
        LIMIT 1

        """
        table_headers=['Crime Code','Crime Count']
        with connection.cursor() as cursor:
            cursor.execute(query, [start_date,lat_min,lat_max,lng_min,lng_max])
            table_data = cursor.fetchall()

    return render(request, 'Base.html', {
        'table_headers': table_headers,
        'table_data': table_data,
        'query_type': query_type,
        'start_date': start_date,
        'end_date': end_date,
        'crime_codes' : crime_codes,
        'crime_desc' : crime_desc,
        'start_time': start_time,
        'end_time': end_time
    })
