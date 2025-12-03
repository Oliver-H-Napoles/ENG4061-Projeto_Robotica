import cv2
import apriltag
import logging

# Configuração de log específica para este módulo
logger = logging.getLogger(__name__)

class VisionSystem:
    def __init__(self, family="tag36h11"):
        """
        Inicializa o sistema de visão e o detector AprilTag.
        Carrega o detector apenas uma vez na memória.
        """
        try:
            self.options = apriltag.DetectorOptions(families=family)
            self.detector = apriltag.Detector(self.options)
            logger.info(f"Detector AprilTag iniciado com a família: {family}")
            self.initialized = True
        except Exception as e:
            logger.error(f"Falha ao iniciar detector AprilTag: {e}")
            self.initialized = False

    def detect_tags(self, frame, draw=True):
        """
        Recebe um frame (imagem colorida), detecta tags e opcionalmente desenha nela.
        
        Retorna:
            processed_frame: A imagem (com desenhos se draw=True)
            detections: Lista de objetos de detecção (ou lista de IDs)
        """
        if not self.initialized:
            return frame, []

        # 1. Converter para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 2. Detectar
        results = self.detector.detect(gray)
        
        # Se não precisa desenhar, retorna logo os resultados para ganhar tempo
        if not draw:
            return frame, results

        # 3. Desenhar (se solicitado)
        for r in results:
            # Extrair coordenadas (convertendo float para int)
            (ptA, ptB, ptC, ptD) = r.corners
            ptB = (int(ptB[0]), int(ptB[1]))
            ptC = (int(ptC[0]), int(ptC[1]))
            ptD = (int(ptD[0]), int(ptD[1]))
            ptA = (int(ptA[0]), int(ptA[1]))

            # Desenhar linhas da borda
            cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
            cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
            cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
            cv2.line(frame, ptD, ptA, (0, 255, 0), 2)

            # Desenhar centro
            (cX, cY) = (int(r.center[0]), int(r.center[1]))
            cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)

            # Escrever ID
            tagID = f"ID: {r.tag_id}"
            cv2.putText(frame, tagID, (ptA[0], ptA[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame, results