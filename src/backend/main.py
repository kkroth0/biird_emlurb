import os
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json

# Importar módulos locais
import database
from models import WasteDetection, WasteDetectionCreate, WasteDetectionUpdate, Camera, NotificationRequest
from notifications import NotificationService
from blockchain_client import BlockchainClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('backend')

# Configurar diretório para salvar imagens e garantir que os diretórios existem
STATIC_DIR = Path(__file__).parent.parent / "data" / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
DETECTIONS_DIR = STATIC_DIR / "detections"

for dir_path in [STATIC_DIR, UPLOADS_DIR, DETECTIONS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Inicializar a aplicação FastAPI
app = FastAPI(
    title="API de Monitoramento de Descarte Ilegal",
    description="API para o sistema de monitoramento de descarte ilegal de resíduos",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar o diretório estático para servir imagens
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Inicializar serviços
notification_service = NotificationService()
blockchain_client = BlockchainClient()

@app.on_event("startup")
async def startup_event():
    logger.info("Inicializando o backend...")
    await database.init_db()
    logger.info("Banco de dados inicializado.")

@app.get("/")
async def root():
    return {"message": "API de Monitoramento de Descarte Ilegal funcionando"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Endpoints para câmeras
@app.get("/api/cameras", response_model=List[Camera])
async def get_cameras():
    cameras = await database.get_all_cameras()
    return cameras

@app.get("/api/cameras/{camera_id}/detections")
async def get_camera_detections(camera_id: str):
    detections = await database.get_camera_detections(camera_id)
    return detections

@app.put("/api/cameras/{camera_id}/status")
async def update_camera_status(camera_id: str, status: str):
    if status not in ["Online", "Offline", "Manutenção"]:
        raise HTTPException(status_code=400, detail="Status inválido")
        
    success = await database.update_camera_status(camera_id, status)
    
    if not success:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")
        
    return {"message": f"Status da câmera {camera_id} atualizado para {status}"}

# Endpoints para detecções de descarte
@app.get("/api/waste-detections")
async def get_waste_detections(
    camera_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100)
):
    """
    Obter todas as detecções de descarte.
    
    Parâmetros:
    - camera_id: Filtrar por câmera específica
    - status: Filtrar por status
    - limit: Limite de resultados
    """
    if camera_id:
        detections = await database.get_camera_detections(camera_id)
    else:
        detections = await database.get_all_detections()
        
    # Filtrar por status se fornecido
    if status:
        detections = [d for d in detections if d.get("status") == status]
        
    # Limitar resultados
    detections = detections[:limit]
    
    return detections

@app.get("/api/waste-detections/{detection_id}")
async def get_waste_detection(detection_id: str):
    """Obter uma detecção específica pelo ID."""
    detection = await database.get_detection(detection_id)
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detecção não encontrada")
        
    return detection

@app.post("/api/waste-detection")
async def create_waste_detection(
    background_tasks: BackgroundTasks,
    camera_id: str = Form(...),
    timestamp: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    detection_area: float = Form(...),
    waste_type: str = Form("Desconhecido"),
    image: Optional[UploadFile] = File(None)
):
    """
    Criar uma nova detecção de descarte.
    
    Este endpoint é usado pelo módulo de visão computacional para
    registrar uma nova detecção.
    """
    try:
        # Gerar ID único
        detection_id = str(uuid.uuid4())
        
        # Processar o timestamp
        try:
            parsed_timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            # Se o formato não for ISO, tentar outro formato comum
            parsed_timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            
        # Preparar dados da detecção
        detection_data = {
            "id": detection_id,
            "camera_id": camera_id,
            "timestamp": parsed_timestamp.isoformat(),
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "detection_area": detection_area,
            "waste_type": waste_type,
            "status": "Aberto"
        }
        
        # Salvar a imagem, se fornecida
        image_url = None
        if image:
            # Gerar nome do arquivo baseado no ID da detecção
            file_extension = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
            image_filename = f"{detection_id}{file_extension}"
            image_path = DETECTIONS_DIR / image_filename
            
            # Salvar o arquivo
            with open(image_path, "wb") as f:
                contents = await image.read()
                f.write(contents)
                
            # Gerar URL relativa
            image_url = f"/static/detections/{image_filename}"
            detection_data["image_url"] = image_url
            
        # Adicionar ao banco de dados
        await database.add_detection(detection_data, image_url)
        
        # Registrar na blockchain em segundo plano
        background_tasks.add_task(register_in_blockchain, detection_data)
        
        # Enviar notificação em segundo plano
        background_tasks.add_task(
            send_notification, 
            detection_data,
            str(image_path) if image else None
        )
        
        return {
            "message": "Detecção registrada com sucesso",
            "id": detection_id,
            "image_url": image_url
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar detecção: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.put("/api/waste-detections/{detection_id}")
async def update_waste_detection(
    detection_id: str, 
    update_data: WasteDetectionUpdate,
    background_tasks: BackgroundTasks
):
    """Atualizar uma detecção existente."""
    # Verificar se a detecção existe
    detection = await database.get_detection(detection_id)
    if not detection:
        raise HTTPException(status_code=404, detail="Detecção não encontrada")
        
    # Atualizar os dados
    update_dict = update_data.dict(exclude_unset=True)
    success = await database.update_detection(detection_id, update_dict)
    
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao atualizar detecção")
        
    # Se o status foi alterado para "Em Atendimento", registrar na blockchain
    if update_data.status == "Em Atendimento":
        # Atualizar detecção completa
        updated_detection = await database.get_detection(detection_id)
        background_tasks.add_task(register_in_blockchain, updated_detection)
        
    return {"message": "Detecção atualizada com sucesso"}

@app.post("/api/notifications")
async def send_notification_request(request: NotificationRequest):
    """
    Endpoint para solicitar o envio de notificações.
    
    Este endpoint pode ser usado pelo frontend para reenviar
    notificações manualmente.
    """
    detection = await database.get_detection(request.detection_id)
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detecção não encontrada")
        
    # Encontrar a imagem, se houver
    image_path = None
    if detection.get("image_url"):
        relative_path = detection["image_url"].replace("/static/", "")
        image_path = STATIC_DIR / relative_path
        
    # Enviar notificação
    results = await notification_service.notify_waste_detection(
        detection,
        str(image_path) if image_path and image_path.exists() else None,
        request.recipients
    )
    
    return {
        "message": "Notificação enviada",
        "results": results
    }

@app.get("/api/blockchain/chain")
async def get_blockchain():
    """Obter toda a blockchain."""
    chain = await blockchain_client.get_chain()
    return chain

@app.get("/api/blockchain/validate")
async def validate_blockchain():
    """Validar a integridade da blockchain."""
    is_valid = await blockchain_client.verify_chain()
    return {"valid": is_valid}

@app.get("/api/blockchain/detection/{detection_id}")
async def get_blockchain_detection(detection_id: str):
    """Obter o bloco da blockchain para uma detecção específica."""
    block = await blockchain_client.search_by_detection_id(detection_id)
    
    if not block:
        raise HTTPException(status_code=404, detail="Bloco não encontrado para esta detecção")
        
    return block

# Funções auxiliares para tarefas em segundo plano
async def register_in_blockchain(detection_data):
    """
    Registra uma detecção na blockchain em segundo plano.
    
    Args:
        detection_data: Dados da detecção
    """
    try:
        logger.info(f"Registrando detecção {detection_data.get('id')} na blockchain...")
        
        # Registrar na blockchain
        block_hash = await blockchain_client.register_detection(detection_data)
        
        if block_hash:
            # Atualizar o hash da blockchain na detecção
            await database.update_detection(
                detection_data.get("id"),
                {"blockchain_hash": block_hash}
            )
            logger.info(f"Detecção registrada na blockchain: {block_hash}")
        else:
            logger.error(f"Falha ao registrar na blockchain: {detection_data.get('id')}")
            
    except Exception as e:
        logger.error(f"Erro ao registrar na blockchain: {str(e)}")

async def send_notification(detection_data, image_path=None):
    """
    Envia notificações sobre uma detecção em segundo plano.
    
    Args:
        detection_data: Dados da detecção
        image_path: Caminho para a imagem da detecção (opcional)
    """
    try:
        logger.info(f"Enviando notificação para detecção {detection_data.get('id')}...")
        
        # Por simplificidade, usando uma lista fixa de destinatários
        # Em produção, seria obtido de um cadastro ou configuração
        recipients = ["5511999999999"]  # Substituir por números reais
        
        # Enviar notificação
        results = await notification_service.notify_waste_detection(
            detection_data,
            image_path,
            recipients
        )
        
        logger.info(f"Notificação enviada: {results}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {str(e)}")

# Ponto de entrada para execução direta
if __name__ == "__main__":
    import uvicorn
    
    # Definir porta padrão e host
    port = int(os.getenv("PORT", 8000))
    
    # Iniciar o servidor
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 