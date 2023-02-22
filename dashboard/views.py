from django.shortcuts import render
from django.contrib.auth import login,logout,authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import paho.mqtt.client as paho
from paho import mqtt
import paho.mqtt.client as mqtt
from time import sleep
import certifi,json

# Create your views here.
class PTZControlsHawa(APIView):
    def __init__(self):
        self.res=0
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def on_publish(self, client, userdata, mid):
        print(client, userdata, mid)
        if mid>self.res:
            self.res=mid

    def on_log(self, mqttc, obj, level, string):
        #print(string)
        return string

    def post(self,request):
        print(request.data)
        pan=request.data["pan"]
        tilt=request.data["tilt"]
        zoom=request.data["zoom"]
            
        client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        client.tls_set(ca_certs=certifi.where())

        client.on_publish = self.on_publish
        client.on_connect = self.on_connect
        client.on_log = self.on_log

        host = "2be1374228c54154bc14422981467fff.s2.eu.hivemq.cloud"
        client.username_pw_set("admin", "Lumsadmin@n1")
        client.connect(host, 8883, 60)
        client.loop_start()
        client.publish("PTZ-HawaGali/PAN", pan, 1)
        client.publish("PTZ-HawaGali/TILT", tilt, 1)
        client.publish("PTZ-HawaGali/ZOOM", zoom, 1)
        sleep(1)
        pub = 0
        client.disconnect()
        client.loop_stop()
        return Response(json.dumps({"data":self.res}))

class PTZControlsPanja(APIView):
    def __init__(self):
        self.res=0
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def on_publish(self, client, userdata, mid):
        print(client, userdata, mid)
        if mid>self.res:
            self.res=mid

    def on_log(self, mqttc, obj, level, string):
        #print(string)
        return string

    def post(self,request):
        print(request.data)
        pan=request.data["pan"]
        tilt=request.data["tilt"]
        zoom=request.data["zoom"]
            
        client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        client.tls_set(ca_certs=certifi.where())

        client.on_publish = self.on_publish
        client.on_connect = self.on_connect
        client.on_log = self.on_log

        host = "2be1374228c54154bc14422981467fff.s2.eu.hivemq.cloud"
        client.username_pw_set("admin", "Lumsadmin@n1")
        client.connect(host, 8883, 60)
        client.loop_start()
        client.publish("PTZ-PanjaGali/PAN", pan, 1)
        client.publish("PTZ-PanjaGali/TILT", tilt, 1)
        client.publish("PTZ-PanjaGali/ZOOM", zoom, 1)
        sleep(1)
        pub = 0
        client.disconnect()
        client.loop_stop()
        return Response(json.dumps({"data":self.res}))

class PTZControlsPalm(APIView):
    def __init__(self):
        self.res=0
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def on_publish(self, client, userdata, mid):
        print(client, userdata, mid)
        if mid>self.res:
            self.res=mid

    def on_log(self, mqttc, obj, level, string):
        #print(string)
        return string

    def post(self,request):
        print(request.data)
        pan=request.data["pan"]
        tilt=request.data["tilt"]
        zoom=request.data["zoom"]
            
        client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        client.tls_set(ca_certs=certifi.where())

        client.on_publish = self.on_publish
        client.on_connect = self.on_connect
        client.on_log = self.on_log

        host = "2be1374228c54154bc14422981467fff.s2.eu.hivemq.cloud"
        client.username_pw_set("admin", "Lumsadmin@n1")
        client.connect(host, 8883, 60)
        client.loop_start()
        client.publish("PTZ-PalmGali/PAN", pan, 1)
        client.publish("PTZ-PalmGali/TILT", tilt, 1)
        client.publish("PTZ-PalmGali/ZOOM", zoom, 1)
        sleep(1)
        pub = 0
        client.disconnect()
        client.loop_stop()
        return Response(json.dumps({"data":self.res}))
