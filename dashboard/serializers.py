from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserLoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField()
    class Meta:
        model=User
        fields = ['username', 'password']
    def validate(self, data):
        username = data['username']
        password = data['password']
        user_qs = User.objects.filter(username__iexact=username)
        if user_qs.exists() and user_qs.count() == 1:
            user_obj = user_qs.first()
            password_passes = user_obj.check_password(password)
            if password_passes:
                return data
            else:
                raise serializers.ValidationError({'error': 'Password is incorrect'})
        raise serializers.ValidationError({'error': 'The credentials provided are invalid.'})

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model=Camera
        fields=['id','name','lat','lng','tower','image']
        
