from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("random/", views.RandomEntry.as_view(), name='random-entry'),
    path("search/", views.SearchView.as_view(), name='search-point'),
    path('create_entry/', views.CreateEntry.as_view(), name='create-entry-point'),
    path('edit-entry/<str:entry>', views.EditEntry.as_view(), name='edit-entry-point'),
    path("entries/<str:entry>/", views.TitleView.as_view(), name="entry-point")
]
