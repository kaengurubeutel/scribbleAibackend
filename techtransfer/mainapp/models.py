from django.db import models

# Create your models here.
class Image(models.Model):
    scribble = models.ImageField("Scribble", upload_to="scribbles", blank=False)
    prompt = models.CharField("Prompt", max_length=200)
    generatedImage = models.ImageField("GeneratedImage", upload_to="generated", blank=True)
    