from django.shortcuts import render
from django.contrib.auth import login,logout,authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class userform(LoginRequiredMixin,APIView):
    def get(self,request):
        return Response({'msg':'Registration success'}) 

class LoginUserForm(APIView):
    def post(self,request):
        serializer=UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username=serializer.data.get('username')
            password=serializer.data.get('password')
            user=authenticate(request,username=username,password=password)
            if user is not None:
                return Response({'msg':'Login Successful'},status=status.HTTP_200_OK)
            else:
                return Response({'errors':['Username or Password is not valid']},status=status.HTTP_404_NOT_FOUND)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class CameraList(LoginRequiredMixin,APIView):
    def get(self,request):
        data=Camera.objects.all()
        print(data.values())
        return Response({'data':data.values()},status=status.HTTP_200_OK)

class EventList(APIView):
    def get(self,request):
        data=Event.objects.all()
        print(data.values())
        return Response({'data':data.values()},status=status.HTTP_200_OK)

class SensorList(LoginRequiredMixin,APIView):
    def get(self,request):
        data=Sensor.objects.all()
        print(data.values())
        return Response({'data':data.values()},status=status.HTTP_200_OK)
class TowerList(LoginRequiredMixin,APIView):
    def get(self,request):
        data=Tower.objects.all()
        print(data.values())
        return Response({'data':data.values()},status=status.HTTP_200_OK)
class TowerDetailList(APIView):
    def get(self,request):
        data=(Tower.objects.all()).values()
        for i in data:
            print(i)
            i['cameras']=(Camera.objects.filter(tower_id=i['id'])).values()
            i['sensors']=(Sensor.objects.filter(tower_id=i['id'])).values()
        print(data)
        return Response({'data':data},status=status.HTTP_200_OK)
def loginUser(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            request.session['status']='admin'
            return redirect('home')
        else:
            messages.info(request,'Username OR Password is incorrect.')
    return render(request,'login.html')

def logoutUser(request):
    logout(request)
    request.session['status']='anonymous'
    return redirect('loginUser')