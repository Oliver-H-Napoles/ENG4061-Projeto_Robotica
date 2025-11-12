import pigpio

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

    def forward(self, duty_percent):
        duty = 

