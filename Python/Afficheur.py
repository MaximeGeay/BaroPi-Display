#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import collections
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
#print(libdir)
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd4in2

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
#import imagedata

import time

EPD_WIDTH = 400
EPD_HEIGHT = 300

COLORED=0
UNCOLORED=255

AXES_OFFSET_Hor=32
AXES_OFFSET_Ver=20

Xo=AXES_OFFSET_Hor
Yo=EPD_HEIGHT-AXES_OFFSET_Ver
Xf=EPD_WIDTH
Yf=AXES_OFFSET_Hor


Coords=collections.namedtuple('Coords',['x0','y0','x1','y1'])
zoneDataPression=Coords(8,1,64,25)  #X découpé par 8 pixels
zoneUnitPression=Coords(67,1,100,25)
zoneDataTend=Coords(150,1,220,25)
zoneDataTemp=Coords(296,1,336,25)
zoneUnitTemp=Coords(337,1,345,25)
zoneDataHum=Coords(352,1,376,25)
zoneUnitHum=Coords(380,1,400,25)




Font10  = ImageFont.truetype('/usr/share/fonts/Ubuntu-L.ttf', 10)
FontData  = ImageFont.truetype('/usr/share/fonts/Ubuntu-B.ttf', 18)
Font24  = ImageFont.truetype('/usr/share/fonts/Ubuntu-B.ttf', 24)



#mImage=Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1) # 1: clear the frame draw = ImageDraw.Draw(image)
#mDraw=ImageDraw.Draw(mImage)


class Afficheur(object):

    def __init__(self):
        self.epd = epd4in2.EPD()
        self.mScale=1 #0=1h 1=3h 2=6h 3=12h 4=24h 5=48h 6=72h 7=96h 8=120h 
        self.pression=0.0
        self.temperature=0.0
        self.humidity=0.0
        self.tendance=()
        self.durees=[1,3,6,12,24,48,72,96,120]
        self.typeGRF=0
        self.initScreen()
        self.clearScreen()
        self.drawAxes()
        self.epd.display(self.epd.getbuffer(self.mImage))
        
        
    def getGraphSize(self):
        #def initGraph(self,xSize,ySize,yMin,yMax):
        xSize=Xf-Xo
        ySize=Yo-Yf
        yMin=960
        yMax=1040
        if self.typeGRF==0: 
            yMin=960
            yMax=1040
        elif self.typeGRF==1: 
            yMin=-5
            yMax=45
        elif self.typeGRF==2: 
            yMin=0
            yMax=100
            
        return [xSize,ySize,yMin,yMax]
    
    def getScale(self):
        return self.mScale
    
    def setScale(self,scale):
        self.mScale=scale
                
    def getDuree(self,scale):
        duree=int(self.durees[int(scale)])
        return self.durees[scale]
    
    def setTypeGRF(self, typeGRF):
        self.typeGRF=typeGRF
        self.drawAxes()
        
    def getTypeGRF(self):
        return self.typeGRF
        

    def initScreen(self):      
        self.epd.init()
        image = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1) # 1: clear the frame draw = ImageDraw.Draw(image)
        draw = ImageDraw.Draw(image)
        #font  = ImageFont.truetype('/usr/share/fonts/Ubuntu-B.ttf', 24)
        draw.text((130, 140), 'Barographe', font = Font24, fill = COLORED) 
        self.epd.display(self.epd.getbuffer(image))
        #epd.display(epd.getbuffer(Himage))
        #time.sleep(1)
    
    def tire(self,draw,y):
        d = Xo
        while d < Xf:
            draw.line((d,y,d+5,y),fill=COLORED)
            draw.line((d+5,y,d+25,y),fill=UNCOLORED)
            d += 25
   
    def ticks(self,draw,scale):
        
        #0=1h 1=3h 2=6h 3=12h 4=24h 5=48h 6=72h 7=96h 8=120h
        if scale==0:
            draw.text((Xo-5,Yo+5), '-1h', font = Font10, fill = COLORED) 
            x=Xo+(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-40min', font = Font10, fill = COLORED) 
        
            x=Xo+2*(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-20min', font = Font10, fill = COLORED) 
        
            x=Xf
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
        
        if scale==1:
            draw.text((Xo-5,Yo+5), '-3h', font = Font10, fill = COLORED) 
            x=Xo+(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-2h', font = Font10, fill = COLORED) 
        
            x=Xo+2*(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-1h', font = Font10, fill = COLORED) 
        
            x=Xf
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            
        if scale==2:
            draw.text((Xo-5,Yo+5), '-6h', font = Font10, fill = COLORED) 
            x=Xo+(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-4h', font = Font10, fill = COLORED) 
        
            x=Xo+2*(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-2h', font = Font10, fill = COLORED) 
        
            x=Xf
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            
        if scale == 3:
            draw.text((Xo-5,Yo+5), '-12h', font = Font10, fill = COLORED) 
            x=Xo+(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-8h', font = Font10, fill = COLORED) 
        
            x=Xo+2*(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-4h', font = Font10, fill = COLORED) 
        
            x=Xf
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            
        if scale == 4:
            draw.text((Xo-5,Yo+5), '-24h', font = Font10, fill = COLORED) 
            
            x=Xo+(Xf-Xo)/4
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-18h', font = Font10, fill = COLORED) 
            
            x=Xo+2*(Xf-Xo)/4
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-12h', font = Font10, fill = COLORED) 
        
            x=Xo+3*(Xf-Xo)/4
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-6h', font = Font10, fill = COLORED) 
        
            x=Xf
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            
        if scale==5:
            draw.text((Xo-5,Yo+5), '-2j', font = Font10, fill = COLORED) 
            
            x=Xo+(Xf-Xo)/4
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-36h', font = Font10, fill = COLORED) 
            
            x=Xo+2*(Xf-Xo)/4
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-24h', font = Font10, fill = COLORED) 
        
            x=Xo+3*(Xf-Xo)/4
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-12h', font = Font10, fill = COLORED) 
        
            x=Xf
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            
        if scale==6:
            draw.text((Xo-5,Yo+5), '-3j', font = Font10, fill = COLORED) 
            x=Xo+(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-2j', font = Font10, fill = COLORED) 
        
            x=Xo+2*(Xf-Xo)/3
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-1j', font = Font10, fill = COLORED) 
        
            x=Xf
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            
        if scale==7:
            draw.text((Xo-5,Yo+5), '-4j', font = Font10, fill = COLORED) 
            
            x=Xo+(Xf-Xo)/4
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-3j', font = Font10, fill = COLORED) 
            
            x=Xo+2*(Xf-Xo)/4
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-2j', font = Font10, fill = COLORED) 
        
            x=Xo+3*(Xf-Xo)/4
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-1j', font = Font10, fill = COLORED) 
        
            x=Xf
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            
        if scale==8:
            draw.text((Xo-5,Yo+5), '-5j', font = Font10, fill = COLORED) 
            
            x=Xo+(Xf-Xo)/5
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-4j', font = Font10, fill = COLORED) 
            
            x=Xo+2*(Xf-Xo)/5
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-3j', font = Font10, fill = COLORED) 
        
            x=Xo+3*(Xf-Xo)/5
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-2j', font = Font10, fill = COLORED)
            
            x=Xo+4*(Xf-Xo)/5
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
            draw.text((x-5,Yo+5), '-1j', font = Font10, fill = COLORED)
        
            x=Xf
            draw.line((x,Yo,x,Yo-5),fill=COLORED)
        
            
         
    
    def drawAxes(self):
    
        # For simplicity, the arguments are explicit numerical coordinates
        #image = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1) # 1: clear the frame draw = ImageDraw.Draw(image)
        #draw = ImageDraw.Draw(image)
        
        self.mDraw.line((Xo,Yo,Xf,Yo), fill=COLORED)
        self.mDraw.line((Xo,Yo,Xo,Yf),fill=COLORED)
        
        if self.typeGRF==0:
        
            self.tire(self.mDraw,Yo-Yo/9) #970
            self.tire(self.mDraw,Yo-2*(Yo/9)) #980
            self.tire(self.mDraw,Yo-3*(Yo/9)) #990
            self.tire(self.mDraw,Yo-4*(Yo/9)) #1000
            self.tire(self.mDraw,Yo-5*(Yo/9)) #1010
            self.tire(self.mDraw,Yo-6*(Yo/9)) #1020
            self.tire(self.mDraw,Yo-7*(Yo/9)) #1030
            self.tire(self.mDraw,Yo-8*(Yo/9)) #1040
    
        
            self.mDraw.text((7, Yo-5), '960', font = Font10, fill = COLORED) 
            self.mDraw.text((7, Yo-5-Yo/9), '970', font = Font10, fill = COLORED) 
            self.mDraw.text((7, Yo-5-2*(Yo/9)), '980', font = Font10, fill = COLORED) 
            self.mDraw.text((7, Yo-5-3*(Yo/9)), '990', font = Font10, fill = COLORED) 
            self.mDraw.text((3, Yo-5-4*(Yo/9)), '1000', font = Font10, fill = COLORED) 
            self.mDraw.text((3, Yo-5-5*(Yo/9)), '1010', font = Font10, fill = COLORED) 
            self.mDraw.text((3, Yo-5-6*(Yo/9)), '1020', font = Font10, fill = COLORED) 
            self.mDraw.text((3, Yo-5-7*(Yo/9)), '1030', font = Font10, fill = COLORED) 
            self.mDraw.text((3, Yo-5-8*(Yo/9)), '1040', font = Font10, fill = COLORED)
            
        elif self.typeGRF==1:
            self.tire(self.mDraw,Yo-Yo/6) #5
            self.tire(self.mDraw,Yo-2*(Yo/6)) #15
            self.tire(self.mDraw,Yo-3*(Yo/6)) #25
            self.tire(self.mDraw,Yo-4*(Yo/6)) #35
            self.tire(self.mDraw,Yo-5*(Yo/6)) #45
            
            self.mDraw.text((9, Yo-5), '-5°', font = Font10, fill = COLORED) 
            self.mDraw.text((11, Yo-5-Yo/6), '5°', font = Font10, fill = COLORED) 
            self.mDraw.text((9, Yo-5-2*(Yo/6)), '15°', font = Font10, fill = COLORED) 
            self.mDraw.text((9, Yo-5-3*(Yo/6)), '25°', font = Font10, fill = COLORED) 
            self.mDraw.text((9, Yo-5-4*(Yo/6)), '35°', font = Font10, fill = COLORED)
            self.mDraw.text((9, Yo-5-5*(Yo/6)), '45°', font = Font10, fill = COLORED) 
            
        elif self.typeGRF==2:
            self.tire(self.mDraw,Yo-Yo/6) #20
            self.tire(self.mDraw,Yo-2*(Yo/6)) #40
            self.tire(self.mDraw,Yo-3*(Yo/6)) #60
            self.tire(self.mDraw,Yo-4*(Yo/6)) #80
            self.tire(self.mDraw,Yo-5*(Yo/6)) #100
            
            self.mDraw.text((7, Yo-5), '0', font = Font10, fill = COLORED) 
            self.mDraw.text((7, Yo-5-Yo/6), '20', font = Font10, fill = COLORED) 
            self.mDraw.text((7, Yo-5-2*(Yo/6)), '40', font = Font10, fill = COLORED) 
            self.mDraw.text((7, Yo-5-3*(Yo/6)), '60', font = Font10, fill = COLORED) 
            self.mDraw.text((7, Yo-5-4*(Yo/6)), '80', font = Font10, fill = COLORED)
            self.mDraw.text((7, Yo-5-5*(Yo/6)), '100', font = Font10, fill = COLORED) 
            
    
        self.ticks(self.mDraw,self.mScale)
        self.mDraw.text((zoneUnitPression.x0,zoneUnitPression.y0),'HPa',font=FontData,fill=COLORED)
        self.mDraw.text((zoneUnitTemp.x0,zoneUnitTemp.y0),'°',font=FontData,fill=COLORED)
        self.mDraw.text((zoneUnitHum.x0,zoneUnitHum.y0),'%',font=FontData,fill=COLORED)
        
   
    
    def majData(self,press,temp,hum):

        majPression(press)
        majTemperature(temp)
        majHumidity(hum)
        
    
    def majPression(self,press):
    
        press=round(press,1)
        self.pression=press
       
        self.mDraw.rectangle(zoneDataPression, outline = COLORED, fill = COLORED)
        self.mDraw.text((zoneDataPression.x0,zoneDataPression.y0),str(press),font = FontData, fill = UNCOLORED)
       #self.epd.EPD_4IN2_PartialDisplay(zoneDataPression.x0,zoneDataPression.y0,zoneDataPression.x1,zoneDataPression.y1,self.epd.getbuffer(self.mImage))
     
    def majTemperature(self,temp):
        temp=round(temp,1)
        self.temperature=temp
        self.mDraw.rectangle(zoneDataTemp, outline = COLORED, fill = COLORED)
        self.mDraw.text((zoneDataTemp.x0,zoneDataTemp.y0),str(temp),font = FontData, fill = UNCOLORED)
       # self.epd.EPD_4IN2_PartialDisplay(zoneDataTemp.x0,zoneDataTemp.y0,zoneDataTemp.x1,zoneDataTemp.y1,self.epd.getbuffer(self.mImage))
       
    def majHumidity(self,hum):
        hum=round(hum)
        self.humidity=hum
        self.mDraw.rectangle(zoneDataHum, outline = COLORED, fill = COLORED)
        self.mDraw.text((zoneDataHum.x0,zoneDataHum.y0),str(hum),font = FontData, fill = UNCOLORED)
       # self.epd.EPD_4IN2_PartialDisplay(zoneDataHum.x0,zoneDataHum.y0,zoneDataHum.x1,zoneDataHum.y1,self.epd.getbuffer(self.mImage))
    
    def majTendance(self,tendance):
        self.tendance=tendance
  
    def clearScreen(self):
        self.mImage = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255) # 1: clear the frame draw = ImageDraw.Draw(image)
        self.mDraw = ImageDraw.Draw(self.mImage) # 1: clear the frame draw = ImageDraw.Draw(image)
    
    
        
    def traceGraphe(self,listPoints):
        self.clearScreen()
        self.drawAxes()
        self.mDraw.text((zoneDataPression.x0,zoneDataPression.y0),str(self.pression),font = FontData, fill = COLORED)
        self.mDraw.text((zoneDataTend.x0,zoneDataTend.y0),self.tendance[self.typeGRF],font = FontData, fill = COLORED)
        self.mDraw.text((zoneDataTemp.x0,zoneDataTemp.y0),str(self.temperature),font = FontData, fill = COLORED)
        self.mDraw.text((zoneDataHum.x0,zoneDataHum.y0),str(self.humidity),font = FontData, fill = COLORED)
        

        for point in listPoints:
            self.mDraw.point((Xf-point[0],Yo-point[1]))
            self.mDraw.point((Xf-point[0],Yo-point[1]+1))
            self.mDraw.point((Xf-point[0],Yo-point[1]-1))
 
        self.epd.display(self.epd.getbuffer(self.mImage))
        
        
    def sleepScreen(self):
        self.initScreen()
        self.epd.sleep()
        

 


