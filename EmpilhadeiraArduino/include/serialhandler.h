#ifndef SERIALHANDLER_H
#define SERIALHANDLER_H

#include <Arduino.h>

#define _MAX_CALLBACKS 10

class SerialHandler {
public:
    typedef void (*Callback)(String);
    void registerCommand(const String& command, Callback func);
    void handleSerial(void);

private:
    String _commands[_MAX_CALLBACKS];
    Callback _callbacks[_MAX_CALLBACKS];
    uint8_t _cmdCount = 0;
};

#endif  /* SERIALHANDLER_H */