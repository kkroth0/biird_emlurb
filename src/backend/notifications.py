import httpx
import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('notifications')

WAHA_URL = os.getenv("WAHA_URL", "http://localhost:3000")
WAHA_TOKEN = os.getenv("WAHA_TOKEN", "your_waha_token")  


DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:3000")

class NotificationService:
    
    
    def __init__(self, 
                 waha_url: str = WAHA_URL,
                 waha_token: str = WAHA_TOKEN,
                 dashboard_url: str = DASHBOARD_URL):
        self.waha_url = waha_url
        self.waha_token = waha_token
        self.dashboard_url = dashboard_url
        
        self.waha_headers = {
            "Authorization": f"Bearer {self.waha_token}",
            "Content-Type": "application/json"
        }
        
        logger.info("Serviço de notificações inicializado.")
        
    async def send_whatsapp_text(self, phone: str, message: str) -> bool:
        try:
            url = f"{self.waha_url}/api/sendText"
            payload = {
                "chatId": f"{phone}@c.us",
                "text": message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, 
                    json=payload, 
                    headers=self.waha_headers,
                    timeout=10
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    logger.info(f"Mensagem WhatsApp enviada para {phone}")
                    return True
                else:
                    logger.error(f"Erro ao enviar mensagem WhatsApp: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {str(e)}")
            return False
            
    async def send_whatsapp_image(self, 
                                  phone: str, 
                                  image_path: str, 
                                  caption: Optional[str] = None) -> bool:
        try:
            url = f"{self.waha_url}/api/sendImage"
            
            if not Path(image_path).exists():
                logger.error(f"Imagem não encontrada: {image_path}")
                return False
                
            with open(image_path, "rb") as img_file:
                import base64
                img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
                
                payload = {
                    "chatId": f"{phone}@c.us",
                    "base64": f"data:image/jpeg;base64,{img_base64}",
                    "caption": caption or ""
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url, 
                        json=payload, 
                        headers=self.waha_headers,
                        timeout=30  
                    )
                    
                    if response.status_code == 200 or response.status_code == 201:
                        logger.info(f"Imagem WhatsApp enviada para {phone}")
                        return True
                    else:
                        logger.error(f"Erro ao enviar imagem WhatsApp: {response.status_code} - {response.text}")
                        return False
                    
        except Exception as e:
            logger.error(f"Erro ao enviar imagem WhatsApp: {str(e)}")
            return False
            
    async def notify_waste_detection(self, 
                                    detection_data: Dict[str, Any], 
                                    image_path: Optional[str] = None,
                                    recipients: Optional[List[str]] = None) -> Dict[str, bool]:
      
   
        if not recipients:
            recipients = ["551199999999"] 
            
        detection_id = detection_data.get("id")
        camera_id = detection_data.get("camera_id")
        timestamp = detection_data.get("timestamp")
        coordinates = detection_data.get("coordinates", {})
        location = f"{coordinates.get('latitude', 0)}, {coordinates.get('longitude', 0)}"
        
        dashboard_link = f"{self.dashboard_url}/detections/{detection_id}"
        
        message = (
            f"🚨 *ALERTA: Descarte Ilegal Detectado!* 🚨\n\n"
            f"📹 *Câmera:* {camera_id}\n"
            f"🕒 *Horário:* {timestamp}\n"
            f"📍 *Localização:* {location}\n\n"
            f"Para ver detalhes, acesse: {dashboard_link}"
        )
        
        results = {
            "whatsapp": False,
        }
        
        for phone in recipients:
            if image_path and Path(image_path).exists():
                results["whatsapp"] = await self.send_whatsapp_image(
                    phone, 
                    image_path, 
                    f"🚨 Descarte Ilegal Detectado! Câmera: {camera_id}, Horário: {timestamp}"
                )
                
                if not results["whatsapp"]:
                    results["whatsapp"] = await self.send_whatsapp_text(phone, message)
            else:
                results["whatsapp"] = await self.send_whatsapp_text(phone, message)
        
            
        logger.info(f"Notificação enviada para detecção {detection_id}: WhatsApp={results['whatsapp']}")
        
        return results


if __name__ == "__main__":
    import asyncio
    
    async def test_notifications():
        service = NotificationService()
        
        test_detection = {
            "id": "test-123",
            "camera_id": "camera_01",
            "timestamp": "2023-05-20T14:30:00",
            "coordinates": {
                "latitude": -8.0476,
                "longitude": -34.8770
            }
        }
        
        results = await service.notify_waste_detection(
            test_detection,
            recipients=["5511999999999"] 
        )
        
        print(f"Resultados: {results}")
    
    asyncio.run(test_notifications()) 