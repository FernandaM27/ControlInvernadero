from tkinter import *
from tkinter import ttk, font
import mysql.connector
from mysql.connector import Error
import serial
import time
import datetime



arduino = serial.Serial('COM3', 9600, timeout = 1)

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sesamo",
        database="invernadero"
    )
    if mydb.is_connected():
        print("Conexion exitosa")
        cursor = mydb.cursor()
        cursor.execute("SELECT database();")
        registro=cursor.fetchone()
        print("Conectado a la BD", registro)
except Error as ex:
    print("Error durante la conexion", ex)

autoFoco = True
autoRegado = True
autoAlarma = True
cantidadAlarmas = 0
horaInicio = time.time()
promedioHora = 0.0
cont = 0
suma = 0
ultimaHumedad = 0

def lecturaArduino():
    global inicioAC
    global finA
    global mydb
    global cantidadAlarmas
    global horaInicio 
    global promedioHora 
    global cont 
    global suma
    global ultimaHumedad
    data = arduino.readline()[:-2]
    if data:
        data = data.decode("utf-8")
        print(data)
        
        tiempoActual = time.time()
        timestamp = datetime.datetime.fromtimestamp(tiempoActual).strftime('%Y-%m-%d %H:%M:%S')

        if data == "MOV":
            lbEstadoAlarma.configure(text="ENCENDIDO")
            lbEstadoAlarma.configure(foreground="green")
            lbEstadoAspersor.configure(text="APAGADO")
            lbEstadoAspersor.configure(foreground="red")

            cantidadAlarmas += 1
            lbCantidadAlarmasDetectadas.configure(text=str(cantidadAlarmas))
            lbUltimaFechaAlarma.configure(text = timestamp)

            cursor = mydb.cursor()
            cursor.execute("INSERT INTO `invernadero`.`alarma` (`hinicio`, `fecha`) VALUES ('"+ timestamp +"', '"+ timestamp +"');")
            mydb.commit()
            cursor.close()

        elif data == "MOVOFF":
            lbEstadoAlarma.configure(text="APAGADO")
            lbEstadoAlarma.configure(foreground="red")

        elif data == "LOW":
            lbEstadoFoco.configure(text="APAGADO")
            lbEstadoFoco.configure(foreground="red")

        elif data == "HIGH":
            lbEstadoFoco.configure(text="ENCEDIDO")
            lbEstadoFoco.configure(foreground="green")

        elif data == "REGANDO":
            lbEstadoAspersor.configure(text="ENCEDIDO")
            lbEstadoAspersor.configure(foreground="green")
        
        elif data == "RON":
            lbEstadoAspersor.configure(text="ENCEDIDO")
            lbEstadoAspersor.configure(foreground="green")

        elif data == "ROFF":
            lbEstadoAspersor.configure(text="APAGADO")
            lbEstadoAspersor.configure(foreground="red")

            lbUltimaFechaRiego.configure(text=timestamp)
            # Guardar en la bd
            cursor = mydb.cursor()
            cursor.execute("INSERT INTO `invernadero`.`riego` (`valor`, `fecha`) VALUES ('"+str(ultimaHumedad)+"', '"+ timestamp +"');")
            mydb.commit()
            cursor.close()
        
        elif data == "AOFF":
            lbEstadoAlarma.configure(text="APAGADO")
            lbEstadoAlarma.configure(foreground="red")
        
        elif data == "AON":
            lbEstadoAlarma.configure(text="APAGADO")
            lbEstadoAlarma.configure(foreground="red")
        else:
            ultimaHumedad = int(data)
            cont += 1
            suma = suma + ultimaHumedad
            promedioHora = suma/cont
            lbPromedio.configure(text = "{:.4f}".format(promedioHora))
            if tiempoActual-horaInicio>1800:
                cursor = mydb.cursor()
                cursor.execute("INSERT INTO `invernadero`.`humedad` (`valor`, `fecha`, `hora`) VALUES ('"+str(promedioHora)+"', '"+ timestamp +"', '"+ timestamp +"');")
                mydb.commit()
                cursor.close()
                suma = 0
                promedioHora = 0.0
                horaInicio = tiempoActual
            lbHumedad.configure(text=data)
            mostrarEnProgress(ultimaHumedad)   

    monitor.after(100, lecturaArduino)        

def mostrarEnProgress(valor):
    if valor <= 341:
        bar['value'] = 33  
        lbEstadoAspersor.configure(text="APAGADO")
        lbEstadoAspersor.configure(foreground="red")   
    if valor >= 682 and valor <= 800:
        bar['value'] = 66
    if valor >= 801:
        bar['value'] = 100    
    marcoD.update_idletasks()

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
monitor.title("Control de Invernadero")
# Cambia el formato de la fuente actual a negrita
fuente = font.Font(weight='bold')

# Define las etiquetas, marcos, botonoes y el slider
# Titulo que se muestra
etiqTitulo = ttk.Label(monitor, text="Monitoreo de riego", font=fuente)

# Marco del Manejo de estados
marcoD = ttk.Frame(monitor, borderwidth=2, relief="raised", padding=(10,10))
marcoD.grid(column=0, row=1, rowspan=2)

lbTituloF1 = ttk.Label(marcoD, text="Control de Invernadero", font=fuente)
lbTituloF1.grid(column=0, row=0, columnspan=5)

#Aspersor
lbAspersor = ttk.Label(marcoD, text="Aspersor: ", font=fuente)
lbAspersor.grid(column=0, row=1)

lbEstadoAspersor = ttk.Label(marcoD, text="APAGADO", font=fuente)
lbEstadoAspersor.grid(column=1, row=1)

OnOffAspersorButton = ttk.Button(marcoD, text="ON/OFF", command=onOffRegado)
OnOffAspersorButton.grid(column=2, row=1)

cambioEstadoAspersorButton = ttk.Button(marcoD, text="AUTO", command=regadoAuto)
cambioEstadoAspersorButton.grid(column=3, row=1)

#Foco
lbFoco = ttk.Label(marcoD, text="Foco: ", font=fuente)
lbFoco.grid(column=0, row=2)

lbEstadoFoco = ttk.Label(marcoD, text="APAGADO", font=fuente)
lbEstadoFoco.grid(column=1, row=2)

OnOffFocoButton = ttk.Button(marcoD, text="ON/OFF", command=onOffFoco)
OnOffFocoButton.grid(column=2, row=2)

cambioEstadoFocoButton = ttk.Button(marcoD, text="AUTO", command=focoAuto)
cambioEstadoFocoButton.grid(column=3, row=2)

#Alarma
lbAlarma = ttk.Label(marcoD, text="Alarma: ", font=fuente)
lbAlarma.grid(column=0, row=3)

lbEstadoAlarma = ttk.Label(marcoD, text="APAGADO", font=fuente)
lbEstadoAlarma.grid(column=1, row=3)

OnOffAlarmaButton = ttk.Button(marcoD, text="ON/OFF", command=onOffAlarma)
OnOffAlarmaButton.grid(column=2, row=3)

lbEstadoSuelo = ttk.Label(marcoD, text="Estado Suelo", font=fuente)
lbEstadoSuelo.grid(column=0, row=4)

lbHumedad = ttk.Label(marcoD, text="0", font=fuente, foreground="blue")
lbHumedad.grid(column=1, row=4)

lbEstadoHumedad = ttk.Label(marcoD, text="Estado Humedad", font=fuente)
lbEstadoHumedad.grid(column=0, row=5)

bar = ttk.Progressbar(marcoD,orient=HORIZONTAL, length=300)
bar.grid(column=1, row = 5, columnspan = 3, pady=9)

lbTitulo2 = ttk.Label(marcoD, text="Detalles de Invernadero", font=fuente)
lbTitulo2.grid(column=0, row=6, columnspan=5)

lbUltimoRiego = ttk.Label(marcoD, text="Último Riego: ", font=fuente)
lbUltimoRiego.grid(column=0, row=7)

lbUltimaFechaRiego = ttk.Label(marcoD, text="", font=fuente)
lbUltimaFechaRiego.grid(column=1, row=7)

lbUltimaAlarma = ttk.Label(marcoD, text="Última Alarma: ", font=fuente)
lbUltimaAlarma.grid(column=0, row=8)

lbUltimaFechaAlarma = ttk.Label(marcoD, text="", font=fuente)
lbUltimaFechaAlarma.grid(column=1, row=8)

lbAlarmasDetectadas = ttk.Label(marcoD, text="Alarmas Detectadas: ", font=fuente)
lbAlarmasDetectadas.grid(column=0, row=9)

lbCantidadAlarmasDetectadas = ttk.Label(marcoD, text="0 ", font=fuente)
lbCantidadAlarmasDetectadas.grid(column=1, row=9)

lbPromedioHumedad = ttk.Label(marcoD, text="Promedio Humedad: ", font=fuente)
lbPromedioHumedad.grid(column=0, row=10)

lbPromedio = ttk.Label(marcoD, text="0 ", font=fuente)
lbPromedio.grid(column=1, row=10)


# percent = StringVar()
# text = StringVar()
# percentLabel = ttk.Label(monitor, textvariable=percent)
# taskLabel = ttk.Label(monitor, textvariable=text)

lecturaArduino()

monitor.mainloop()