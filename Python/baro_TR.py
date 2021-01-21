#!/usr/bin/python3
# -*- coding:utf-8 -*-
#import baro_afficheur

import socket
import re
import datetime
import sys
import os
import time
import threading
import RPi.GPIO as GPIO

import configparser


#libdir = sys.path
#if os.path.exists(libdir):
 #   sys.path.append(libdir)

from Afficheur import Afficheur
from DataManager import *
from GraphManager import *

mConfig=configparser.ConfigParser()

try:
    with open('configBaro.ini'): pass
except IOError:
    print("Ini Error")
    cfg = configparser.ConfigParser()
    S = 'NETWORK'
    cfg.add_section(S)
    cfg.set(S, 'broadcastaddress', '255.255.255.255')
    cfg.set(S, 'udpportdata', '50002')
    cfg.set(S, 'udpportconfig', '50003')
    cfg.set(S, 'timeoutwifi', '10')
    S = 'SETTINGS'
    cfg.add_section(S)
    cfg.set(S, 'refreshperiod', '60')
    cfg.set(S,'scale','1')
    cfg.set(S,'typegrf','0') #0=pression 1=temperature 2=humidity
    S= 'RECORDS'
    cfg.add_section(S)
    cfg.set(S, 'recordsdirectory', '/home/pi/DatasBaro/')
    cfg.set(S, 'recordratio', '5')
    cfg.write(open('configBaro.ini','w'))
   
mConfig.read('configBaro.ini')
UDP_IP=mConfig.get('NETWORK','broadcastaddress')
UDP_PORT_DATA =int(mConfig.get('NETWORK','udpportdata'))
UDP_PORT_CONFIG =int(mConfig.get('NETWORK','udpportconfig'))
mTimeoutWiFi=int(mConfig.get('NETWORK','timeoutwifi'))
mRefreshDelay=int(mConfig.get('SETTINGS','refreshperiod'))
mTypeGRF=int(mConfig.get('SETTINGS','typegrf'))
mScale=int(mConfig.get('SETTINGS','scale'))
mRecDir=mConfig.get('RECORDS','recordsdirectory' )
mRecRatio=int(mConfig.get('RECORDS','recordratio'))



sockData=0
sockConfig=0
sockConfig2=0

mDisplayConnected=False
mIpAddr=""

mScreen=Afficheur()
mDataManager=DataManager()
mGraphManager=GraphManager()
def dessineGraph():
    mDuree=mScreen.getDuree(mScreen.getScale())
    mGraphManager.setDuree(mDuree)
    mGraphManager.fillGraph(mDataManager.getDataList(mDuree))
    mScreen.majTendance(mDataManager.getTendance())
    coordList=mGraphManager.getCoords()
    th_dessineGrf= threading.Thread(target=mScreen.traceGraphe,args=(coordList,))
    th_dessineGrf.start()
    #mScreen.traceGraphe(coordList)
    
mRecord=0
mScreen.setScale(mScale)
mScreen.setTypeGRF(mTypeGRF)
mGraphManager.setType(mTypeGRF)
mDataManager.initXML(mRecDir)
mGraphManager.initGraph(mScreen.getGraphSize())

mDuree=mScreen.getDuree(mScreen.getScale())
mGraphManager.setDuree(mDuree)



GPIO.setmode(GPIO.BCM)
btn_Pow=21
GPIO.setup(btn_Pow,GPIO.OUT,initial=GPIO.HIGH) #alim bouton
btn_ScaleUp=26
btn_ScaleDown=20
btn_GrfUp=19
btn_GrfDown=16
btn_Halt=13

GPIO.setup(btn_ScaleUp,GPIO.IN)
GPIO.setup(btn_ScaleDown,GPIO.IN)
GPIO.setup(btn_GrfUp,GPIO.IN)
GPIO.setup(btn_GrfDown,GPIO.IN)
GPIO.setup(btn_Halt,GPIO.IN)
bScaleUp=True
bScaleDown=True
bGrfUp=True
bGrfDown=True
bHalt=True

#Détection connections Boutons
bAliveScaleUp=GPIO.input(btn_ScaleUp)
bAliveScaleDown=GPIO.input(btn_ScaleDown)
bAliveGrfUp=GPIO.input(btn_GrfUp)
bAliveGrfDown=GPIO.input(btn_GrfDown)
bAliveHalt=GPIO.input(btn_Halt)

def connectionTest():
    bTest= False
    f = os.popen('ifconfig wlan0 | grep inet | cut -d: -f2')
    your_ip=f.read()
    s=your_ip.split(' ')
    IpAddr=""
    BdAddr=""
    if len(s)>1:
        IpAddr=s[9]
        BdAddr=s[15].replace('\n','')
        
        bTest=True
    else:
        print("Display not connected")
        bTest=False
        n=mTimeoutWiFi
        while n>0:
            print('Reconnection in ',n,'s')
            n-=1
            time.sleep(1)
    return (bTest,IpAddr,BdAddr)
    
def initSockets():

    global UDP_IP
    global UDP_PORT_CONFIG
    global UDP_PORT_DATA
    global mTimeoutWiFi
    global sockData
    global sockConfig
    global sockConfig2
    
    mConfig.read('configBaro.ini')
    UDP_IP=mConfig.get('NETWORK','broadcastaddress')
    UDP_PORT_DATA =int(mConfig.get('NETWORK','udpportdata'))
    UDP_PORT_CONFIG =int(mConfig.get('NETWORK','udpportconfig'))
    mTimeoutWiFi=int(mConfig.get('NETWORK','timeoutwifi'))
    
    sockData = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sockConfig = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sockConfig2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    
    sockData.bind((UDP_IP, UDP_PORT_DATA))
    sockData.setblocking(0)

    sockConfig.bind((mIpAddr, UDP_PORT_CONFIG))
    sockConfig.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sockConfig.setblocking(0)

    
    sockConfig2.bind(("255.255.255.255", UDP_PORT_CONFIG))
    sockConfig2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sockConfig2.setblocking(0)
    
def closeSockets():
    sockData.close()
    sockConfig.close()
    sockConfig2.close()
    
def stopProgram():
    mScreen.sleepScreen()
    GPIO.cleanup()
    closeSockets()


def on_ClickScale(up,scale):
    scale+=up
    if scale>8:
        scale=0
    elif scale<0:
        scale=8
    mConfig.set('SETTINGS', 'scale', str(scale))
    mConfig.write(open('configBaro.ini','w'))
    mScreen.setScale(scale)
    dessineGraph()
    return scale

def on_ClickGrf(up,grf):
    grf+=up
    if grf>2:
        grf=0
    elif grf<0:
        grf=2
    mConfig.set('SETTINGS', 'typegrf', str(grf))
    mConfig.write(open('configBaro.ini','w'))
    mScreen.setTypeGRF(grf)
    mGraphManager.setType(grf)
    mGraphManager.initGraph(mScreen.getGraphSize())
    dessineGraph() 
    return grf

        


while mDisplayConnected==False:
     (b,ip,bdAddr)=connectionTest()
     mDisplayConnected=b
     mIpAddr=ip
     if UDP_IP=="255.255.255.255":
        UDP_IP=bdAddr

print ("Diplay connected IpAddr:",mIpAddr)
print('UDP_IP:',UDP_IP)
print('UDP_PORT_DATA:',UDP_PORT_DATA)
print('UDP_PORT_CONFIG:',UDP_PORT_CONFIG)
initSockets()

pression=0.0
lastPression=0.0
temp=0.0
lastTemp=0.0
humidity=0.0
lastHumidity=0.0


mTimeStart=0
mTrame=""
mFirstData=True


try:
    mTimeStart=datetime.datetime.utcnow()
    # t1.join()
    # t2.join()
    sData=""
    s=""
    p=""
        
    while True:
        sockData.settimeout(0.02)
        bTrame1Recue=False
        bTrame2Recue=False
        try:
            data,addr= sockData.recvfrom(1024) # buffer size is 1024 bytes
            sData=("%s" %data)
            s=re.split(",",sData)
            bTrame1Recue=True
            
        except socket.timeout:
            pass
        
        sockConfig.settimeout(0.02)
        try:
            param,addr=sockConfig.recvfrom(1024) # buffer size is 1024 bytes
            sConfig=("%s" %param)
            p=re.split(",",sConfig)
            bTrame2Recue=True
        except socket.timeout:
            pass
        sockConfig2.settimeout(0.02)
        try:
            param,addr=sockConfig2.recvfrom(1024) # buffer size is 1024 bytes
            sConfig=("%s" %param)
            p=re.split(",",sConfig)
            bTrame2Recue=True
        except socket.timeout:
            pass
                    
                      
            
            
        if bTrame2Recue:
            if "$BARODISPLAY" in p[0]:
                if "getIpAddress" in p[1]:
                    sMsg=bytearray("$BARODISPLAY,IpAddress,"+mIpAddr+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,("255.255.255.255",UDP_PORT_CONFIG))
                if "getBroadcastAddress" in p[1]:
                    sMsg=bytearray("$BARODISPLAY,BroadcastAddress,"+UDP_IP+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                if "getUdpPort" in p[1]:
                    sMsg=bytearray("$BARODISPLAY,UdpPort,"+str(UDP_PORT_CONFIG)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                if "getUdpPortSec" in p[1]:
                    sMsg=bytearray("$BARODISPLAY,UdpPortSec,"+str(UDP_PORT_DATA)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                if "getTimeoutWiFi" in p[1]:
                    sMsg=bytearray("$BARODISPLAY,timeoutWiFi,"+str(mTimeoutWiFi)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                if "setBroadcastAddress" in p[1]:
                    UDP_IP=p[2]
                    mConfig.set('NETWORK', 'broadcastaddress', UDP_IP)
                    mConfig.write(open('configBaro.ini','w'))
                    closeSockets()
                    initSockets()
                    sMsg=bytearray("$BARODISPLAY,BroadcastAddress,"+UDP_IP+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                if "setUdpPort" in p[1]:
                    UDP_PORT_CONFIG=int(p[2])
                    mConfig.set('NETWORK', 'udpportconfig',str(UDP_PORT_CONFIG))
                    mConfig.write(open('configBaro.ini','w'))
                    closeSockets()
                    initSockets()
                    sMsg=bytearray("$BARODISPLAY,UdpPort,"+str(UDP_PORT_CONFIG)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                if "setUdpPortSec" in p[1]:
                    UDP_PORT_DATA=int(p[2])
                    mConfig.set('NETWORK', 'udpportdata',str(UDP_PORT_DATA))
                    mConfig.write(open('configBaro.ini','w'))
                    closeSockets()
                    initSockets()
                    sMsg=bytearray("$BARODISPLAY,UdpPortSec,"+str(UDP_PORT_DATA)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                if "setTimeoutWiFi" in p[1]:
                    mTimeoutWiFi=int(p[2])
                    mConfig.set('NETWORK', 'timeoutwifi', mTimeoutWiFi)
                    mConfig.write(open('configBaro.ini','w'))
                    sMsg=bytearray("$BARODISPLAY,timeoutWiFi,"+str(mTimeoutWiFi)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                if "getPeriod" in p[1]:
                    sMsg=bytearray("$BARODISPLAY,period,"+str(mRefreshDelay)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                if "setPeriod" in p[1]:
                    mRefreshDelay=int(p[2])
                    print(mRefreshDelay)
                    mConfig.set('SETTINGS', 'refreshperiod', str(mRefreshDelay))
                    #mConfig['SETTINGS']['refreshperiod']=str(mRefreshDelay)
                    mConfig.write(open('configBaro.ini','w'))
                    sMsg=bytearray("$BARODISPLAY,period,"+str(mRefreshDelay)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))
                
                if "getScale" in p[1]:
                    sMsg=bytearray("$BARODISPLAY,scale,"+str(mScreen.getScale())+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))

                if "setScale" in p[1]:
                    nScale= int(p[2])
                    mConfig.set('SETTINGS', 'scale', str(nScale))
                    mConfig.write(open('configBaro.ini','w'))
                    mScreen.setScale(nScale)
                    dessineGraph()                    
                    
                    
                if "getRecordRatio" in p[1]:
                    sMsg=bytearray("$BARODISPLAY,ratio,"+str(mRecRatio)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))

                if "setRecordRatio" in p[1]:
                    mRecRatio= int(p[2])
                    mConfig.set('RECORDS', 'recordratio', str(mRecRatio))
                    mConfig.write(open('configBaro.ini','w'))
                    
                if "getGrfType" in p[1]:
                    sMsg=bytearray("$BARODISPLAY,grfType,"+str(mTypeGRF)+",\r\n",'utf-8')
                    sockConfig.sendto(sMsg,(UDP_IP,UDP_PORT_CONFIG))

                if "setGrfType" in p[1]:
                    mTypeGRF= int(p[2])
                    mConfig.set('SETTINGS', 'typegrf', str(mTypeGRF))
                    mConfig.write(open('configBaro.ini','w'))
                    
                    mScreen.setTypeGRF(mTypeGRF)
                    mGraphManager.setType(mTypeGRF)
                    mGraphManager.initGraph(mScreen.getGraphSize())
                    dessineGraph()  
                                        
                if "refresh" in p[1]:
                    dessineGraph()  
                    
                if "shutdown" in p[1]:
                    stopProgram()
                    f = os.popen('sudo shutdown -h now')
                    
                    
                    
        if bTrame1Recue:
            if "$IIXDR" in s[0]:
                pression=float(s[2])
                temperature=round(float(s[6]),1)
                humidity=round(float(s[10]))
                pression=pression*1000
                pression=round(pression,1)
            
                print(datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")+"-> "+str(pression)+"HPa "+str(temperature)+"°C "+str(humidity)+"%")
                if pression!=lastPression :
                    mScreen.majPression(pression)
                    lastPression=pression
                if temperature!=lastTemp :
                    mScreen.majTemperature(temperature)
                    lastTemp=temperature
                if humidity!=lastHumidity :
                    mScreen.majHumidity(humidity)
                    lastHumidity=humidity
           
            
                date = datetime.datetime.utcnow() 
                data=UneData(pression,temperature,humidity,date)  
                
                if mRecord>=mRecRatio:
                    mRecord=0
                    mDataManager.addData(data)
                    
                mRecord+=1
                
                currentTime=date
                if mFirstData==True:
                    mFirstData=False
                    dessineGraph()  
                if (currentTime-mTimeStart).total_seconds()>mRefreshDelay:
                    mTimeStart=datetime.datetime.utcnow()   
                    dessineGraph()  
               
                
              
            
            
        if bAliveScaleUp:
            bScaleUp=GPIO.input(btn_ScaleUp)
            if not bScaleUp:           
                while not bScaleUp:
                    bScaleUp=GPIO.input(btn_ScaleUp)
                    time.sleep(0.02) 
                print("bouton ScaleUp")              
                mScale=on_ClickScale(1,mScale) 
                print(mScale)  
        
        if bAliveScaleDown:        
            bScaleDown=GPIO.input(btn_ScaleDown)
            if not bScaleDown:           
                while not bScaleDown:
                    bScaleDown=GPIO.input(btn_ScaleDown)
                    time.sleep(0.02) 
                print("bouton ScaleDown")                                
                mScale=on_ClickScale(-1,mScale)
                print(mScale)
                
        if bAliveGrfUp:
            bGrfUp=GPIO.input(btn_GrfUp)
            if not bGrfUp:           
                while not bGrfUp:
                    bGrfUp=GPIO.input(btn_GrfUp)
                    time.sleep(0.02) 
                print("bouton GrfUp")   
                mTypeGRF=on_ClickGrf(1,mTypeGRF) 
                print(mTypeGRF) 
        
        if bAliveGrfDown:
            bGrfDown=GPIO.input(btn_GrfDown)
            if not bGrfDown:           
                while not bGrfDown:
                    bGrfDown=GPIO.input(btn_GrfDown)
                    time.sleep(0.02) 
                print("bouton GrfDown")  
                mTypeGRF=on_ClickGrf(-1,mTypeGRF)
                print(mTypeGRF)    
                
        if bAliveHalt:    
            bHalt=GPIO.input(btn_Halt)
            if not bHalt:           
                while not bHalt:
                    bHalt=GPIO.input(btn_Halt)
                    time.sleep(0.02) 
                print("bouton Halt")           
                stopProgram()
                f = os.popen('sudo shutdown -h now')

#except:
except KeyboardInterrupt:    
    stopProgram()
    print("\n Programme interrompu")
        

    

