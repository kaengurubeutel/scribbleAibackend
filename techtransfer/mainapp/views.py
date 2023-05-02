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
 
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
import numpy as np
import torch
from PIL import Image as Imgs

controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-scribble").to('cpu')

pipe = StableDiffusionControlNetPipeline.from_pretrained(

    "runwayml/stable-diffusion-v1-5", controlnet=controlnet

).to('cpu')
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)


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
        neg_prompts= "Blurriness, Pixelation, Overexposure, Underexposure, Incorrect white balance, Incorrect color saturation,ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face, bad hands, blurry, distorted, Incorrect contrast, Incorrect brightness, Visible compression artifacts, Poor lighting, Unnatural shadows and highlights, Undefined edges, Unsmooth transitions, Unrealistic textures, Imbalanced contrast, Uneven exposure, Poor color accuracy, Inaccurate reflections, Motion blur, Incorrect depth of field, Lens distortion, Incorrect perspective, Visible seams or stitching, Image distortion or artifacts, Jagged edges or aliasing, Inaccurate geometry, Incorrect camera angle, Poor framing, Halos, Image artifacts, Color bleeding, Posterization, Visible banding, Vignetting, Noise reduction artifacts, Over-sharpening, Under-sharpening, Banding in gradients, HDR artifacts, Color cast, Dust or scratches, Image warping, Blur in moving objects, Ghosting, Interpolation artifacts, Lack of detail in shadows or highlights, Moiré patterns in fine textures, Color shifts in bright or dark areas, Vignetting in corners or edges, Noise reduction artifacts, Incorrect sharpening, Unsharp or unclear fine details, Chromatic aberration in high-contrast areas, Distortion or skewing of objects, Lack of detail in complex textures, Image artifacts caused by lens or sensor dust, Color fringing in high-contrast areas, Lens flare in bright areas, Scratches or dust spots caused by hardware, Visible image seams, Incorrect aspect ratio, Incorrect aspect scaling, Incorrect cropping, Visible noise or grain, Incorrect blending of images, Incorrect lighting direction, Poorly defined or unnatural shadows, Poorly defined or unnatural highlights, Inconsistent color saturation, Inconsistent contrast, Inconsistent brightness, Unnatural color rendering, Lack of sharpness, Lack of clarity, Inconsistent geometry, Inconsistent texture, Inconsistent color accuracy, Inconsistent depth of field, Incorrect lens distortion correction, Incorrect perspective correction, Incorrect color balance, Incorrect color grading, Inconsistent sharpening, Unnatural-looking textures, Lack of fine detail, Poorly defined or unnatural edges, Poorly defined or unnatural transitions, Incorrect image aspect ratio, Poorly defined or unnatural reflections, Poorly defined or unnatural shadows and highlights, Inconsistent exposure, Inconsistent lighting, Inconsistent saturation, Inconsistent brightness and contrast, low poly count, Unnatural-looking materials or textures, Incorrect or inconsistent scale, Incorrect or inconsistent lighting, Poorly defined or unnatural shadows, Inconsistent polygon density, Poorly optimized topology, Incorrect or inconsistent rigging, Incorrect or inconsistent weighting, Unnatural-looking motion or movement, Incorrect or inconsistent physics, Visible seams or texture stretching, Incorrect or inconsistent texture mapping, Poorly defined or unnatural reflections, Incorrect or inconsistent camera angle, Poorly defined or unnatural edges, Incorrect or inconsistent depth of field, Incorrect or inconsistent aspect ratio, Inaccurate or inconsistent physics simulation, Inconsistent or unnatural lighting, Unnatural or unrealistic shadows and reflections, Lack of detail, Inconsistent or unnatural textures, Inconsistent or unnatural geometry, Unnatural or unrealistic animation."
        init_image = Imgs.open(self.scribble).convert("RGB")
        generator = torch.manual_seed(0)

        image = pipe(

            prompt=self.prompt, num_inference_steps=21, generator=generator, image=init_image, negative_prompt=neg_prompts

        ).images[0]


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
