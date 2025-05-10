from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
import uuid
import logging
from pathlib import Path
import json

# Criar a aplicação Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS

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

@app.route('/')
def root():
    """Endpoint raiz para verificar se a API está funcionando."""
    return jsonify({"message": "API de Monitoramento de Descarte Ilegal funcionando"})

@app.route('/health')
def health_check():
    """Verificação de saúde da API."""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/static/<path:path>')
def serve_static(path):
    """Servir arquivos estáticos."""
    return send_from_directory(str(STATIC_DIR), path)

# Endpoints para câmeras
@app.route('/api/cameras')
def get_cameras():
    """Obter todas as câmeras cadastradas."""
    return jsonify(cameras)

@app.route('/api/cameras/<camera_id>/detections')
def get_camera_detections(camera_id):
    """Obter todas as detecções de uma câmera específica."""
    camera_detections = [d for d in detections if d["camera_id"] == camera_id]
    return jsonify(camera_detections)

@app.route('/api/cameras/<camera_id>/status', methods=['PUT'])
def update_camera_status(camera_id):
    """Atualizar o status de uma câmera."""
    data = request.json
    status = data.get('status')
    
    if status not in ["Online", "Offline", "Manutenção"]:
        return jsonify({"error": "Status inválido"}), 400
        
    for camera in cameras:
        if camera["id"] == camera_id:
            camera["status"] = status
            return jsonify({"message": f"Status da câmera {camera_id} atualizado para {status}"})
            
    return jsonify({"error": "Câmera não encontrada"}), 404

# Endpoints para detecções de descarte
@app.route('/api/waste-detections')
def get_waste_detections():
    """
    Obter todas as detecções de descarte.
    
    Parâmetros:
    - camera_id: Filtrar por câmera específica
    - status: Filtrar por status
    - limit: Limite de resultados
    """
    camera_id = request.args.get('camera_id')
    status = request.args.get('status')
    limit = int(request.args.get('limit', 50))
    
    result = detections
    
    if camera_id:
        result = [d for d in result if d["camera_id"] == camera_id]
        
    if status:
        result = [d for d in result if d["status"] == status]
        
    return jsonify(result[:limit])

@app.route('/api/waste-detections/<detection_id>')
def get_waste_detection(detection_id):
    """Obter uma detecção específica pelo ID."""
    for detection in detections:
        if detection["id"] == detection_id:
            return jsonify(detection)
            
    return jsonify({"error": "Detecção não encontrada"}), 404

@app.route('/api/waste-detection', methods=['POST'])
def create_waste_detection():
    """
    Criar uma nova detecção de descarte.
    
    Este endpoint é usado pelo módulo de visão computacional para
    registrar uma nova detecção.
    """
    try:
        # Obter dados do formulário
        camera_id = request.form['camera_id']
        timestamp = request.form['timestamp']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        detection_area = float(request.form['detection_area'])
        waste_type = request.form.get('waste_type', 'Desconhecido')
        
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
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                # Gerar nome do arquivo baseado no ID da detecção
                file_extension = os.path.splitext(image.filename)[1]
                image_filename = f"{detection_id}{file_extension}"
                image_path = DETECTIONS_DIR / image_filename
                
                # Salvar o arquivo
                image.save(image_path)
                
                # Gerar URL relativa
                image_url = f"/static/detections/{image_filename}"
                detection["image_url"] = image_url
            
        # Adicionar à lista de detecções
        detections.append(detection)
        
        return jsonify({
            "message": "Detecção registrada com sucesso",
            "id": detection_id,
            "image_url": image_url
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar detecção: {str(e)}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/api/waste-detections/<detection_id>', methods=['PUT'])
def update_waste_detection(detection_id):
    """Atualizar uma detecção existente."""
    data = request.json
    status = data.get('status')
    waste_type = data.get('waste_type')
    
    for detection in detections:
        if detection["id"] == detection_id:
            if status is not None:
                detection["status"] = status
            if waste_type is not None:
                detection["waste_type"] = waste_type
            return jsonify({"message": "Detecção atualizada com sucesso"})
            
    return jsonify({"error": "Detecção não encontrada"}), 404

@app.route('/api/blockchain/validation')
def validate_blockchain():
    """Simulação da validação da blockchain."""
    return jsonify({"valid": True})

if __name__ == "__main__":
    # Definir porta padrão e host
    port = int(os.getenv("PORT", 8000))
    
    # Iniciar o servidor
    app.run(host="0.0.0.0", port=port, debug=True) 