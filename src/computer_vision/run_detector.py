#!/usr/bin/env python3
"""
Script para executar o detector de descartes ilegais.
Este script simula a obtenção periódica de imagens de câmeras e a detecção
de possíveis descartes ilegais.
"""

import os
import time
import argparse
import logging
from pathlib import Path
from detector import WasteDetector

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('waste_detector_runner')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Detector de Descartes Ilegais')
    
    parser.add_argument(
        '--cameras-folder',
        type=str,
        default='../data/sample_images',
        help='Pasta contendo as subpastas das câmeras com imagens'
    )
    
    parser.add_argument(
        '--backend-url',
        type=str,
        default='http://localhost:8000',
        help='URL do backend API'
    )
    
    parser.add_argument(
        '--threshold',
        type=int,
        default=1000,
        help='Threshold para detecção (área mínima em pixels)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Intervalo (em segundos) entre cada ciclo de detecção'
    )
    
    return parser.parse_args()

def main():
    """Função principal."""
    args = parse_arguments()
    
    # Criar o detector
    detector = WasteDetector(
        backend_url=args.backend_url,
        threshold=args.threshold
    )
    
    # Verificar se a pasta de câmeras existe
    cameras_folder = Path(args.cameras_folder)
    if not cameras_folder.exists():
        logger.error(f"Pasta de câmeras não encontrada: {cameras_folder}")
        logger.info("Criando pasta de câmeras...")
        cameras_folder.mkdir(parents=True, exist_ok=True)
        
        # Criar um exemplo de pasta de câmera para demonstração
        sample_camera = cameras_folder / "camera_01"
        sample_camera.mkdir(exist_ok=True)
        logger.info(f"Pasta de exemplo criada: {sample_camera}")
        logger.info("Adicione imagens de exemplo (.jpg ou .png) nesta pasta.")
        return
    
    # Encontrar todas as pastas de câmeras
    camera_folders = [f for f in cameras_folder.iterdir() if f.is_dir()]
    
    if not camera_folders:
        logger.error(f"Nenhuma pasta de câmera encontrada em: {cameras_folder}")
        return
    
    logger.info(f"Encontradas {len(camera_folders)} câmeras")
    
    try:
        while True:
            logger.info("Iniciando ciclo de detecção...")
            
            total_detections = 0
            
            # Processar cada câmera
            for camera_folder in camera_folders:
                camera_id = camera_folder.name
                logger.info(f"Processando câmera: {camera_id}")
                
                # Detectar descartes na pasta da câmera
                detections = detector.process_camera_images(camera_id, str(camera_folder))
                total_detections += detections
                
                if detections > 0:
                    logger.info(f"Detectados {detections} possíveis descartes na câmera {camera_id}")
                else:
                    logger.info(f"Nenhum descarte detectado na câmera {camera_id}")
            
            logger.info(f"Ciclo de detecção concluído. Total de descartes: {total_detections}")
            logger.info(f"Aguardando {args.interval} segundos para o próximo ciclo...")
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        logger.info("Detector interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no detector: {e}")

if __name__ == "__main__":
    main() 