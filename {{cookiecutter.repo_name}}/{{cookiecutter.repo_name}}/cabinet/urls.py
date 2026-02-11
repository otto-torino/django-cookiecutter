from django.urls import path
from .views import permalink

app_name = "cabinet"

urlpatterns = [
    path("permalink/<int:file_id>/", permalink, name="permalink"),
]
