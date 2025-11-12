#include <Arduino.h>
#include "wheels.h"

uint8_t IN1, IN2, IN3, IN4, ENA, ENB;
Roda rodaEsq, rodaDir;

void setup() {
  Serial.begin(9600);

  // 2 rodas por enquanto
  IN1 = 22;
  IN2 = 23;
  IN3 = 24;
  IN4 = 25;
  ENA = 5;
  ENB = 6;
  rodaEsq = Roda(ENA, IN1, IN2);
  rodaDir = Roda(ENB, IN3, IN4);
}

void loop() {
  rodaDir.forward(100);
  rodaEsq.forward(100);

  delay(1000);

  rodaDir.stop();
  rodaEsq.stop();

  delay(1000);

  rodaDir.reverse(50);
  rodaEsq.reverse(50);

  delay(2000);

  rodaDir.forward(100);
  rodaEsq.reverse(100);

  delay(1000);

  rodaDir.stop();
  rodaEsq.stop();

  delay(1000);
}
