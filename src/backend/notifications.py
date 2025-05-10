import httpx
import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('notifications')

# Configurações
WAHA_URL = os.getenv("WAHA_URL", "http://localhost:3000")
WAHA_TOKEN = os.getenv("WAHA_TOKEN", "your_waha_token")  # Token de acesso WAHA

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_telegram_bot_token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_telegram_chat_id")

# URL base para acessar o dashboard
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:3000")

class NotificationService:
    """Serviço para envio de notificações via WhatsApp e Telegram."""
    
    def __init__(self, 
                 waha_url: str = WAHA_URL,
                 waha_token: str = WAHA_TOKEN,
                 telegram_token: str = TELEGRAM_BOT_TOKEN,
                 telegram_chat_id: str = TELEGRAM_CHAT_ID,
                 dashboard_url: str = DASHBOARD_URL):
        """
        Inicializa o serviço de notificações.
        
        Args:
            waha_url: URL da API WAHA
            waha_token: Token de autenticação da API WAHA
            telegram_token: Token do bot do Telegram
            telegram_chat_id: ID do chat/grupo do Telegram
            dashboard_url: URL base do dashboard
        """
        self.waha_url = waha_url
        self.waha_token = waha_token
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.dashboard_url = dashboard_url
        
        # Headers para as requisições WAHA
        self.waha_headers = {
            "Authorization": f"Bearer {self.waha_token}",
            "Content-Type": "application/json"
        }
        
        logger.info("Serviço de notificações inicializado.")
        
    async def send_whatsapp_text(self, phone: str, message: str) -> bool:
        """
        Envia uma mensagem de texto via WhatsApp.
        
        Args:
            phone: Número de telefone (com código do país, sem +)
            message: Texto da mensagem
            
        Returns:
            bool: True se a mensagem foi enviada com sucesso
        """
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
        """
        Envia uma imagem via WhatsApp.
        
        Args:
            phone: Número de telefone (com código do país, sem +)
            image_path: Caminho para a imagem
            caption: Legenda da imagem (opcional)
            
        Returns:
            bool: True se a imagem foi enviada com sucesso
        """
        try:
            url = f"{self.waha_url}/api/sendImage"
            
            # Verificar se o arquivo existe
            if not Path(image_path).exists():
                logger.error(f"Imagem não encontrada: {image_path}")
                return False
                
            # Preparar os dados para envio
            with open(image_path, "rb") as img_file:
                # Obter o base64 da imagem
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
                        timeout=30  # Aumento do timeout para uploads de imagem
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
            
    async def send_telegram_message(self, message: str) -> bool:
        """
        Envia uma mensagem de texto via Telegram.
        
        Args:
            message: Texto da mensagem
            
        Returns:
            bool: True se a mensagem foi enviada com sucesso
        """
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    logger.info("Mensagem Telegram enviada com sucesso")
                    return True
                else:
                    logger.error(f"Erro ao enviar mensagem Telegram: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem Telegram: {str(e)}")
            return False
            
    async def send_telegram_photo(self, 
                                 image_path: str, 
                                 caption: Optional[str] = None) -> bool:
        """
        Envia uma foto via Telegram.
        
        Args:
            image_path: Caminho para a imagem
            caption: Legenda da foto (opcional)
            
        Returns:
            bool: True se a foto foi enviada com sucesso
        """
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendPhoto"
            
            # Verificar se o arquivo existe
            if not Path(image_path).exists():
                logger.error(f"Imagem não encontrada: {image_path}")
                return False
                
            # Preparar o formulário multipart
            files = {"photo": open(image_path, "rb")}
            data = {
                "chat_id": self.telegram_chat_id,
                "caption": caption or "",
                "parse_mode": "Markdown"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, 
                    files=files, 
                    data=data,
                    timeout=30  # Aumento do timeout para uploads de imagem
                )
                
                if response.status_code == 200:
                    logger.info("Foto Telegram enviada com sucesso")
                    return True
                else:
                    logger.error(f"Erro ao enviar foto Telegram: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Erro ao enviar foto Telegram: {str(e)}")
            return False
            
    async def notify_waste_detection(self, 
                                    detection_data: Dict[str, Any], 
                                    image_path: Optional[str] = None,
                                    recipients: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Notifica sobre uma detecção de descarte ilegal via WhatsApp e Telegram.
        
        Args:
            detection_data: Dados da detecção
            image_path: Caminho para a imagem da detecção (opcional)
            recipients: Lista de números de telefone para notificar (opcional)
            
        Returns:
            Dict[str, bool]: Status do envio para cada canal
        """
        # Se não for especificado, usar uma lista padrão de números
        if not recipients:
            recipients = ["551199999999"]  # Substituir por números reais
            
        detection_id = detection_data.get("id")
        camera_id = detection_data.get("camera_id")
        timestamp = detection_data.get("timestamp")
        coordinates = detection_data.get("coordinates", {})
        location = f"{coordinates.get('latitude', 0)}, {coordinates.get('longitude', 0)}"
        
        # Link para o dashboard
        dashboard_link = f"{self.dashboard_url}/detections/{detection_id}"
        
        # Construir a mensagem
        message = (
            f"🚨 *ALERTA: Descarte Ilegal Detectado!* 🚨\n\n"
            f"📹 *Câmera:* {camera_id}\n"
            f"🕒 *Horário:* {timestamp}\n"
            f"📍 *Localização:* {location}\n\n"
            f"Para ver detalhes, acesse: {dashboard_link}"
        )
        
        # Resultados do envio
        results = {
            "whatsapp": False,
            "telegram": False
        }
        
        # Enviar para WhatsApp
        for phone in recipients:
            # Tentar enviar com imagem se disponível
            if image_path and Path(image_path).exists():
                results["whatsapp"] = await self.send_whatsapp_image(
                    phone, 
                    image_path, 
                    f"🚨 Descarte Ilegal Detectado! Câmera: {camera_id}, Horário: {timestamp}"
                )
                
                # Se falhar com imagem, tentar só texto
                if not results["whatsapp"]:
                    results["whatsapp"] = await self.send_whatsapp_text(phone, message)
            else:
                # Enviar só texto se não tiver imagem
                results["whatsapp"] = await self.send_whatsapp_text(phone, message)
        
        # Enviar para Telegram
        if image_path and Path(image_path).exists():
            results["telegram"] = await self.send_telegram_photo(image_path, message)
        else:
            results["telegram"] = await self.send_telegram_message(message)
            
        # Logar resultados
        logger.info(f"Notificação enviada para detecção {detection_id}: WhatsApp={results['whatsapp']}, Telegram={results['telegram']}")
        
        return results


# Para testes
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
        
        # Aqui você pode testar enviando para um número real
        results = await service.notify_waste_detection(
            test_detection,
            recipients=["5511999999999"]  # Substituir por um número real para testar
        )
        
        print(f"Resultados: {results}")
    
    asyncio.run(test_notifications()) 