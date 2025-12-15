import argparse
import cv2
import time
import numpy as np

from vision.tag_detection import VisionSystem
from navigation.navigation import RobotChassis

TARGET_DISTANCE_M = 0.30   # o robô deve parar a 30 cm da tag!
MAX_LINEAR_SPEED = 20.0    # cm/s (Limitador de segurança, vel. linear)
MAX_ANGULAR_SPEED = 40.0   # deg/s (Limitador do giro, vel. angular)

# Kp_linear: Converte erro de metros para cm/s
# Se o erro for 0.5m, e Kp=40, ele anda a 20 cm/s
KP_LINEAR = 100.0           

# Kp_angular: Converte erro lateral (metros) para deg/s
# Se o erro for 0.1m (10cm), e Kp=300, ele gira a 30 deg/s
KP_ANGULAR = 300.0

def main():
    parser = argparse.ArgumentParser(description="Recebe id da tag da missão")
    parser.add_argument('april_id', type=int, help="ID da apriltag para seguir")
    args = parser.parse_args()
    
    chassis = RobotChassis()
    vision = VisionSystem(tag_size_meters=0.05)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    chassis.start()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erro da câmera!")
                return

            frame, detections = vision.detect_tags(frame, draw=False)

            linear_cmd = 0.0
            angular_cmd = 0.0

            target_tag = None

            if detections:
                for d in detections:
                    if d.tag_id == args.april_id:
                        target_tag = d
                        break

            if target_tag is not None:
                x_m = target_tag.pose_t[0]   # desvio lateral (metros)
                z_m = target_tag.pose_t[2]   # distancia ate tag (metros)

                print(f"Achou tag! x={x_m} z={z_m}")

                error_dist = z_m - TARGET_DISTANCE_M
                error_ang = -x_m

                linear_cmd = error_dist * KP_LINEAR
                angular_cmd = error_ang * KP_ANGULAR
            
            else:
                # Se a lista estiver vazia OU se a lista tem tags mas não a que queremos
                # O robô deve parar por segurança
                linear_cmd = 0.0
                angular_cmd = 0.0
            
            # Segurança: robô tem que respeitar limites máximos
            linear_cmd = np.clip(linear_cmd, -MAX_LINEAR_SPEED, MAX_LINEAR_SPEED)
            angular_cmd = np.clip(angular_cmd, -MAX_ANGULAR_SPEED, MAX_ANGULAR_SPEED)
            
            # deadzone
            if abs(linear_cmd) < 1.0: linear_cmd = 0.0
            if abs(angular_cmd) < 1.0: angular_cmd = 0.0

            chassis.set_velocity(linear_cmd, angular_cmd)

    except KeyboardInterrupt:
        print("Interrupção via teclado")
    finally:
        print("Parando robô")
        chassis.stop()
        chassis.l_wheel_motor.close()
        chassis.r_wheel_motor.close()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()