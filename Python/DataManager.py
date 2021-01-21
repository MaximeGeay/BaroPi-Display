#!/usr/bin/python3
# -*- coding:utf-8 -*-

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import datetime
import os

class XMLWriter(object):
    def __init__(self):
        self.dirPath=""
        self.ns = {"n1": "http://cqt.barographe.fr/Datas"}
        ET.register_namespace('n1', self.ns["n1"])
        self.root = ET.Element(ET.QName(self.ns["n1"], "Datas"))
        self.dhInit=datetime.datetime.utcnow()
        self.tree=''
        self.absPath=""
        
    def createXML(self,sPath):
        self.dirPath=sPath
        self.dhInit=datetime.datetime.utcnow()
        self.absPath=sPath+"Baro_"+self.dhInit.strftime("%Y%m%d")+".xml"

        try:
            with open(self.absPath): pass
        except IOError:
            ET.ElementTree(self.root).write(self.absPath,xml_declaration=True, encoding='UTF-8')
            
        self.tree = ET.parse(self.absPath)
        self.root=self.tree.getroot()

    def addData(self,data):
            dDatas=dict()
            dDatas["Pression"]=str(round(data.press,1))
            dDatas["Temperature"]=str(round(data.temp,1))
            dDatas["Humidity"]=str(round(data.hum,1))
            dDatas["DateHeure"]=data.dateheure.strftime("%d/%m/%Y %H:%M:%S")
            e=ET.SubElement(self.root,'Mesure',attrib=dDatas)
            e.tail="\n\t"
            self.tree.write(self.absPath,xml_declaration=True, encoding='UTF-8')
            
    def getDateFichier(self):
        return self.dhInit
        
    def getDataInFile(self,dhDebut,sPath):
        doc = minidom.parse(sPath)
        dataList = doc.getElementsByTagName('Mesure')

        mesuresList=[]
        n=0
        i=0
        for mesure in dataList:
            dhMesure=datetime.datetime.strptime(mesure.getAttribute('DateHeure'),"%d/%m/%Y %H:%M:%S")
            n+=1
            
            if dhMesure>dhDebut:
                i+=1
                pression=float(mesure.getAttribute('Pression'))
                date=dhMesure
                temperature=float(mesure.getAttribute('Temperature'))
                humidity=float(mesure.getAttribute('Humidity'))
                data=UneData(pression,temperature,humidity,date) 
                mesuresList.append(data)
   
        return mesuresList
        
    def getData(self,dhDebut):
    
        dateNow=datetime.datetime.utcnow()
        delta=dateNow-dhDebut
        nbFile=delta.days+1               
        mesuresList=[]
        
        while nbFile>0:
            nbFile=nbFile-1
            dateFic=dateNow-datetime.timedelta(days=nbFile)
            sFic=self.dirPath+"Baro_"+dateFic.strftime("%Y%m%d")+".xml"
            
            if os.path.isfile(sFic):
                mesuresList=mesuresList+self.getDataInFile(dhDebut,sFic)
                
        return mesuresList
        
    
    


class UneData(object):
    __slots__=['press','temp','hum','dateheure']
    
    def __init__(self,press=0,temp=0,hum=0,dateheure=datetime.datetime.utcnow()):
        self.press=press
        self.temp=temp
        self.hum=hum
        self.dateheure=dateheure
        
        

class DataManager(object):
    def __init__(self):
        self.dataList=[]
        #self.lastData=UneData()
        self.writer=XMLWriter()
        self.tendance=() #tuple 0=pression 1=temperature 2=humidity
    
    def initXML(self,sPath):
        self.dirPath=sPath
        try: 
            os.makedirs(sPath)
        except OSError:
            if not os.path.isdir(sPath):
                Raise
        
        self.writer.createXML(sPath)
        
    
    def addData(self,data):
        dateNow=datetime.datetime.utcnow().date()
        dateFic=self.writer.getDateFichier()
        if dateNow!=dateFic.date():
            self.writer.createXML(self.dirPath)
        self.UneData=data
        #self.dataList.append(self.UneData)
        self.writer.addData(self.UneData)
        
    def calculTendance(self):
        if len(self.dataList)==0:
            return
        debutData=self.dataList[len(self.dataList)-1].dateheure-self.dataList[0].dateheure
        dhToFind=datetime.datetime.utcnow()
        duree=0
        tendPress=""
        tendTemp=""
        tendHum=""
        if debutData.seconds >= (3*3600-60) or debutData.days>0:
            dh1=self.dataList[len(self.dataList)-1].dateheure-datetime.timedelta(seconds=(3*3600-60))
            dhToFind=dh1
            dataDeb=self.findDataAt(dhToFind)
            if dataDeb.press>0:
                duree=3
                print("DateToFind "+dhToFind.strftime("%d/%m/%Y %H:%M:%S"))
                print("DataFound "+str(duree)+" Date "+dataDeb.dateheure.strftime("%d/%m/%Y %H:%M:%S")+" Pression "+str(dataDeb.press))
        elif debutData.seconds>=(3600-60):  
            dh2=self.dataList[len(self.dataList)-1].dateheure-datetime.timedelta(seconds=(3600-60))
            dhToFind=dh2
            dataDeb=self.findDataAt(dhToFind)
            if dataDeb.press>0:
                duree=1
                print("DateToFind "+dhToFind.strftime("%d/%m/%Y %H:%M:%S"))
                print("DataFound "+str(duree)+" Date "+dataDeb.dateheure.strftime("%d/%m/%Y %H:%M:%S")+" Pression "+str(dataDeb.press))
        else:
            dataDeb=UneData()
        
        if duree>0:
            press1=dataDeb.press
            press2=self.dataList[len(self.dataList)-1].press
            temp1=dataDeb.temp
            temp2=self.dataList[len(self.dataList)-1].temp
            hum1=dataDeb.hum
            hum2=self.dataList[len(self.dataList)-1].hum
            
            
            dTend=round((press2-press1),1)
            if dTend<0:
                tendPress=str(dTend)+" HPa"
            else:
                tendPress="+"+str(dTend)+" HPa"
                
            dTend=round((temp2-temp1),1)
            if dTend<0:
                tendTemp=str(dTend)+" °"
            else:
                tendTemp="+"+str(dTend)+" °"
                
            dTend=round((hum2-hum1),1)
            if dTend<0:
                tendHum=str(dTend)+" %"
            else:
                tendHum="+"+str(dTend)+" %"
                
            
            tendPress=tendPress+" /"+str(duree)+"h"
            tendTemp=tendTemp+" /"+str(duree)+"h"
            tendHum=tendHum+" /"+str(duree)+"h"           
        
        self.tendance=tendPress,tendTemp,tendHum
        
        
        
        
    def getDataList(self,duree):
        dateFin=datetime.datetime.utcnow()
        dateDeb=dateFin-datetime.timedelta(hours=duree)
       
        self.dataList=self.writer.getData(dateDeb)
        self.calculTendance()
        
        return self.dataList
    
    def getTendance(self):
        return self.tendance
    
    
            
            
    def findDataAt(self,dhToFind):       
        dataPrec=self.dataList[len(self.dataList)-1]
        dataFound=UneData()   
        if self.dataList[0].dateheure>dhToFind:
            return dataFound
   
        for data in reversed(self.dataList):
            if data.dateheure<=dhToFind and dataPrec.dateheure>=dhToFind:
                delta1=dhToFind-data.dateheure
                delta2=dataPrec.dateheure-dhToFind
                if delta1>delta2:
                    dataFound=dataPrec
                else:
                    dataFound=data
                delta3=dhToFind-dataFound.dateheure
                if delta3.days==-1:
                    delta3=dataFound.dateheure-dhToFind
                if delta3.seconds>600:
                    print("Trop d'écart entre la date recherchée "+dhToFind.strftime("%d/%m/%Y %H:%M:%S")+" et la date trouvée "+dataFound.dateheure.strftime("%d/%m/%Y %H:%M:%S"))
                    print("Delta "+str(delta3.seconds)+" "+str(delta3.days))
                    dataFound=UneData()
                break
            
            dataPrec=data
            
        return dataFound
        
        
   
        
