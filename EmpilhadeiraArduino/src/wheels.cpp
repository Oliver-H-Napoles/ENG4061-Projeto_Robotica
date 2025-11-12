#include "wheels.h"

Roda::Roda(uint8_t pinoPWM, uint8_t pinoINA, uint8_t pinoINB) 
    : _pinoPWM(pinoPWM), _pinoINA(pinoINA), _pinoINB(pinoINB) {
    pinMode(_pinoPWM, OUTPUT);
    pinMode(_pinoINA, OUTPUT);
    pinMode(_pinoINB, OUTPUT);
}

void Roda::forward(uint8_t throttle) {
    if (!_validate_throttle(throttle)) {
        #ifdef DEBUG
        Serial.println("Erro: throttle deve ser um inteiro de 0 a 100.");
        #endif
        return;
    }

    digitalWrite(_pinoINA, HIGH);
    digitalWrite(_pinoINB, LOW);
    analogWrite(_pinoPWM, map(throttle, 0, 100, 0, 255));
}

void Roda::reverse(uint8_t throttle) {
    if (!_validate_throttle(throttle)) {
        #ifdef DEBUG
        Serial.println("Erro: throttle deve ser um inteiro de 0 a 100.");
        #endif
        return;
    }

    digitalWrite(_pinoINA, LOW);
    digitalWrite(_pinoINB, HIGH);
    analogWrite(_pinoPWM, map(throttle, 0, 100, 0, 255));
}

void Roda::stop() {
    digitalWrite(_pinoINA, LOW);
    digitalWrite(_pinoINB, LOW);
    analogWrite(_pinoPWM, 0);
}

bool Roda::_validate_throttle(uint8_t throttle) {
    return throttle <= 100; 
}
