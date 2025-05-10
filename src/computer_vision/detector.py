import cv2
import numpy as np
import os
import time
import requests
import logging
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('waste_detector')

class WasteDetector:
    """
    Detector de descartes ilegais usando OpenCV.
    Usa técnicas simples como subtração de fundo para detectar objetos novos nas imagens.
    """
    
    def __init__(self, backend_url="http://localhost:8000", threshold=1000):
        """
        Inicializa o detector.
        
        Args:
            backend_url: URL da API do backend
            threshold: Limiar para detecção (área mínima em pixels)
        """
        self.backend_url = backend_url
        self.threshold = threshold
        self.background_images = {}  # Dicionário para armazenar imagens de fundo por câmera
        logger.info("Detector de descartes ilegais inicializado")
        
    def load_background(self, camera_id, image_path):
        """
        Carrega uma imagem de fundo para uma câmera específica.
        
        Args:
            camera_id: ID da câmera
            image_path: Caminho para a imagem de fundo
        """
        try:
            background = cv2.imread(image_path)
            if background is None:
                logger.error(f"Não foi possível carregar a imagem de fundo: {image_path}")
                return False
                
            # Convertemos para escala de cinza para simplificar a detecção
            background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
            self.background_images[camera_id] = background_gray
            logger.info(f"Imagem de fundo carregada para câmera {camera_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar imagem de fundo: {str(e)}")
            return False
            
    def detect_waste(self, camera_id, current_image_path):
        """
        Detecta possíveis descartes ilegais comparando a imagem atual com a imagem de fundo.
        
        Args:
            camera_id: ID da câmera
            current_image_path: Caminho para a imagem atual
            
        Returns:
            tuple: (has_waste, image_with_detection, contours_area)
        """
        # Verificar se temos uma imagem de fundo para esta câmera
        if camera_id not in self.background_images:
            logger.error(f"Imagem de fundo não encontrada para câmera {camera_id}")
            return False, None, 0
            
        try:
            # Carregar a imagem atual
            current_image = cv2.imread(current_image_path)
            if current_image is None:
                logger.error(f"Não foi possível carregar a imagem atual: {current_image_path}")
                return False, None, 0
                
            # Converter para escala de cinza
            current_gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
            
            # Calcular a diferença absoluta entre as imagens
            diff = cv2.absdiff(self.background_images[camera_id], current_gray)
            
            # Aplicar um threshold para binarizar a imagem de diferença
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            # Aplicar operações morfológicas para reduzir ruído
            kernel = np.ones((5, 5), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Encontrar contornos na imagem binarizada
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Calcular a área total dos contornos
            total_area = sum(cv2.contourArea(c) for c in contours)
            
            # Verificar se a área é maior que o threshold
            has_waste = total_area > self.threshold
            
            # Se houver detecção, desenhar os contornos na imagem original
            image_with_detection = current_image.copy()
            cv2.drawContours(image_with_detection, contours, -1, (0, 0, 255), 2)
            
            if has_waste:
                logger.info(f"Possível descarte detectado na câmera {camera_id}. Área total: {total_area}")
            
            return has_waste, image_with_detection, total_area
        except Exception as e:
            logger.error(f"Erro na detecção: {str(e)}")
            return False, None, 0
            
    def notify_backend(self, camera_id, image_path, detection_data):
        """
        Notifica o backend sobre um possível descarte ilegal.
        
        Args:
            camera_id: ID da câmera
            image_path: Caminho para a imagem com detecção
            detection_data: Dados adicionais sobre a detecção
            
        Returns:
            bool: True se a notificação foi bem-sucedida, False caso contrário
        """
        try:
            # Preparar metadados para envio
            timestamp = datetime.now().isoformat()
            
            # Estes dados seriam obtidos de uma configuração real,
            # mas para o POC usamos valores fixos
            latitude = -8.0476  # Coordenadas de exemplo para Recife
            longitude = -34.8770
            
            # Criar payload para o backend
            payload = {
                "camera_id": camera_id,
                "timestamp": timestamp,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "detection_area": detection_data,
                "waste_type": "Desconhecido"  # Em uma versão avançada, usaríamos classificação
            }
            
            # Preparar a imagem para upload
            files = {
                "image": (os.path.basename(image_path), open(image_path, "rb"), "image/jpeg")
            }
            
            # Enviar notificação ao backend
            response = requests.post(
                f"{self.backend_url}/api/waste-detection", 
                data=payload,
                files=files,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"Notificação enviada com sucesso. ID: {response.json().get('id', 'N/A')}")
                return True
            else:
                logger.error(f"Erro ao enviar notificação: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao notificar backend: {str(e)}")
            return False
            
    def process_camera_images(self, camera_id, images_folder, background_index=0):
        """
        Processa todas as imagens de uma câmera específica.
        
        Args:
            camera_id: ID da câmera
            images_folder: Pasta contendo as imagens da câmera
            background_index: Índice da imagem a ser usada como fundo
            
        Returns:
            int: Número de descartes detectados
        """
        folder_path = Path(images_folder)
        image_files = sorted([f for f in folder_path.glob("*.jpg") or folder_path.glob("*.png")])
        
        if not image_files:
            logger.warning(f"Nenhuma imagem encontrada na pasta: {images_folder}")
            return 0
            
        # Carregar a imagem de fundo
        background_path = str(image_files[background_index])
        if not self.load_background(camera_id, background_path):
            return 0
            
        detections_count = 0
        
        # Processar cada imagem, exceto a de fundo
        for i, image_path in enumerate(image_files):
            if i == background_index:
                continue  # Pular a imagem de fundo
                
            logger.info(f"Processando imagem {i+1}/{len(image_files)}: {image_path}")
            
            has_waste, image_with_detection, area = self.detect_waste(camera_id, str(image_path))
            
            if has_waste:
                # Salvar a imagem com os contornos para referência
                detection_path = folder_path / f"detection_{i}.jpg"
                cv2.imwrite(str(detection_path), image_with_detection)
                
                # Notificar o backend
                if self.notify_backend(camera_id, str(detection_path), area):
                    detections_count += 1
                    
                # Simular um alerta local para o POC
                print(f"\nALERTA: Possível descarte ilegal detectado na câmera {camera_id}!")
                print(f"Timestamp: {datetime.now().isoformat()}")
                print(f"Área de detecção: {area} pixels\n")
                
                # Um pequeno delay para visualização do alerta no terminal
                time.sleep(1)
                
        return detections_count


# Exemplo de uso (para teste)
if __name__ == "__main__":
    detector = WasteDetector()
    
    # Neste exemplo, processaríamos imagens de uma pasta de amostra
    sample_folder = "../data/sample_images/camera_01"
    
    # Verificar se a pasta existe, caso contrário criar para testes
    if not os.path.exists(sample_folder):
        os.makedirs(sample_folder, exist_ok=True)
        print(f"Pasta criada: {sample_folder}")
        print("Adicione imagens de exemplo nesta pasta para testar o detector.")
    else:
        print(f"Processando imagens da câmera 01 da pasta: {sample_folder}")
        detections = detector.process_camera_images("camera_01", sample_folder)
        print(f"Total de descartes detectados: {detections}") 