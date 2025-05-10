from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import uuid
import logging
from pathlib import Path
import json

# Criar a aplicação FastAPI
app = FastAPI(
    title="API de Monitoramento de Descarte Ilegal",
    description="API para o sistema de monitoramento de descarte ilegal de resíduos",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('backend')

# Configurar diretório para salvar imagens
STATIC_DIR = Path(__file__).parent.parent / "data" / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
DETECTIONS_DIR = STATIC_DIR / "detections"

# Garantir que os diretórios existem
for dir_path in [STATIC_DIR, UPLOADS_DIR, DETECTIONS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Montar o diretório estático para servir imagens
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Dados em memória para o MVP (em produção, usar banco de dados)
cameras = [
    {
        "id": "camera_01",
        "name": "Câmera Entrada Parque",
        "location": "Parque da Jaqueira",
        "coordinates": {
            "latitude": -8.0376,
            "longitude": -34.8970
        },
        "status": "Online"
    },
    {
        "id": "camera_02",
        "name": "Câmera Avenida Principal",
        "location": "Av. Boa Viagem",
        "coordinates": {
            "latitude": -8.1176,
            "longitude": -34.8970
        },
        "status": "Online"
    }
]

detections = [
    {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "camera_id": "camera_01",
        "timestamp": "2023-05-20T14:30:00",
        "coordinates": {
            "latitude": -8.0376,
            "longitude": -34.8970
        },
        "detection_area": 1500.0,
        "waste_type": "Desconhecido",
        "image_url": "/static/detections/sample.jpg",
        "status": "Aberto",
        "blockchain_hash": "0x1a2b3c4d5e6f..."
    }
]

@app.get("/")
async def root():
    """Endpoint raiz para verificar se a API está funcionando."""
    return {"message": "API de Monitoramento de Descarte Ilegal funcionando"}

@app.get("/health")
async def health_check():
    """Verificação de saúde da API."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Endpoints para câmeras
@app.get("/api/cameras")
async def get_cameras():
    """Obter todas as câmeras cadastradas."""
    return cameras

@app.get("/api/cameras/{camera_id}/detections")
async def get_camera_detections(camera_id: str):
    """Obter todas as detecções de uma câmera específica."""
    camera_detections = [d for d in detections if d["camera_id"] == camera_id]
    return camera_detections

@app.put("/api/cameras/{camera_id}/status")
async def update_camera_status(camera_id: str, status: str):
    """Atualizar o status de uma câmera."""
    if status not in ["Online", "Offline", "Manutenção"]:
        raise HTTPException(status_code=400, detail="Status inválido")
        
    for camera in cameras:
        if camera["id"] == camera_id:
            camera["status"] = status
            return {"message": f"Status da câmera {camera_id} atualizado para {status}"}
            
    raise HTTPException(status_code=404, detail="Câmera não encontrada")

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
    result = detections
    
    if camera_id:
        result = [d for d in result if d["camera_id"] == camera_id]
        
    if status:
        result = [d for d in result if d["status"] == status]
        
    return result[:limit]

@app.get("/api/waste-detections/{detection_id}")
async def get_waste_detection(detection_id: str):
    """Obter uma detecção específica pelo ID."""
    for detection in detections:
        if detection["id"] == detection_id:
            return detection
            
    raise HTTPException(status_code=404, detail="Detecção não encontrada")

@app.post("/api/waste-detection")
async def create_waste_detection(
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
        detection = {
            "id": detection_id,
            "camera_id": camera_id,
            "timestamp": parsed_timestamp.isoformat(),
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "detection_area": detection_area,
            "waste_type": waste_type,
            "status": "Aberto",
            "blockchain_hash": None
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
            detection["image_url"] = image_url
            
        # Adicionar à lista de detecções
        detections.append(detection)
        
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
    status: Optional[str] = None,
    waste_type: Optional[str] = None
):
    """Atualizar uma detecção existente."""
    for detection in detections:
        if detection["id"] == detection_id:
            if status is not None:
                detection["status"] = status
            if waste_type is not None:
                detection["waste_type"] = waste_type
            return {"message": "Detecção atualizada com sucesso"}
            
    raise HTTPException(status_code=404, detail="Detecção não encontrada")

@app.get("/api/blockchain/validation")
async def validate_blockchain():
    """Simulação da validação da blockchain."""
    return {"valid": True}

# Ponto de entrada para execução direta
if __name__ == "__main__":
    import uvicorn
    
    # Definir porta padrão e host
    port = int(os.getenv("PORT", 8000))
    
    # Iniciar o servidor
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 