# OPCUA-Fetch-Demo
**OPCUA-Fetch-Demo**, a demonstrates building a local OPC UA server that emits test random data, allowing developers to centrally access real-time sensor values for IoT and edge-device development. Easy to fetch from multiple programming languages.
___
**Attention:** Please remind this is a short demo for establishing an OPCUA Server and API, it is a development and testing server. Do not use it in a production deployment.
___
## 1. Deployment
Please pull this repo via the command below.

**Windows (PowerShell)**
```cmd
git clone https://github.com/afukuDev/OPCUA-Fetch-Demo.git
cd OPCUA-Fetch-Demo
```
___
## 2. Create & activate a Python virtual environment, then install dependencies
Python virtual environments are set up according to each developer’s preference. In this repository we provide a Conda-based example: create a Conda environment named OPCUA-Fetch-Demo running Python 3.8.20.

### 1. Create an Enviornment.
Using Conda prompt to create and activate.
```cmd
conda create -n OPCUA-Fetch-Demo python=3.8.20 -y
conda init
conda activate OPCUA-Fetch-Demo
```
Check the Python version.
```cmd
python --version   # Result Python 3.8.20

```
### 2. Python Module installation.
Using pip command install the module below.
**asyncua, Flask flask-cors, numpy**
```cmd
pip install asyncua Flask flask-cors numpy
```
___
### 3. Download Ua Expert and Start the OPCUA Server.
#### 1. Download UAExpert from [UAExpert](https://www.google.com/aclk?sa=L&pf=1&ai=DChsSEwjT6KTz9tSQAxVjB3sHHVokIk0YACICCAEQABoCdG0&co=1&ase=2&gclid=Cj0KCQjwgpzIBhCOARIsABZm7vF2EIE6AvhkLEsDdAT4hXCe4V1nA7geWVbjVWuABvCH37II1A2IbyMaAlZfEALw_wcB&cid=CAASlwHkaJ4XMIRgKhW5x06RDzBjNbo-28aLS_l1ZNzreIz2r6pJZUa66Qumq-mvj_rj_0hAF53HUfpiDidabnzwOg3hbxAlw_MuCjv9kgXWgGx8FCJdhb_UPI_BeppCN-3HY99anu3D7uzeCL5-aVNYi3S8ODTucsltdKWdfIfdyLqwlIEBXybZ2DoHm390Jr6hVz3vpysK9VSj&cce=2&category=acrcp_v1_32&sig=AOD64_3tp-rwsKD5aaoRkgGdVhrU9wxMsw&q&nis=4&adurl=https://www.unified-automation.com/products/development-tools/uaexpert.html?gad_source%3D1%26gad_campaignid%3D19807579087%26gbraid%3D0AAAAADrhzLpQBI19xGV9JwWjaKlINDryl%26gclid%3DCj0KCQjwgpzIBhCOARIsABZm7vF2EIE6AvhkLEsDdAT4hXCe4V1nA7geWVbjVWuABvCH37II1A2IbyMaAlZfEALw_wcB&ved=2ahUKEwja7Z7z9tSQAxW-e_UHHddhC5MQ0Qx6BAgMEAE)
![image](https://github.com/afukuDev/OPCUA-Fetch-Demo/blob/main/img/UAEXPERT.png)

#### 2. Start UP the Server.
``` CMD
python server_UI.py

```
___
### 4. Start the Server and Monitoring.
#### 1. Server startup.
Starting up the OPCUA Server and flask_api by pressing the "Start" button.

![image](https://github.com/afukuDev/OPCUA-Fetch-Demo/blob/main/img/SERVER_DEMO.png)

#### 2. UAExpert Settings.
Open UAExpert and select the server from "Local".
![image](https://github.com/afukuDev/OPCUA-Fetch-Demo/blob/main/img/ADD_SERVER.png)
Select the Server.
![image](https://github.com/afukuDev/OPCUA-Fetch-Demo/blob/main/img/ADD_SERVER_2.png)
Press the connect to monitoring.
![image](https://github.com/afukuDev/OPCUA-Fetch-Demo/blob/main/img/UA_Motoring.png)

### 3. Monitor the Data.
Select the object to see the live data for OPCUA Server.
![image](https://github.com/afukuDev/OPCUA-Fetch-Demo/blob/main/img/UA_DATA.png)

### 3. Third Party Program/APP Connection Example.
>**Note:** Currently we on working on establishing new third party app examples. New program example will be available soon.

Please select the example below.


| Program/Framework | Link | 
| -------- | -------- | 
| Vue.js    | [vue_demo](https://github.com/afukuDev/OPCUA-Fetch-Demo/tree/main/vue_demo)| 
