import math
import pigpio
import time
import threading


class DCMotor:
    def __init__(self, pwm_pin: int, inA_pin: int, inB_pin: int, freq: int):
        '''
        Inicializador de uma motor DC. Recebe:
        pwm_pin: pino para PWM.
        inA_pin: pino A da ponte-H.
        inB_pin: pino B da ponte-H.
        freq: frequência da onda PWM.
        '''

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio não conseguiu conectar-se à placa!")
    
        self.pwm_pin = pwm_pin
        self.inA_pin = inA_pin
        self.inB_pin = inB_pin
        self.freq = freq

        self.pi.set_mode(self.pwm_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.inA_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.inB_pin, pigpio.OUTPUT)

        self.pi.set_PWM_range(self.pwm_pin, 100)    # agora duty cycle máximo é 100 (antes era 255)
        self.pi.set_PWM_frequency(self.pwm_pin, self.freq)

        self.stop() # começar parado para evitar surpresinhas fdp

    def forward(self, duty_percent):
        self.pi.write(self.inA_pin, 1)
        self.pi.write(self.inB_pin, 0)
        self.pi.set_PWM_dutycycle(self.pwm_pin, duty_percent)

    def reverse(self, duty_percent):
        self.pi.write(self.inA_pin, 0)
        self.pi.write(self.inB_pin, 1)
        self.pi.set_PWM_dutycycle(self.pwm_pin, duty_percent)
    
    def stop(self):
        self.pi.write(self.inA_pin, 0)
        self.pi.write(self.inB_pin, 0)
        self.pi.set_PWM_dutycycle(self.pwm_pin, 0)

    def close(self):
        self.stop()     # para rodas...
        self.pi.stop()  # e mata conexão com o rpi


class Encoder:
    def __init__(self, interrupt_pin: int, ppr: int, debounce_us: float=0):
        """
        Cria um novo encoder rotatório óptico.
        interrupt_pin: o pino que vai receber os pulsos do OUT do encoder.
        ppr: (pulses per revolution) quantos pulsos o encoder gera para uma volta completa.
        debounce_us: em microssegundos, o intervalo de debounce (ignora pulsos dentro do intervalo)
        """

        self.interrupt_pin = interrupt_pin
        self.ppr = ppr
        self.debounce_us = debounce_us

        self.last_tick = 0
        self.pulses = 0
        self._lock = threading.Lock()

        self._last_calc_time = time.time()
        self._last_calc_pulses = 0

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio não conseguiu conectar-se à placa!")
        
        self.pi.set_mode(self.interrupt_pin, pigpio.INPUT)

        self._cb = self.pi.callback(
            interrupt_pin,
            pigpio.EITHER_EDGE,
            self._pulse_callback
        )

    def _pulse_callback(self, gpio, level, tick):
        if self.debounce_us > 0:
            if (tick - self.last_tick) < self.debounce_us:
                return      # está dentro do intervalo de debouncing
            self.last_tick = tick
        
        with self._lock:    # evita concorrência de threads
            self.pulses += 1
    
    def get_pulses(self):
        with self._lock:
            return self.pulses
        
    def reset(self):
        with self._lock:
            self.pulses = 0
    
    def get_rpm(self):
        now = time.time()
        dt = now - self._last_calc_time
        
        if dt <= 0:
            return 0

        pulses_now = self.get_pulses()
        dp = pulses_now - self._last_calc_pulses

        self._last_calc_time = now
        self._last_calc_pulses = pulses_now

        revolutions = dp / self.ppr
        
        return (revolutions / dt) * 60.0    # rpm!
    
    def stop(self):
        self._cb.cancel()
        self.pi.stop()


class Wheel:
    def __init__(self, wheel_diameter_cm: float, motor: DCMotor, encoder: Encoder | None = None):
        """
        Cria uma roda, opcionalmente com um encoder.
        wheel_diameter_cm: o diâmetro da roda em centímetros.
        motor: um objeto da classe DCMotor, representando o motor DC que moverá a roda.
        encoder (opcional): um objeto Encoder, usado para medir velocidade angular, distância percorrida etc.
        """

        self.encoder = encoder
        self.motor = motor
        self.wheel_diameter_cm = wheel_diameter_cm
        self._wheel_circumference_cm = math.pi * self.wheel_diameter_cm

    def has_encoder(self):
        return self.encoder is not None
    
    def get_speed_cm_s(self):
        if not self.has_encoder():
            return 0.0
        
        rpm = self.encoder.get_rpm()
        rps = rpm / 60.0
        return rps * self._wheel_circumference_cm
    
    def set_throttle(self, duty_percent: int):
        "duty_percent pode ser positivo para ir para frente, ou negativo para ré"

        if duty_percent > 0:
            self.motor.forward(duty_percent)
        elif duty_percent < 0:
            self.motor.reverse(-duty_percent)
        else:
            self.motor.stop()   # duty_percent é zero
    
    def stop(self):
        self.motor.stop()
    
    def close(self):
        if self.has_encoder():
            self.encoder.stop()
        self.motor.close()