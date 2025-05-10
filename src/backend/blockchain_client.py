import httpx
import logging
import json
from typing import Dict, Any, List, Optional
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('blockchain_client')

BLOCKCHAIN_API_URL = os.getenv("BLOCKCHAIN_API_URL", "http://localhost:8080")

class BlockchainClient:
    
    def __init__(self, api_url: str = BLOCKCHAIN_API_URL):
        self.api_url = api_url
        logger.info(f"Cliente da blockchain inicializado: {self.api_url}")
        
    async def get_chain(self) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/chain", timeout=10)
                
                if response.status_code == 200:
                    chain_data = response.json()
                    logger.info(f"Blockchain recuperada: {len(chain_data)} blocos")
                    return chain_data
                else:
                    logger.error(f"Erro ao obter a blockchain: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Erro ao obter a blockchain: {str(e)}")
            return []
            
    async def get_block(self, block_hash: str) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/blocks/{block_hash}", timeout=10)
                
                if response.status_code == 200:
                    block_data = response.json()
                    logger.info(f"Bloco recuperado: {block_hash}")
                    return block_data
                elif response.status_code == 404:
                    logger.warning(f"Bloco não encontrado: {block_hash}")
                    return None
                else:
                    logger.error(f"Erro ao obter o bloco: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Erro ao obter o bloco: {str(e)}")
            return None
            
    async def add_block(self, data: Dict[str, Any]) -> Optional[str]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/mine", 
                    json={"data": data},
                    timeout=15  # Tempo maior para mineração
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    block_hash = result.get("hash")
                    logger.info(f"Novo bloco adicionado à blockchain: {block_hash}")
                    return block_hash
                else:
                    logger.error(f"Erro ao adicionar bloco: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Erro ao adicionar bloco: {str(e)}")
            return None
            
    async def verify_chain(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/validate", timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    is_valid = result.get("valid", False)
                    logger.info(f"Validação da blockchain: {is_valid}")
                    return is_valid
                else:
                    logger.error(f"Erro ao validar a blockchain: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Erro ao validar a blockchain: {str(e)}")
            return False
            
    async def search_by_detection_id(self, detection_id: str) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/search", 
                    params={"detection_id": detection_id},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result:
                        logger.info(f"Bloco encontrado para detecção {detection_id}")
                        return result
                    else:
                        logger.warning(f"Nenhum bloco encontrado para detecção {detection_id}")
                        return None
                else:
                    logger.error(f"Erro na busca por detecção: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Erro na busca por detecção: {str(e)}")
            return None
            
    async def register_detection(self, detection_data: Dict[str, Any]) -> Optional[str]:
        try:
            blockchain_data = {
                "detection_id": detection_data.get("id"),
                "camera_id": detection_data.get("camera_id"),
                "timestamp": detection_data.get("timestamp"),
                "coordinates": detection_data.get("coordinates"),
                "waste_type": detection_data.get("waste_type", "Desconhecido"),
                "detection_area": detection_data.get("detection_area"),
                "status": detection_data.get("status", "Aberto"),
                "image_reference": detection_data.get("image_url")
            }
            
            block_hash = await self.add_block(blockchain_data)
            
            if block_hash:
                logger.info(f"Detecção {detection_data.get('id')} registrada na blockchain: {block_hash}")
                return block_hash
            else:
                logger.error(f"Falha ao registrar detecção {detection_data.get('id')} na blockchain")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao registrar detecção na blockchain: {str(e)}")
            return None

if __name__ == "__main__":
    import asyncio
    
    async def test_blockchain():
        client = BlockchainClient()
        
        test_data = {
            "id": "test-456",
            "camera_id": "camera_02",
            "timestamp": "2023-05-21T10:15:00",
            "coordinates": {
                "latitude": -8.0369,
                "longitude": -34.9066
            },
            "waste_type": "Entulho",
            "detection_area": 2500.5,
            "status": "Aberto",
            "image_url": "/static/detections/test-456.jpg"
        }
        
        block_hash = await client.register_detection(test_data)
        print(f"Bloco adicionado: {block_hash}")
        
        chain = await client.get_chain()
        print(f"Blockchain: {len(chain)} blocos")
        
        is_valid = await client.verify_chain()
        print(f"Blockchain válida: {is_valid}")
        
        if block_hash:
            block = await client.get_block(block_hash)
            print(f"Bloco recuperado: {block}")
            
            detection_block = await client.search_by_detection_id("test-456")
            print(f"Bloco por detecção: {detection_block}")
    
    asyncio.run(test_blockchain()) 