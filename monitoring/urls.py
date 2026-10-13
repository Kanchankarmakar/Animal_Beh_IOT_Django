
from django.urls import path

from . import views

urlpatterns = [
    path("animals/", views.animal_list, name="animal_list"),
    path("devices/", views.device_list, name="device_list"),
    path("animals/add/", views.animal_create, name="animal_create"),
    path(
        "animals/<int:pk>/edit/",
        views.animal_update,
        name="animal_update",
    ),
    path(
        "animals/<int:pk>/delete/",
        views.animal_delete,
        name="animal_delete",
    ),
    
    path(
        "animals/<int:pk>/monitoring/",
        views.animal_monitoring,
        name="animal_monitoring",
    ),

]
