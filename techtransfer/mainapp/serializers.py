from rest_framework import serializers
import base64
from django.core.files.base import ContentFile
from django.core.files.base import ContentFile
import base64

import uuid
from .models import Image
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

