from rest_framework import serializers
from f4hashtag.models import File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['s3_address','file_id','user_id','name','hashtag']
