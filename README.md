# 🚔 LAPD Crime Database Project

This Project was made for the M134 - Database Management Systems programming assigment 1, during the Fall semester 2024.
Welcome to the LAPD Crime Database project! This web application is designed to manage and analyze crime reports for the LAPD.
It provides functionalities to create, search crime data efficiently. 
The application is built using Django and leverages TailwindCSS for modern UI styling.

## 📋Table of Contents
* Features
* Technologies Used
* Installation
* Database Models

##  ✨Features
* Create Crime Reports: Add new crime cases with associated victims, crime codes, weapons, and MO codes.
* Search Crimes: Search and filter crime data by various parameters (date, area, crime code, etc.).
* User Authentication: Secure login and user management via Django's authentication system.
* Dynamic Forms: Use formsets to add multiple victims, crime codes, and weapons to a case.
* Responsive Design: TailwindCSS ensures the app works well on all devices.

## 🛠Technologies Used
* Framework: Django
* Database: PostgreSQL
* Frontend: HTML, CSS (TailwindCSS), JavaScript
* Version Control: Git


## 🚀 Installation

**Prerequisites**:

* Python 3.8+
* PostgreSQL
* pip (Python package manager)

**Steps to Set Up the Project:**

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/lapd-crime-database.git
cd lapd-crime-database
```
2. **Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```
3. **Install Dependencies**
```bash
pip install -r requirements.txt
```
4. **Set Up the Database**
* Update settings.py with your PostgreSQL database credentials.
* Apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```
5. **Create a Superuser**
```bash
python manage.py createsuperuser
```
6. **Run the Server**
```bash
python manage.py runserver
```
7. **Access the Application**
Open your browser and visit: http://127.0.0.1:8000/

## 🗃Database Models
### Key Models:
* **Cases**: Represents crime cases with fields like date_rptd, premis_cd, status_code, and relations to victims, weapons, MO codes, and crime codes.
* **Victims**: Stores information about crime victims.
* **CrimesCodes**: Stores crime codes and their descriptions.
* **Weapons**: Stores weapon codes and their descriptions.
* **MoCodes**: Stores modus operandi (MO) codes.
* **CaseStatus**: Represents the status of a case (e.g., Open, Closed).

### Relationships:
Many-to-Many relationships between:
* Cases and Victims
* Cases and Weapons
* Cases and MoCodes (through CasesMoCodes)
* Cases and CrimesCodes (through CasesCrimeCodes)

## 🔧Usage
### Creating a New Case
1. Navigate to the New Case page.
2. Fill out the case details, add victims, crime codes, weapons, and MO codes.
3. Submit the form. You'll receive a success message upon creation.
### Searching for Crimes
1. Use the Search Crimes page to filter crimes by area, date, and other criteria.
2. View the results in a table format.
