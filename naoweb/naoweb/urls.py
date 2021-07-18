"""naoweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
import sys
from django.contrib import admin
from django.urls import path
import app.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app.views.pin_page),
    path('presentations', app.views.index),
    path('create/presentation', app.views.create_presentation),
    path('presentation/<int:pid>/create/survey', app.views.create_survey),
    path('survey/<int:sid>', app.views.get_survey),
    path('update/survey/<int:sid>', app.views.update_survey),
    path('open/survey/<int:sid>', app.views.open_survey),
    path('survey/status/<int:sid>', app.views.get_survey_status),
    path('survey/pin/<str:pin>', app.views.get_survey_by_pin),
    path('view/presentation/<int:pid>', app.views.presentation_page),
    path('view/survey/<int:sid>', app.views.survey_page),
    path('answer/survey/<int:sid>', app.views.answer_survey)
]
