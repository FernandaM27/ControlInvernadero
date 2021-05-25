from tkinter import *
from tkinter import ttk, font
import mysql.connector
from mysql.connector import Error
import serial
import time
import datetime

arduino = serial.Serial('COM6', 9600, timeout = 1)

autoFoco = True
autoRegado = True
autoAlarma = True

def lecturaArduino():
    global inicioAC
    global finA
    global mydb
    data = arduino.readline()[:-2]
    if data:
        data = data.decode("utf-8")
        print(data)
        if data == "MOV":
            lbEstadoAlarma.configure(text="ENCENDIDO")
            lbEstadoAlarma.configure(background="green")
            lbEstadoAspersor.configure(text="APAGADO")
            lbEstadoAspersor.configure(background="red")
        elif data == "MOVOFF":
            lbEstadoAlarma.configure(text="APAGADO")
            lbEstadoAlarma.configure(background="red")
        elif data == "LOW":
            lbEstadoFoco.configure(text="APAGADO")
            lbEstadoFoco.configure(background="red")
        elif data == "HIGH":
            lbEstadoFoco.configure(text="ENCEDIDO")
            lbEstadoFoco.configure(background="green")
        elif data == "REGANDO":
            lbEstadoAspersor.configure(text="ENCEDIDO")
            lbEstadoAspersor.configure(background="green")
        elif data == "ROFF":
            lbEstadoAspersor.configure(text="APAGADO")
            lbEstadoAspersor.configure(background="red")
        else:
            lbHumedad.configure(text=data)

    monitor.after(100, lecturaArduino)        

try:
    # Se conecta con la base de datos.
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sesamo",
        database="casainteligente"
    )
    if mydb.is_connected():
        print("Conexion exitosa")
        cursor = mydb.cursor()
        cursor.execute("SELECT database();")
        registro=cursor.fetchone()
        print("Conectado a la BD", registro)
except Error as ex:
    print("Error durante la conexion", ex)

# Se crean las variables para obtener el periodo se uso del AC en modo automatico.
inicioAC = 0.0
finAC = 0.0

def onOffFoco():  
    global autoFoco     
    if(autoFoco):
        arduino.write(("LOFF").encode())
        autoFoco = False
    else:
        arduino.write(("LON").encode())    
        autoFoco=True

def focoAuto():       
    arduino.write(("LAU").encode())

def onOffRegado():  
    global autoRegado     
    if(autoRegado):
        arduino.write(("ROFF").encode())
        autoRegado = False
    else:
        arduino.write(("RON").encode())    
        autoRegado=True

def regadoAuto():  
    global autoRegado     
    arduino.write(("RAU").encode())

def onOffAlarma():  
    global autoAlarma     
    if(autoAlarma):
        print()
        arduino.write(b'AOFF')
        autoAlarma = False
    else:
        arduino.write(b'AON')    
        autoAlarma=True

# Se crea la pantalla con su titulo
monitor = Tk()
monitor.title("Control del riego")
# Cambia el formato de la fuente actual a negrita
fuente = font.Font(weight='bold')

# Define las etiquetas, marcos, botonoes y el slider
# Titulo que se muestra
etiqTitulo = ttk.Label(monitor, text="Monitoreo de riego", font=fuente)

# Marco del Manejo de estados
marcoD = ttk.Frame(monitor, borderwidth=2, relief="raised", padding=(10,10))
marcoD.grid(column=0, row=1, rowspan=2)


lbTituloF1 = ttk.Label(marcoD, text="Control de riego", font=fuente)
lbTituloF1.grid(column=0, row=0, columnspan=3)

#Aspersor
lbAspersor = ttk.Label(marcoD, text="Aspersor: ", font=fuente)
lbAspersor.grid(column=0, row=1)

lbEstadoAspersor = ttk.Label(marcoD, text="Apagado", font=fuente, background="red")
lbEstadoAspersor.grid(column=2, row=1, columnspan=2)

OnOffAspersorButton = ttk.Button(marcoD, text="On/Off", command=onOffRegado)
OnOffAspersorButton.grid(column=5, row=1)

cambioEstadoAspersorButton = ttk.Button(marcoD, text="AUTO", command=regadoAuto)
cambioEstadoAspersorButton.grid(column=6, row=1)

#Foco
lbFoco = ttk.Label(marcoD, text="Foco: ", font=fuente)
lbFoco.grid(column=0, row=2)

lbEstadoFoco = ttk.Label(marcoD, text="Apagado", font=fuente, background="red")
lbEstadoFoco.grid(column=2, row=2, columnspan=2)

OnOffFocoButton = ttk.Button(marcoD, text="On/Off", command=onOffFoco)
OnOffFocoButton.grid(column=5, row=2)

cambioEstadoFocoButton = ttk.Button(marcoD, text="AUTO", command=focoAuto)
cambioEstadoFocoButton.grid(column=6, row=2)

#Alarma
lbAlarma = ttk.Label(marcoD, text="Alarma: ", font=fuente)
lbAlarma.grid(column=0, row=3)

lbEstadoAlarma = ttk.Label(marcoD, text="APAGADO", font=fuente, background="red")
lbEstadoAlarma.grid(column=2, row=3, columnspan=2)

OnOffAlarmaButton = ttk.Button(marcoD, text="Off", command=onOffAlarma)
OnOffAlarmaButton.grid(column=5, row=3)

lbEstadoSuelo = ttk.Label(marcoD, text="Estado Suelo", font=fuente)
lbEstadoSuelo.grid(column=0, row=7, columnspan=2)

lbHumedad = ttk.Label(marcoD, text="0", font=fuente)
lbHumedad.grid(column=4, row=7, columnspan=2)

lecturaArduino()

monitor.mainloop()