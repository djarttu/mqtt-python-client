import RPi.GPIO as GPIO
import os
import boto3
from boto3.s3.transfer import S3Transfer
from botocore.exceptions import NoCredentialsError
from subprocess import call
import time
from datetime import datetime
import paho.mqtt.client as mqtt
ledpinRed = 20
ledpinGreen = 26
access_key_id='XXXX'
secret_access_key='XXXX'
session_token='XXXX'
bucketName='myBucketti'
x=20
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ledpinRed, GPIO.OUT)
GPIO.setup(ledpinGreen, GPIO.OUT)
eka=True
MQTT_server="X.X.X.X"

def on_connect(client, userdata, flags, rc):
    print("Connected"+str(rc))
    client.subscribe("ovi")
    
def on_message(client, userdata, msg):
    print(msg.topic)
    o=msg.payload.decode('utf-8')
    print(o)
    
    sytytaLed(o)
    
    
def sytytaLed(o):
    print("pitäs sytyttää")
    if(o=='avaa'):
        print (o)
        GPIO.output(ledpinGreen, GPIO.HIGH)
        time.sleep(6)
        print ("led off")
        GPIO.output(ledpinGreen, GPIO.LOW)
        time.sleep(2)
    if(o=='kiinni'):
        print (o)
        GPIO.output(ledpinRed, GPIO.HIGH)
        time.sleep(6)
        print ("led off")
        GPIO.output(ledpinRed, GPIO.LOW)
        time.sleep(2)   
    #x-=1
    #print (x)
    #GPIO.cleanup()
    
def on_public():
    print("published")
def capture():
    dt = str(datetime.now())
    print(dt)
    dtime = dt[0:4]+dt[5:7]+dt[8:10]+dt[11:13]+dt[14:16]+dt[17:19]
    try:
        call(["fswebcam", "-d", "/dev/video0", "-r", "1280x720", "--no-banner", "./%d.jpg" % int(dtime)])
        global localFile
        localFile=dtime+".jpg"
        global localFilePath
        localFilePath="/home/dietpi/"+localFile
        print(localFile)
        ##print(localFilePath)
    except:
        print("Kameraa ei löytynny")
def upload_to_aws(localFilePath, bucket, s3_file):
    print(access_key_id)
    s3=boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, aws_session_token=session_token)
    print(localFile)
    try:
        s3.upload_file(localFile,bucket,s3_file)
        print("Upload successful")
        client.publish("kuva",localFile,0)
        return True
    except FileNotFoundError:
        print("File not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
            
client=mqtt.Client()
client.on_publish=on_public
client.on_message=on_message
client.on_connect=on_connect
client.connect(MQTT_server, 1883, 60)
client.loop_start()

while True:
    if GPIO.input(18)==GPIO.HIGH:
        print("Nappi toimmiui")
        time.sleep(2)
        capture()
        print(localFilePath)
        uploaded=upload_to_aws(localFilePath,bucketName,localFile)
        """    print ("led on")\n    GPIO.output(ledpin, GPIO.HIGH)\n    time.sleep(2)\n    print ("led off")\n    GPIO.output(ledpin, GPIO.LOW)\n    time.sleep(2)\n    #x-=1\n    print (x)\n    \nGPIO.cleanup()"""