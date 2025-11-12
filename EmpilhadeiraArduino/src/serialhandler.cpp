#include "serialhandler.h"

void SerialHandler::registerCommand(const String& command, Callback func) {
    if (_cmdCount < _MAX_CALLBACKS) {
        _commands[_cmdCount] = command;
        _callbacks[_cmdCount] = func;
        _cmdCount++;
    }
}

void SerialHandler::handleSerial() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();

        for (uint8_t c; c < _cmdCount; c++) {
            if (input == _commands[c]) {
                _callbacks[c](input);
                return;
            }
        }

        #ifdef DEBUG
        Serial.println("Comando desconhecido: " + input);
        #endif
    }
}
