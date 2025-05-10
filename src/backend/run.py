#!/usr/bin/env python3
"""
Script para iniciar o backend do sistema de monitoramento de descarte ilegal.
"""

import os
import logging
import argparse
import uvicorn

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('backend_runner')

def main():
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Servidor Backend de Monitoramento de Descarte Ilegal')
    
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host para executar o servidor (padrão: 0.0.0.0)')
    
    parser.add_argument('--port', type=int, default=8000,
                        help='Porta para executar o servidor (padrão: 8000)')
    
    parser.add_argument('--reload', action='store_true',
                        help='Ativar o recarregamento automático do código (para desenvolvimento)')
    
    parser.add_argument('--workers', type=int, default=1,
                        help='Número de workers (padrão: 1)')
    
    args = parser.parse_args()
    
    # Configurar ambiente
    os.environ.setdefault('PYTHONPATH', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Iniciar servidor
    logger.info(f"Iniciando o servidor backend em {args.host}:{args.port}")
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
    )

if __name__ == "__main__":
    main() 