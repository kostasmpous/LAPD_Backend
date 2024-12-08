from django import forms

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