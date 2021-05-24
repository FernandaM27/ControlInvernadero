//Librerias necesarias
#include <Servo.h>

//Definir pines
const int PIN_FOTORES = A0;
const int PIN_SENSOR = A2;
const int PIN_LED = 3;

const int PIN_LED_PERSONA = 13;
const int PIN_PIR = 2;
const int IN1 = 8;
const int IN2 = 9;
const int IN3 = 10;
const int IN4 = 11;
const unsigned int PIN_SERVO = 6;

//pausas
const int PAUSA = 500;
int lapsoAnterior = 0;

//comunicación
const unsigned int BAUD_RATE = 9600;

//variables necesarias
const float luzDia = 0.90;
int ledDia = HIGH;
boolean llave = false;
boolean llaveAnterior = false;
// Angulos) en los que se posicionara el servo
const int angulos[] = {0, 90};

// Crea una instancia de la clase Servo, que implemeta la biblioteca servo.
Servo servo;
const int pasosRevolucion = 4076;
// Velocidad del motor (En realidad es el retraso en uS entre dos
// pasos del motor). A mayor valor, menor velocidad y viceversa
int velocidad = 1000;
// Contador para los pasos
int cuentaPasos = 0;
// Secuencia media fase
const int numPasos = 8;
const int secuenciaEncendido[8] = { B1000, B1100, B0100, B0110,
                                    B0010, B0011, B0001, B1001
                                  };

int estadoAntPir = LOW;

boolean autoLuz = true;
boolean autoRegado = true;
boolean autoAlarma = true;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_LED_PERSONA, OUTPUT);
  // Establece el pin de control del servo
  servo.attach(PIN_SERVO);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(PIN_PIR, INPUT);
}

void loop() {
  char comando[6];
  // Se lee el sensor de movimiento
  int valorPir = digitalRead(PIN_PIR);
  // Si se detecta movimiento
  if (valorPir == HIGH && autoAlarma) {
    // se enciende el LED
    digitalWrite(PIN_LED_PERSONA, HIGH);
    // Si no habia movimiento anteriormente
    Serial.println("MOV");
    if (estadoAntPir == LOW) {

      // Hay movimiento
      estadoAntPir = HIGH;
    }
    cambiarEstadoLlave(false);
    delay(5000);
    digitalWrite(PIN_LED_PERSONA, LOW);
    Serial.println("MOVOFF");
  } else {
    float valor = 0;
    // Lee el nivel de luz de la fotoresistencia
    float nivelLuz = analogRead(PIN_FOTORES);
    // Convierte el nivel de luz a un valor flotante en
    // el rango 0 a 5.0 V.
    if (autoLuz) {
      valor = nivelLuz * (5.0 / 1023.0);
      // Envia el valor al puerto serie
      //Serial.println(valor);
      //delay(PAUSA);
      //Serial.println(valor);
      if (valor >= luzDia) {
        digitalWrite(PIN_LED, LOW);
        Serial.println("LOW");
      } else {
        digitalWrite(PIN_LED, HIGH);
        Serial.println("HIGH");
      }
    }
    if (autoRegado) {
      int humedad = analogRead(PIN_SENSOR);
      Serial.println(humedad);
      if (humedad > 500) {
        cambiarEstadoLlave(true);
      } else {
        cambiarEstadoLlave(false);
      }
    }
    lapsoAnterior = 0;

    if (llave) {
      Serial.println("REGANDO");
      for (int i = 0; i < pasosRevolucion; i++) {
        // Gira un paso en la direccion horaria
        pasoHorario();
        delayMicroseconds(velocidad);
      }
    }else{
      Serial.println("REGADO");
    }
  }
  if (Serial.available() > 0) {
    int n = Serial.readBytesUntil('\n', comando, 10);
    comando[n] = '\0';
    if (!strcmp(comando, "LON")) {
      autoLuz = false;
      digitalWrite(PIN_LED, HIGH);
      Serial.println("HIGH");
    } else if (!strcmp(comando, "LOFF")) {
      autoLuz = false;
      digitalWrite(PIN_LED, LOW);
      Serial.println("LOW");
    } else if (!strcmp(comando, "LAU")) {
      autoLuz = true;
    } else if (!strcmp(comando, "RON")) {
      autoRegado = false;
      cambiarEstadoLlave(true);
      Serial.println("RON");
      llave = true;
    } else if (!strcmp(comando, "ROFF")) {
      autoRegado = false;
      cambiarEstadoLlave(false);
      Serial.println("ROFF");
      llave = false;
    } else if (!strcmp(comando, "RAU")) {
      autoRegado = true;
    } else if (!strcmp(comando, "AON")) {
      autoAlarma = true;
      Serial.println("AON");
    } else if (!strcmp(comando, "AOFF")) {
      autoAlarma = false;
      Serial.println("AOFF");
    }
  }
}

/*
  Esta funcion hace que el motor gire un paso en la dirección
  horaria
*/
void pasoHorario() {
  cuentaPasos++;
  if (cuentaPasos >= numPasos) cuentaPasos = 0;
  // Energiza las bobinas del motor
  energiza(cuentaPasos);
}

/*
  Esta funcion energiza las bobinas del motor
*/
void energiza(int paso) {
  digitalWrite(IN1, bitRead(secuenciaEncendido[paso], 0));
  digitalWrite(IN2, bitRead(secuenciaEncendido[paso], 1));
  digitalWrite(IN3, bitRead(secuenciaEncendido[paso], 2));
  digitalWrite(IN4, bitRead(secuenciaEncendido[paso], 3));
}

void cambiarEstadoLlave(bool estado) {
  if (llave != estado && autoRegado) {
    llave = estado;
  }
  if (estado) {
    servo.write(angulos[0]);
  } else {
    servo.write(angulos[1]);
  }
}
