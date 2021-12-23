
## Register for google device acces program here :https://developers.google.com/nest/device-access/get-started
## Set up Google Cloud Platform and Enable the API and get an OAuth 2.0 Client ID
## Create a new project in device access page save the clientid and projectid, make sure redirect uri is as per instructions in the above link.
## Link your google account for the project by visiting the uri https://nestservices.google.com/partnerconnections/project-id/auth?redirect_uri=https://www.google.com&access_type=offline&prompt=consent&client_id=oauth2-client-id&response_type=code&scope=https://www.googleapis.com/auth/sdm.service
## In the above uri link replace the projectid and clientid with yours which was obtained in previous steps.
## Above link with your credentials will give you an authorisation code in the redirect uri, do not close that page without making note of it.
## Use the authorization code to retrieve an access token, that you can use to call the SDM (smart device management)API
## Link for above is here https://developers.google.com/nest/device-access/authorize#get_an_access_token
## Google OAuth returns two tokens, an access token and a refresh token.
## Copy both these values. The access token is used to call the SDM API and the refresh token is used to get a new access token.
## Authorization is not complete until you make your first devices.list call with your new access token
## Use  curl to make this call for the devices endpoint: from a terminal, curl uiri is below
## curl -X GET 'https://smartdevicemanagement.googleapis.com/v1/enterprises/project-id/devices' \-H 'Content-Type: application/json' \-H 'Authorization: Bearer access-token'
## Access tokens for the SDM API are only valid for 1 hour, as noted in the expires_in parameter returned by Google OAuth. If your access token expires, use the refresh token to get a new one.
## curl for new access token with refresh token is :curl -L -X POST 'https://www.googleapis.com/oauth2/v4/token?client_id=oauth2-client-id&client_secret=oauth2-client-secret&refresh_token=refresh-token&grant_type=refresh_token' 
## https://developers.google.com/nest/device-access/registration
## https://developers.google.com/nest/device-access/get-started
## https://developers.google.com/nest/device-access/authorize
## https://developers.google.com/nest/device-access/use-the-api
## https://developers.google.com/nest/device-access/api/thermostat from __future__ import print_function
## to localhost on your for firebase login redirection and nest auth redirection localhost must be forwarded to 9005 or whatever port your,
#  rpi tries to localhost, in mine it was trying to redirect to 9005 all other ports refused to connect.

from fastapi.applications import FastAPI
import flask
from flask import app
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import sys
import time
import pickle      ## pickle is used to save response as files in bytes  https://docs.python.org/3/library/pickle.html
from dotenv import dotenv_values
import pyrebase
from google.auth import credentials
from google_auth_oauthlib.helpers import credentials_from_session
import requests
import json
import os
from flask import Flask,Blueprint,jsonify,url_for
from flask_cors import CORS
import BlynkLib
from time import sleep 
from PyP100 import PyP100
import logging
import google.oauth2.credentials
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import requests
from google import oauth2
from google_auth_oauthlib.flow import InstalledAppFlow,Flow  ##needs to pip install it first
from sense_hat import SenseHat
from google.auth.transport.requests import Request
import asyncio
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates


app= FastAPI()


sense=SenseHat()
sense.clear()
config = dotenv_values(".env") ## for mqtt creds and projectcode of nestapi
credentials = None
BLYNK_AUTH = config["BLYNK_AUTH"]
# initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)


#configure Logging
logging.basicConfig(level=logging.INFO)
# Define event callbacks for MQTT
def on_connect(client, userdata, flags, rc):
    logging.info("Connection Result: " + str(rc))

def on_publish(client, obj, mid):
    logging.info("Message Sent ID: " + str(mid))

mqttc = mqtt.Client(client_id=config["clientId"])

# Assign event callbacks
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

# parse mqtt url for connection details
url_str = 'mqtt://mqtt3.thingspeak.com:8883'
print(url_str)
url = urlparse(url_str)
base_topic = url.path[1:]

# Configure MQTT client with user name and password
mqttc.username_pw_set(config["username"], config["password"])
# Load CA certificate for Transport Layer Security
mqttc.tls_set("./broker.thingspeak.crt")

#Connect to MQTT Broker
mqttc.connect(url.hostname, url.port)
mqttc.loop_start()

#Set Thingspeak Channel to publish to
topic = "channels/"+config["channelId"]+"/publish"

##SmartPlug Code
p100 = PyP100.P100(config["tapo_ipaddress"], config["tapo_email"], config["tapo_password"]) #Creating a P100 plug object
p100.handshake() #Creates the cookies required for further methods 
p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods
#p100.turnOn() #Sends the turn on request
#p100.setBrightness(100) #Sends the set brightness request
p100.turnOff() #Sends the turn off request
p100.getDeviceInfo() #Returns dict with all the device info




##creating the flow for authentication built in methods from pickle and flow
# token.pickle stores the user's credentials from previously successful logins
def get_access_token():
    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:  ## rb is read bytes
            credentials = pickle.load(token)
    if credentials and credentials.valid:
        access_token = "Bearer" + ' ' + credentials.token
    # If there are no valid credentials available, then either refresh the token or log in.
    elif not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            refresh_token = credentials.refresh_token
            print("expired access token: " + credentials.token) 
            credentials.refresh(Request())
            print(refresh_token)
            # print(dir(credentials))
            print(credentials.client_id)
            print(credentials.client_secret)
            print(credentials.token_uri)
            print(credentials.valid)
            print(credentials.expired)
            access_token = "Bearer" + ' ' + credentials.token
            print("New Access token :" +  access_token) ## token which is needed for api calls
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'clientId_secret.json',
                scopes=[
                    'https://www.googleapis.com/auth/sdm.service'
                ]
            )

            flow.run_local_server(port=9005, prompt='consent',
                                authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:           ## wb is write bytes
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)
    return access_token  ##watch the return indentation just one tab space from def for return of the main method
accesToken=get_access_token()



# print(get_access_token()) ## token which is needed for api calls
uri_get_devices = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + config["projectCode"] + '/devices'
headers = {
    'Content-Type': 'application/json',
    'Authorization': accesToken,
}
response = requests.get(uri_get_devices, headers=headers)
# print(response.json())
response_json = response.json()
# print(response_json)
device_0_name = response_json['devices'][0]['name']
# print(device_0_name)   ## device_0_name is the first one from json at 0 , i have only one nest device which is thermostat



def thermostat_humidity():
    uri_get_device = 'https://smartdevicemanagement.googleapis.com/v1/' + device_0_name

    headers = {
        'Content-Type': 'application/json',
        'Authorization': accesToken,
    }

    response = requests.get(uri_get_device, headers=headers)

    response_json = response.json()
    humidity = response_json['traits']['sdm.devices.traits.Humidity']['ambientHumidityPercent']
    print('Nest Humidity is :', humidity)
    return humidity

Nest_thermostat_humidity=thermostat_humidity()

# print ("Current Humidity on corridor from nest device is", thermostat_humidity())


##function for temperature
def thermostat_temperature():
    uri_get_device = 'https://smartdevicemanagement.googleapis.com/v1/' + device_0_name
    headers = {
        'Content-Type': 'application/json',
        'Authorization': accesToken,
    }
    response = requests.get(uri_get_device, headers=headers)
    response_json = response.json()
    temperature = response_json['traits']['sdm.devices.traits.Temperature']['ambientTemperatureCelsius']
    print('Nest Temperature is :', temperature)
    return temperature
nest_thermostat_temp=thermostat_temperature()
# print ("Current Temperature on Corridor from nest device is " , (thermostat_temperature()) )




def sense_hat_temp():
    temp = round(sense.temperature,2) - 14
    return temp
print ("Temperature inside the room from sense hat is : " , sense_hat_temp())

def sense_hat_humidity():
    humidity = round(sense.humidity,2)
    return humidity
print ("Humidity inside the room from sense hat is : " , sense_hat_humidity())


def turn_ON_nest_heating():
    url_get_device = 'https://smartdevicemanagement.googleapis.com/v1/' + device_0_name
    headers = {
        'Content-Type': 'application/json',
        'Authorization': accesToken,
    }
    response = requests.get(url_get_device, headers=headers)
    response_json = response.json()
    blynk.run()
    current_sensehat_temperature = sense_hat_temp()
    current_nestsensor_temperature = nest_thermostat_temp
    current_sensehat_temperature = current_nestsensor_temperature - 1  ## upstairs is kinda always colder than downstairs where the nest device is
    low_temp=18
    blynk.virtual_write(3,nest_thermostat_temp)
    blynk.virtual_write(4,current_sensehat_temperature)
    print("heating turns on at temp below :", low_temp,"temp now is: ", current_sensehat_temperature)
    # high_temp=20
    # set_temperature = response_json['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint']['heatCelsius']
    heating_ON_temp_threshold = current_sensehat_temperature + 1.5 ## heat to ambient temp + 1.5
    if current_sensehat_temperature < low_temp:
        temp_set_to = heating_ON_temp_threshold  ## set the set temp to 1 degree above the current temperature
        blynk.virtual_write(3,nest_thermostat_temp)
        blynk.virtual_write(4,current_sensehat_temperature)  
        uri_setHeat_temperature =  'https://smartdevicemanagement.googleapis.com/v1/' + device_0_name + ':executeCommand'
        headers = {
        'Content-Type': 'application/json',
        'Authorization': accesToken,
        }
        data = '{"command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat", "params" : {"heatCelsius" : ' + str(temp_set_to) + '} }'
        response = requests.post(uri_setHeat_temperature, headers=headers, data=data)
        print("Nest Heating is turned on,Temp now is: " , nest_thermostat_temp ,"it will be turned off at :", temp_set_to )
    elif nest_thermostat_temp > heating_ON_temp_threshold :
        temp_set_to = nest_thermostat_temp - 1
        blynk.virtual_write(3,nest_thermostat_temp)
        blynk.virtual_write(4,current_sensehat_temperature)
        uri_setHeat_temperature =  'https://smartdevicemanagement.googleapis.com/v1/' + device_0_name + ':executeCommand'
        headers = {
        'Content-Type': 'application/json',
        'Authorization': accesToken,
        }
        data = '{"command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat", "params" : {"heatCelsius" : ' + str(temp_set_to) + '} }'
        response = requests.post(uri_setHeat_temperature, headers=headers, data=data)
        print("Nest Heating is turned off,Temp now is: ", nest_thermostat_temp )



def turn_ON_dehumidifier():
            blynk.run()
            low_humidity_threshold = 30
            high_humidity_threshold = 50
            blynk.virtual_write(1,thermostat_humidity())
            blynk.virtual_write(2,sense_hat_humidity())
            # await asyncio.sleep(30)
            if thermostat_humidity() > high_humidity_threshold:
                # thingspeak_humidity_uri='https://api.thingspeak.com/update?api_key=65KUKP9LE538POLB&field2={{thermostat_humidity()}}'
                # requests.post(thingspeak_humidity_uri)
                print("Turning on de-dehumidifier,ideal humidity is 40-50, nest sensor humidity is: ", thermostat_humidity())
                p100.turnOn()
                payload="field2="+str(thermostat_humidity())
                mqttc.publish(topic, payload)
                time.sleep(30)
            elif thermostat_humidity() < low_humidity_threshold:
                print("Humidity is low downstairs")                  
            elif thermostat_humidity() < high_humidity_threshold:
                print("Humidity is good downstairs")
                print("Turning off de-dehumidifier,ideal humidity is 40-50,nest sensor humidity is: ", thermostat_humidity())
                p100.turnOff()
                payload="field2="+str(thermostat_humidity())
                mqttc.publish(topic, payload)

                time.sleep(30)


while True:
    turn_ON_nest_heating()
    turn_ON_dehumidifier()
    sleep(20)
    
    #     ## https://fastapi.tiangolo.com/advanced/templates/?h=templ
    # @app.get("/")
    # def nest_readings():
    #     nest_humidity=thermostat_humidity()
    #     nest_temperature=thermostat_temperature()
    #     sense_temperature=sense_hat_temp()
    #     sense_humidity=sense_hat_humidity()
    #     return templates.TemplateResponse("index.html",{"nest_humidity":nest_humidity,"nest_temperature":nest_temperature,
    #     "sense_temperature":sense_temperature,"sense_humidity":sense_humidity})                    
    






 

