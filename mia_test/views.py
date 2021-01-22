from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status, mixins
import tensorflow as tf # tensorflow 1.13.1+
import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt
import os
from glob import glob
from .apps import Selfie2AnimeConfig
#import PIL
from PIL import Image as Pimg
from django.http import Http404
from drf_yasg.inspectors.base import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from .serializers import *
from .models import *
from django.views import View 
import urllib

# 리액트 연동 테스트용 뷰. viewset을 이용, get, post, put, delete 가능
class GalleryView(viewsets.GenericViewSet, mixins.ListModelMixin, View):
    serializer_class = GallerySerializer
    
    @swagger_auto_schema(query_serializer=GallerySerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        conditions = {
            'gallery_id': self.kwargs.get("gallery_id", None),
            'created_at': self.kwargs.get("created_at", None),
            'user': self.kwargs.get("user", None),
        }
        conditions = {key: val for key, val in conditions.items() if val is not None}
        galleries = Gallery.objects.filter(**conditions)
        if not galleries.exists():
            raise Http404

        return galleries

    def add(self, request): 
        galleries = Gallery.objects.filter(**request.data)
        if galleries.exists():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        gallery_serializer = GallerySerializer(data=request.data, partial=True)
        if not gallery_serializer.is_valid():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        gallery = gallery_serializer.save()

        return Response(GallerySerializer(gallery).data, status=status.HTTP_201_CREATED)



class GalleryViewSet(viewsets.ModelViewSet):
    serializer_class = GallerySerializer

    def get_queryset(self):
        return Gallery.objects.all().order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save()


class call_model(APIView):

    def get(self,request):
        if request.method == 'GET':
            folder_path=Selfie2AnimeConfig.folder_path
            gan=Selfie2AnimeConfig.gan
            sess=Selfie2AnimeConfig.sess
            checkpoint_path=Selfie2AnimeConfig.checkpoint_path
            saver=Selfie2AnimeConfig.saver

            response = HttpResponse(content_type="image/jpeg")
            #img_path=(folder_path+'/selfie2anime/imgs/nana.jpg')
            

            detector = dlib.get_frontal_face_detector()
            sp = dlib.shape_predictor(folder_path+'/selfie2anime/checkpoint/shape_predictor_5_face_landmarks.dat')

         
            #이건 url,, 리액트에 띄운 사진 링크 복사 한 거,,되는거 확인했구 json으로 받아올 것입니다 ,,~~
            url = "data:image/jpeg;base64,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"
           
            resp = urllib.request.urlopen(url)
            img = np.asarray(bytearray(resp.read()), dtype="uint8")
            img = cv2.imdecode(img, cv2.IMREAD_COLOR)
           
        #    img = url_to_image(url)

         #   img = cv2.imread(img_path, flags=cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
     

            brightness = 0
            contrast = 30
            img = np.int16(img)
            img = img * (contrast / 127 + 1) - contrast + brightness
            img = np.clip(img, 0, 255)
            img = np.uint8(img)

            dets = detector(img)
            
            if len(dets) == 0:
                print('No faces!')
                result = None
            else:
                # don't crop if face is too big
                if dets[0].width() < img.shape[1] * 0.55:
                    s = sp(img, dets[0])
                    img = dlib.get_face_chip(img, s, size=256, padding=0.65)

                # preprocessing
                img_input = cv2.resize(img, dsize=(256, 256), interpolation=cv2.INTER_NEAREST)
                img_input = np.expand_dims(img_input, axis=0)
                img_input = img_input / 127.5 - 1

                # inference
                img_output = Selfie2AnimeConfig.sess.run(gan.test_fake_B, feed_dict={gan.test_domain_A: img_input})

                # postprocessing
                img_output = (img_output + 1) * 127.5
                img_output = img_output.astype(np.uint8).squeeze()
                
                result = np.hstack([cv2.resize(img, (256, 256)), img_output])
             #   cv2.imwrite(folder_path+'/selfie2anime/result/%s' % os.path.basename(img_path), result[:, :, ::-1])
                img_name = 'iu.jpg' #json 파일에서 파일 이름 가져오기 (url과 함께~) 파일 저장할 때 파일명으로 저장하기 위함 ! 
                cv2.imwrite(folder_path+'/selfie2anime/result/'+ img_name, result[:, :, ::-1])
                img = Pimg.open(folder_path+"/selfie2anime/result/"+img_name)
                img.save(response,'jpeg')

            return response

        
