from django.shortcuts import render
from django.http import HttpResponse

def home_page_view(request,*args,**kwargs):
    my_title = "LAPD Crime Database"
    my_context = {
        "page_title": my_title,
    }
    html_template = "Home.html"
    return render(request,html_template,my_context)