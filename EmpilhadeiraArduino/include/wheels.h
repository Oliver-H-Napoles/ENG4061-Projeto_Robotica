#ifndef WHEELS_H
#define WHEELS_H

#include <Arduino.h>

class Roda {
public:
    Roda(uint8_t pinoPWM, uint8_t pinoINA, uint8_t pinoINB);
    void forward(uint8_t throttle);
    void reverse(uint8_t throttle);
    void stop(void);

private:
    uint8_t _pinoPWM;
    uint8_t _pinoINA;
    uint8_t _pinoINB;
    bool _validate_throttle(uint8_t throttle);
};

#endif /* WHEELS_H */