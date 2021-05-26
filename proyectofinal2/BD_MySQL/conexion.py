import mysql.connector
from mysql.connector import Error

try:
    conexion = mysql.connector.connect(
       host = 'localhost',
       user = 'root',
       port =  3306,
       password = 'sesamo',
       db = 'invernadero'
    )

    if conexion.is_connected():
        print('Conexión exitosa.')
        infoServer = conexion.get_server_info()
        print('Informacion del server: ', infoServer)
except Error as ex:
    print('Error durante la conexión: ', ex)
finally: 
    if conexion.is_connected():

        conexion.close()
        print('La conexión ha finalizado.')