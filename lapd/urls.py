"""
URL configuration for lapd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.i18n import urlpatterns

from auth.views import login_view
from .views import home_page_view, crime_database_view, search_crime, create_case
from django.contrib import admin
from django.urls import path, include
from auth import views as auth_views
from . import views
#urlpatterns = [
 #   path('admin/', admin.site.urls),
#]

urlpatterns=[
    path('home/', home_page_view, name='home'),
    path("queries/",crime_database_view,name="queries"),
    path("newcase/",create_case,name="newcase"),
    path("search/",search_crime,name="search"),
    path("login/",login_view),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # new

    path('cases/', create_case, name='case_list'),

]
