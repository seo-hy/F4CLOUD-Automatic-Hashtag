from django.shortcuts import render

# Create your views here.
from f4hashtag.models import File
from f4hashtag.serializers import FileSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import boto3
from datetime import datetime

from io import BytesIO
import io

class hashtag(APIView):
    def post(self, request):
        if request.method == 'POST':
            try:
                data = request.data
                file_id = data['fileId']
                user_id = data['userId']

                s3_address = File.objects.values('s3_address').distinct().filter(file_id=file_id, user_id=user_id)
                s3_address = s3_address[0]['s3_address']
                client = boto3.client('rekognition')

                # file_address format : object URL
                proc = s3_address[8:]
                bucket = proc[:proc.find('.')]
                file_path = proc[proc.find('/') + 1:]

                print(bucket, file_path)

                if file_path.find('/') != -1:
                    file_name = file_path
                    while (file_name.find('/') != -1):
                        file_name = file_name[file_name.find('/') + 1:]
                else:
                    file_name = file_path

                if file_name.find('/') != -1:
                    file_name = file_name[file_name.find('/') + 1:]

                # Use Amazon rekognition Object detection
                response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': file_name}}, MaxLabels=10)
                obj_list = list()
                translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)

                # Set Max
                max = 2
                threshold = 95.0
                for label in response['Labels']:
                    max-=1
                    #print("Label: " + label['Name'])
                    #print("Confidence: " + str(label['Confidence']))
                    if(max == -1):
                        break
                    if(label['Confidence']>threshold):
                        print(label['Name'])
                        print("Confidence: " + str(label['Confidence']))
                        result = translate.translate_text(Text=label['Name'],
                                                          SourceLanguageCode="en", TargetLanguageCode="ko")
                        tag = str(result.get('TranslatedText'))
                        tag = tag.replace(' ','_')
                        obj_list.append(tag)
                print(obj_list)
                if(len(obj_list)==0):
                    return Response({'recommend' : ''})
                recommend = '#'
                recommend += ' #'.join(obj_list)
                msg = {'recommend':recommend}

                return Response(msg,status=status.HTTP_200_OK)
            except Exception as e:
                msg = {'msg' : str(e) }
                print(msg)
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.method == 'PUT':
            try:
                data = request.data
                print(data)
                file_id = data['fileId']
                user_id = data['userId']
                hashtag = data['hashtag']
                item = File.objects.filter(user_id=user_id, file_id=file_id)
                item.update(hashtag=hashtag)
                res = File.objects.values('hashtag').distinct().filter(user_id=user_id, file_id=file_id)
                res = res[0]['hashtag']
                msg = {'hashtag': res}
                print(msg)
                return Response(msg,status=status.HTTP_200_OK)

            except Exception as e:
                msg = {'msg' : str(e) }
                print(msg)
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)

class search_hashtag(APIView):
    def get(self,request):
        if request.method == 'GET':
            try:
                res = list()
                data = request.data
                user_id = request.GET['userId']
                keyword = request.GET['keyword']
                tmp = File.objects.filter(hashtag__contains=keyword,user_id=user_id)
                for e in tmp:
                    res.append(e)

                serializer = FileSerializer(res, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except Exception as e:
                msg = {'msg': str(e)}
                print(msg)
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)