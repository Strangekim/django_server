# problems/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.problem_upload, name="problem_upload"),
]
