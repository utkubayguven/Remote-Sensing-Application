# Remote-Sensing-Application
## Overview
This project simulates a networked system with a temperature sensor, humidity sensor, gateway, and server. It's designed to demonstrate the integration and communication between different network components using TCP and UDP protocols.

##Installation
->Ensure Python 3.x is installed.
->Clone the repository: git clone [[repository link]](https://github.com/utkubayguven/Remote-Sensing-Application).

##Components

###Temperature Sensor
->Generates values between 20-30°C.
->Sends data to the gateway via TCP.

###Humidity Sensor
->Generates values between 40-90%.
->Sends data to the gateway via UDP.
->Triggers data transmission when humidity > 80% or every 3 seconds.

###Gateway
->Receives data from sensors.
->Forwards data to the server.
->Monitors sensor activity.

###Server
->Stores temperature and humidity data.
->Web interface to display data.

##Usage
->Start the server: python server.py.
->Run the gateway: python gateway.py.
->Activate sensors: python temperature_sensor.py and python humidity_sensor.py.

##Troubleshooting
->Ensure all components are running.
->Check network configurations.
