import aiosqlite
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "waste_detection.db"

os.makedirs(DB_DIR, exist_ok=True)

CREATE_DETECTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS detections (
    id TEXT PRIMARY KEY,
    camera_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    coordinates TEXT NOT NULL,
    detection_area REAL NOT NULL,
    waste_type TEXT NOT NULL,
    image_url TEXT,
    status TEXT NOT NULL,
    blockchain_hash TEXT,
    created_at TEXT NOT NULL
);
"""

CREATE_CAMERAS_TABLE = """
CREATE TABLE IF NOT EXISTS cameras (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    coordinates TEXT NOT NULL,
    status TEXT NOT NULL,
    last_detection TEXT
);
"""

INSERT_DETECTION = """
INSERT INTO detections (
    id, camera_id, timestamp, coordinates, detection_area, 
    waste_type, image_url, status, blockchain_hash, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

GET_DETECTION_BY_ID = """
SELECT * FROM detections WHERE id = ?;
"""

UPDATE_DETECTION = """
UPDATE detections SET status = ?, waste_type = ?, blockchain_hash = ? WHERE id = ?;
"""

GET_ALL_DETECTIONS = """
SELECT * FROM detections ORDER BY timestamp DESC;
"""

GET_DETECTIONS_BY_CAMERA = """
SELECT * FROM detections WHERE camera_id = ? ORDER BY timestamp DESC;
"""

INSERT_CAMERA = """
INSERT INTO cameras (id, name, location, coordinates, status, last_detection)
VALUES (?, ?, ?, ?, ?, ?);
"""

GET_ALL_CAMERAS = """
SELECT * FROM cameras;
"""

UPDATE_CAMERA_STATUS = """
UPDATE cameras SET status = ? WHERE id = ?;
"""

UPDATE_CAMERA_LAST_DETECTION = """
UPDATE cameras SET last_detection = ? WHERE id = ?;
"""

async def init_db():
    """Inicializar o banco de dados."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_DETECTIONS_TABLE)
        await db.execute(CREATE_CAMERAS_TABLE)
        await db.commit()

        # Inserir algumas câmeras de exemplo se a tabela estiver vazia
        cursor = await db.execute("SELECT COUNT(*) FROM cameras;")
        count = await cursor.fetchone()
        if count[0] == 0:
            sample_cameras = [
                (
                    "camera_01", 
                    "Câmera Av. Boa Viagem", 
                    "Av. Boa Viagem, 1000", 
                    json.dumps({"latitude": -8.1209, "longitude": -34.8953}),
                    "Online",
                    None
                ),
                (
                    "camera_02", 
                    "Câmera Parque da Jaqueira", 
                    "Parque da Jaqueira", 
                    json.dumps({"latitude": -8.0369, "longitude": -34.9066}),
                    "Online",
                    None
                ),
                (
                    "camera_03", 
                    "Câmera Marco Zero", 
                    "Marco Zero, Recife Antigo", 
                    json.dumps({"latitude": -8.0631, "longitude": -34.8711}),
                    "Online",
                    None
                )
            ]
            for camera in sample_cameras:
                await db.execute(INSERT_CAMERA, camera)
            await db.commit()
        
async def add_detection(detection_data: Dict[str, Any], image_url: Optional[str] = None) -> str:
    detection_id = detection_data.get("id")
    camera_id = detection_data.get("camera_id")
    timestamp = detection_data.get("timestamp")
    coordinates = json.dumps(detection_data.get("coordinates"))
    detection_area = detection_data.get("detection_area")
    waste_type = detection_data.get("waste_type", "Desconhecido")
    status = detection_data.get("status", "Aberto")
    blockchain_hash = detection_data.get("blockchain_hash")
    created_at = datetime.now().isoformat()
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            INSERT_DETECTION,
            (
                detection_id, camera_id, timestamp, coordinates, detection_area,
                waste_type, image_url, status, blockchain_hash, created_at
            )
        )
        await db.commit()
        
        # Atualizar o último timestamp de detecção da câmera
        await db.execute(UPDATE_CAMERA_LAST_DETECTION, (timestamp, camera_id))
        await db.commit()
    
    return detection_id

async def get_detection(detection_id: str) -> Dict[str, Any]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(GET_DETECTION_BY_ID, (detection_id,))
        row = await cursor.fetchone()
        
        if not row:
            return None
            
        detection = dict(row)
        detection["coordinates"] = json.loads(detection["coordinates"])
        
        return detection

async def update_detection(detection_id: str, update_data: Dict[str, Any]) -> bool:
    status = update_data.get("status")
    waste_type = update_data.get("waste_type")
    blockchain_hash = update_data.get("blockchain_hash")
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            UPDATE_DETECTION,
            (status, waste_type, blockchain_hash, detection_id)
        )
        await db.commit()
        
        return True

async def get_all_detections() -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(GET_ALL_DETECTIONS)
        rows = await cursor.fetchall()
        
        detections = []
        for row in rows:
            detection = dict(row)
            detection["coordinates"] = json.loads(detection["coordinates"])
            detections.append(detection)
            
        return detections

async def get_camera_detections(camera_id: str) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(GET_DETECTIONS_BY_CAMERA, (camera_id,))
        rows = await cursor.fetchall()
        
        detections = []
        for row in rows:
            detection = dict(row)
            detection["coordinates"] = json.loads(detection["coordinates"])
            detections.append(detection)
            
        return detections

async def get_all_cameras() -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(GET_ALL_CAMERAS)
        rows = await cursor.fetchall()
        
        cameras = []
        for row in rows:
            camera = dict(row)
            camera["coordinates"] = json.loads(camera["coordinates"])
            cameras.append(camera)
            
        return cameras

async def update_camera_status(camera_id: str, status: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(UPDATE_CAMERA_STATUS, (status, camera_id))
        await db.commit()
        
        return True 