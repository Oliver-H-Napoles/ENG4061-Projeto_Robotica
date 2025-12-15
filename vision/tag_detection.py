import cv2
from pupil_apriltags import Detector
import numpy as np
import logging

logger = logging.getLogger(__name__)

class VisionSystem:
    def __init__(self, family="tag36h11", tag_size_meters=0.05, resolution=(1280, 720)):
        """
        Inicializa o sistema de visão usando pupil_apriltags.
        """
        self.tag_size = tag_size_meters

        try:
            self.detector = Detector(
                families=family,
                nthreads=6,
                quad_decimate=1.0,
                quad_sigma=0.0,
                refine_edges=True
            )
            logger.info(f"Detector pupil_apriltags iniciado com a família: {family}")
            self.initialized = True
        except Exception as e:
            logger.error(f"Falha ao iniciar pupil_apriltags: {e}")
            self.initialized = False

        W, H = resolution

        if W == 1280:
            fx = 1068.0
            fy = 1068.0
            cx = 640.0
            cy = 360.0
        elif W == 640:
            fx = 534.0
            fy = 534.0
            cx = 320.0
            cy = 240.0
        else:
            logger.warning("Resolução desconhecida, usando f=W")
            fx = float(W)
            fy = float(W)
            cx = W / 2.0
            cy = H / 2.0

        self.camera_params = (fx, fy, cx, cy)

        # coeficientes da câmera (dist. focal, deslocamento etc.)
        self.dist_coefficients = np.zeros((5, 1))
        self.camera_matrix = np.array([
            [fx, 0, cx],
            [0, fy, cy],
            [0,  0,  1]
        ])

    def detect_tags(self, frame, draw=True):
        if not self.initialized:
            return frame, []

        # a biblioteca espera uma img em preto e branco
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar com cálculo de pose
        detections = self.detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=self.camera_params,
            tag_size=self.tag_size
        )

        if not draw:
            return frame, detections

        # Desenhar
        for d in detections:
            # corners já vêm como array Nx2
            corners = d.corners.astype(int)

            # desenhar as 4 linhas da box
            cv2.polylines(frame, [corners], True, (0, 255, 0), 2)

            # centro da apriltag!
            cX, cY = map(int, d.center)
            cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)

            # escrever ID
            cv2.putText(frame, f"ID: {d.tag_id}", (corners[0][0], corners[0][1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
            x, y, z = self.estimate_position(d)
            print(f"x={x}, y={y}, z={z}")

        return frame, detections
    
    def estimate_position(self, detection):
        return detection.pose_t