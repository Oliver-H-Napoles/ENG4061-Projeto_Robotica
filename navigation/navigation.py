import math
import pigpio
from simple_pid import PID
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
    
    def __str__(self):
        return f"Encoder @ GPIO{self.interrupt_pin}"

    def _pulse_callback(self, gpio, level, tick):
        if self.debounce_us > 0:
            if (tick - self.last_tick) < self.debounce_us:
                return      # está dentro do intervalo de debouncing
            self.last_tick = tick
            
        with self._lock:    # evita concorrência de threads
            #print(f"{self}: ticked!")
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
    
    def get_speed_cm_s(self):
        if not self.encoder:
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
        if self.encoder:
            self.encoder.stop()
        self.motor.close()


class SpeedPID:
    def __init__(self, kp:float, ki:float, kd:float, setpoint:float=0.0, output_lim:tuple=(-100,100)):
        self.pid = PID(kp, ki, kd, setpoint=setpoint)
        self.pid.output_limits = output_lim
        self.pid.sample_time = 0.05     # 20 Hz, um vigésimo de segundo

    def update(self, current_speed:float) -> float:
        return self.pid(current_speed)
    
    def set_target(self, target: float):
        self.pid.setpoint = target

    def reset(self):
        self.pid.reset()


class RobotChassis:
    def __init__(self):
        self.l_wheel_motor = DCMotor(12, 5 ,6, 500)
        self.r_wheel_motor = DCMotor(13, 7, 8, 500) 

        self.track_width = 17.0     # Distância entre as rodas (cm)
        
        # Qual a velocidade do robo quando ele esta com duty cycle de 100%?
        self.estimated_max_speed_cm_s = 60.0 

        # Calibração pra roda esquerda girar certo...
        self.l_trim = 1.4   

    def set_velocity(self, linear_cm_s, angular_deg_s):
        """
        Converte velocidade desejada (cm/s) diretamente para PWM (0-100)
        sem feedback de sensores.
        """
        angular_rad_s = math.radians(angular_deg_s)
        
        # velocidade linear necessária para cada roda em cm/s
        target_v_l = linear_cm_s - (angular_rad_s * self.track_width / 2.0)
        target_v_r = linear_cm_s + (angular_rad_s * self.track_width / 2.0)

        # conversão para PWM 
        # PWM = (Velocidade_Alvo / Velocidade_Maxima) * 100
        pwm_l = (target_v_l / self.estimated_max_speed_cm_s) * 100.0
        pwm_r = (target_v_r / self.estimated_max_speed_cm_s) * 100.0

        # cada roda tava girando em uma velocidade angular diferente com o mesmo PWM
        # isso aqui é uma multiplicação q conserta 
        pwm_l = pwm_l * self.l_trim

        # aplicar aos motores com limites
        self._set_motor_power(self.l_wheel_motor, pwm_l)
        self._set_motor_power(self.r_wheel_motor, pwm_r)

    def _set_motor_power(self, motor, pwm_value):
        """
        Função auxiliar para lidar com PWM positivo (frente), negativo (ré) 
        e limite de 100%.
        """
        # Limita entre -100 e 100 (Clamp)
        pwm_value = max(min(pwm_value, 100.0), -100.0)

        # deadzone
        if abs(pwm_value) < 10.0:
            motor.stop()
            return

        if pwm_value > 0:
            motor.forward(abs(pwm_value))
        elif pwm_value < 0:
            motor.reverse(abs(pwm_value))
        else:
            motor.stop()

    def start(self):
        print("RobotChassis (Open Loop): Sistema pronto.")

    def stop(self):
        self.l_wheel_motor.stop()
        self.r_wheel_motor.stop()
        
    def close(self):
        self.stop()
        self.l_wheel_motor.close()
        self.r_wheel_motor.close()

if __name__ == "__main__":
    lwheel = DCMotor(12, 5, 6, 500)
    rwheel = DCMotor(13, 7, 8, 500)
    l_wheel_encoder = Encoder(17, 32)
    try:
        lwheel.forward(100)
        rwheel.forward(100)
        while True:
            pass
    except KeyboardInterrupt:
        lwheel.stop()
        rwheel.stop()
        