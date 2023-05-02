import datetime
import time
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from .models import Image
from .serializers import ImageSerializer

from django import forms 
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import escape
from .helper import pretty_request
 

# Create your views here.
class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['prompt', 'scribble']

class Imageview:
    def __init__ (self, scribble, prompt):
        self.scribble = scribble
        self.prompt = prompt
        self.generatedImg = None
    
    def generate(self):
        
        image = None
        # TODO include the replicate API
        self.generatedImg = image

        return self.generatedImg


def index(request):
    return render(request, 'index.html')

class applyStableDiffusion(APIView):
    
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ImageSerializer
  
    
    def post(self, request, format = None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            tmp = Imageview(request.data.get('scribble'), request.data.get('prompt'))
            img = tmp.generate()
            imagename = "generatedPic_v" + str(Image.objects.latest('id').id + 1)
            predir = 'media/'
            imgdirectory = 'generated/' + imagename + '.png'
            img.save(predir + imgdirectory)
            i = Image(scribble = tmp.scribble, prompt= tmp.prompt, generatedImage = imgdirectory )
            i.save() 
            
            data = ImageSerializer(Image.objects.latest('id')).data
            return JsonResponse({'data':data}, status=status.HTTP_201_CREATED)
        return Response({'Bad Request':'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
