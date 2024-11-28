from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def home_page_view(request,*args,**kwargs):
    my_title = "LAPD Crime Database"
    my_context = {
        "page_title": my_title,
    }
    html_template = "Home.html"
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