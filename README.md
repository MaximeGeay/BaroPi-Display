# BaroPi-Display
Afficheur Barographe basé sur un RPi3 et e-ink screen EPD 4in2 pour le capteur BaroWiFi-Arduino

L'ensemble est paramétrable via le logiciel BaroWiFI-GUI

Le script python à lancer est baro_tr.py

Sur le schéma, il y également un GPS Adafruit ultimate GPS et une horloge RTC.
Il est important que le raspberry soit à l'heure pour l'archivage et l'affichage des données baromètre.
Le GPS permet de créer un serveur ntp en cas d'une utilisation hors connexion
