from django.urls import path
from .views import applyStableDiffusion

urlpatterns = [
    path("run", applyStableDiffusion.as_view(), name="run")
]
