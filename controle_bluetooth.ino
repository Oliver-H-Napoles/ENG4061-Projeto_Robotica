#include <SoftwareSerial.h>

SoftwareSerial bluetooth(2, 3);


int porta = 13;
int esquerda = 5;
int direita = 3;
int encoderIn = 18;
unsigned long contador;
float rpm;

String comando = "";

void readSerial() {
  if (Serial.available() > 0) {
  comando = Serial.readStringUntil('\n');  // Lê até o fim da linha
    comando.trim();
    if (comando == "off") {
      digitalWrite(direita, HIGH);
      digitalWrite(esquerda, LOW);
    } 
    else if (comando == "on") {
      digitalWrite(direita, LOW);
      digitalWrite(esquerda, HIGH);
    }
    else if (comando.substring(0,3) == "num"){
      int valor = comando.substring(4,7).toInt();
      analogWrite(porta, valor);
      Serial.println(valor);
    }
  }
}

void definePonteH(){
  pinMode(direita, OUTPUT);
  pinMode(esquerda, OUTPUT);
  pinMode(porta, OUTPUT);
  digitalWrite(porta, LOW);
  digitalWrite(direita, HIGH);
  digitalWrite(esquerda, LOW);

}

void conta(){
  contador++;
}

void defineEncoder(){
  pinMode(encoderIn, INPUT);
  attachInterrupt(digitalPinToInterrupt(encoderIn), conta, RISING);
}

unsigned long mNow;
unsigned long mCmp;

void rpmRead(){
  mNow = millis();
  if(mNow>mCmp + 100){ //conta quantas voltas ele deu em um segundo
    rpm = contador*600/32;
    Serial.println(contador);
    //contador = 0;
    mCmp = mNow;
  }
}

void setup() {
  contador = 0;
  Serial.begin(9600);
  bluetooth.begin(38400);
  defineEncoder();
  //definePonteH();
  mCmp = millis();
}

void loop() {
  rpmRead();
  readSerial();
  
  if (Serial.available()) {
    char r = Serial.read();
    bluetooth.print(r);
    Serial.print(r);
  }


  if (bluetooth.available()) {
    char r = bluetooth.read();
    Serial.print(r); 
    if (r == '\n' || r == '\r') {
      comando.trim();
      if (comando == "FRENTE") {
        Serial.println("ANDAR PARA FRENTE");
      } else if (comando == "TRAS") {
        Serial.println("ANDAR PARA TRAS");
      } else if (comando == "DIREITA") {
        Serial.println("GIRAR PARA DIREITA");
      } else if (comando == "ESQUERDA") {
        Serial.println("GIRAR PARA ESQUERDA");
      }
      comando = "";
    } else {
      comando += r;
    }
  }
}