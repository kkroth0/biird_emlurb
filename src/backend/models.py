from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class WasteDetection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    camera_id: str
    timestamp: datetime
    coordinates: Coordinates
    detection_area: float
    waste_type: str = "Desconhecido"
    image_url: Optional[str] = None
    status: str = "Aberto"  # "Aberto", "Em Atendimento", "Concluído"
    blockchain_hash: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "camera_id": "camera_01",
                "timestamp": "2023-05-20T14:30:00",
                "coordinates": {
                    "latitude": -8.0476,
                    "longitude": -34.8770
                },
                "detection_area": 1500.0,
                "waste_type": "Desconhecido",
                "image_url": "/static/detections/123e4567.jpg",
                "status": "Aberto",
                "blockchain_hash": "0x1a2b3c4d5e6f..."
            }
        }

class WasteDetectionCreate(BaseModel):
    camera_id: str
    timestamp: datetime
    coordinates: Coordinates
    detection_area: float
    waste_type: str = "Desconhecido"

class WasteDetectionUpdate(BaseModel):
    status: Optional[str] = None
    waste_type: Optional[str] = None
    blockchain_hash: Optional[str] = None

class Camera(BaseModel):
    id: str
    name: str
    location: str
    coordinates: Coordinates
    status: str = "Online"  # "Online", "Offline", "Manutenção"
    last_detection: Optional[datetime] = None

class NotificationRequest(BaseModel):
    detection_id: str
    recipients: List[str]
    message: Optional[str] = None

class BlockchainTransaction(BaseModel):
    hash: str
    detection_id: str
    timestamp: datetime
    block_number: int
    data: Dict[str, Any] 