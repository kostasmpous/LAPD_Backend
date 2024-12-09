from django import forms
from django.forms import modelformset_factory, inlineformset_factory

from lapd.models import Cases, Victims, VictimDescent, CrimesCodes, CasesCrimeCodes, Weapons, MoCodes


class CrimeReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    crime_code = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'type': 'text'})
    )
    crime_code2 = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'type': 'text'})
    )
    start_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    end_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={'type': 'time'})
    )

class CaseForm(forms.ModelForm):
    mo_codes = forms.ModelMultipleChoiceField(
        queryset=MoCodes.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'hidden'})
    )
    class Meta:
        model = Cases
        fields = [
            'dr_no', 'date_rptd', 'date_occ', 'time_occ', 'area_code',
            'premis_cd', 'location', 'cross_street', 'lat', 'long', 'status_code'
        ]
        widgets = {
            'date_rptd': forms.DateInput(attrs={'type': 'date'}),
            'date_occ': forms.DateInput(attrs={'type': 'date'}),
            'time_occ': forms.TimeInput(attrs={'type': 'time'}),
            'lat': forms.TextInput(attrs={'placeholder': 'Latitude'}),
            'long': forms.TextInput(attrs={'placeholder': 'Longitude'}),
        }

class CasesWeaponsForm(forms.ModelForm):
    weapon = forms.ModelChoiceField(
        queryset=Weapons.objects.all(),
        label="Weapon",
        widget=forms.Select(attrs={'class': 'border border-gray-300 rounded px-4 py-2 w-full'})
    )

    class Meta:
        model = Cases.weapons.through  # Access the through model for the many-to-many relationship
        fields = ['weapon']

CasesWeaponsFormSet = modelformset_factory(
    Cases.weapons.through,
    form=CasesWeaponsForm,
    extra=1,  # Number of empty forms to display by default
)

class CasesCrimeCodesForm(forms.ModelForm):

    crime_code = forms.ModelChoiceField(
        queryset=CrimesCodes.objects.all(),
        label="Crime Code",
        widget=forms.Select(attrs={'class': 'border border-gray-300 rounded px-4 py-2 w-full'})
    )
    crime_level = forms.IntegerField(
        label="Crime Level",
        widget=forms.NumberInput(attrs={'class': 'border border-gray-300 rounded px-4 py-2 w-full', 'min': 1})
    )

    class Meta:
        model = CasesCrimeCodes
        fields = ['crime_code', 'crime_level']


CasesCrimeCodesFormSet = inlineformset_factory(
    parent_model=Cases,
    model=CasesCrimeCodes,
    form=CasesCrimeCodesForm,
    extra=3,  # Display 3 empty forms by default (you can adjust this number)
    can_delete=False  # Allow deleting crime codes if needed
)


class VictimForm(forms.ModelForm):
    class Meta:
        descent_code = forms.ModelChoiceField(
            queryset=VictimDescent.objects.all(),
            empty_label="Select Descent Code",
            widget=forms.Select(attrs={
                'class': 'border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'})
        )

        model = Victims
        fields = [ 'age', 'sex', 'descent_code']
        widgets = {
            'age': forms.NumberInput(attrs={'placeholder': 'Age'}),
            'sex': forms.TextInput(attrs={'placeholder': 'Sex'}),
        }

VictimFormSet = modelformset_factory(Victims, form=VictimForm, extra=1)
