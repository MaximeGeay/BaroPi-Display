#!/usr/bin/python3
# -*- coding:utf-8 -*-

import datetime
from datetime import timedelta

# class UneDataGraph(object):
    # __slots__=['press','dateheure']
    
    # def __init__(self,press=0,dateheure=0):
        # self.press=press
        # self.dateheure=dateheure



class GraphManager(object):
    def __init__(self):
        self.graphXSize=368
        self.graphYSize=248 #300-20-32
        self.graphMinY=960
        self.graphMaxY=1040
        self.duree=3 #en heures
        self.graphCoord=[]
        self.graphData=[]
        self.graphType=0

        
    def initGraph(self,graphSize):
        self.graphXSize=graphSize[0]
        self.graphYSize=graphSize[1]
        self.graphMinY=graphSize[2]
        self.graphMaxY=graphSize[3]
        
    def setDuree(self,duree):
        self.duree=duree
        
    def setType(self,grfType):
        self.graphType=grfType

    def fillGraph(self,datalist):
        self.graphCoord=[]
        dateFin=datetime.datetime.utcnow()
        dateDeb=dateFin-datetime.timedelta(hours=self.duree)
        x=0.0
        y=0.0
        
        for data in datalist:         
            deltaT=(dateFin-data.dateheure).total_seconds()
            deltaTotal=(dateFin-dateDeb).total_seconds()
            x=deltaT*self.graphXSize/deltaTotal
            if self.graphType==0:
                y=(data.press-self.graphMinY)*self.graphYSize/(self.graphMaxY-self.graphMinY)
            elif self.graphType==1:
                y=(data.temp-self.graphMinY)*self.graphYSize/(self.graphMaxY-self.graphMinY)
            elif self.graphType==2:
                y=(data.hum-self.graphMinY)*self.graphYSize/(self.graphMaxY-self.graphMinY)
            x=round(x)
            y=round(y)
            bExist=0
            if x<self.graphXSize:
                for xy in self.graphCoord:
                    if xy[0]==x:
                        bExist=1
                        break
                if bExist==0:              
                    self.graphCoord.append([x,y])
            
        

    def getCoords(self):
        return self.graphCoord
    
        
        
        
        
