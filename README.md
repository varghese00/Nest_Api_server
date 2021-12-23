# Nest_Api_server
Computer Systems IOT Assignment

This project is mainly focused on interacting with google nest api and tweaking the heating parameters and automating a few devices.

At the momemt the nest device i have senses only the temperature and humidity of the place it is installed which is downstairs. The temperature of upstairs does not automate the heating,
the only way to do it is get another nest device.

As a part of this project I have used rasperry pi and senseHat to interact with the google nest api and manipulate the readings from nest device and automate the heating of the house
based on the heating from upstairs as well, where the raspberry pi is running. 
Raspberry Pi makes the api call and get the temp and humidity readings and compare it with sensehat readings and automate the heating controls. Based on the humidity levels i have 
automated the turning on and off of dehumidifier using tapo smart plug.

I used blynk to visualise the readings so didnt use flask or fast api to make a web app. Only thing i would have wished to do is to manually turn on and off the devices and break the
loop and re run it. Tried but could not figure out ! 
Used paho mqtt,webhooks and thingspeak to publish subscribe to the events turned on and off.

I could have done better but it was really draining especially working with google api and getting the tokens working to make the calls to nest api. 

***Ignore html,css and templates,static folders and files !!  Json files are for reference purposes !
