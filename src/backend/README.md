# 🦅 BiiRD - Instalação do Backend

Este é o backend do sistema, construído com FastAPI (Python) e parcialmente integrado com uma blockchain em Go.

![image](https://github.com/user-attachments/assets/87342879-da1f-4c02-a199-851cece43feb)

## Configuração do Ambiente

1. Instale as dependências Python:

```bash
pip install -r ../../requirements.txt
```

2. Configure as variáveis de ambiente (opcional):

```bash
# API da blockchain
export BLOCKCHAIN_API_URL=http://localhost:8080

# Configurações da API WAHA para WhatsApp
export WAHA_URL=http://localhost:3000
export WAHA_TOKEN=your_waha_token

# URL do Dashboard para links em notificações
export DASHBOARD_URL=http://localhost:3000
```

## Executando o Backend

Para executar o backend em modo de desenvolvimento:

```bash
python run.py --reload
```

O servidor estará disponível em [http://localhost:8000](http://localhost:8000).

## Estrutura do Backend

- `main.py` - Arquivo principal com os endpoints da API
- `models.py` - Modelos de dados com Pydantic 
- `database.py` - Operações de banco de dados com SQLite
- `blockchain_client.py` - Cliente para comunicação com a blockchain
- `notifications.py` - Serviço para envio de notificações

## Endpoints Principais

- `GET /api/cameras` - Lista todas as câmeras
- `GET /api/waste-detections` - Lista todas as detecções
- `POST /api/waste-detection` - Cria uma nova detecção
- `PUT /api/waste-detections/{detection_id}` - Atualiza uma detecção
- `GET /api/blockchain/chain` - Obtém a blockchain
- `GET /api/blockchain/validate` - Valida a integridade da blockchain

## Integração com Visão Computacional (Em andamento)

O backend recebe notificações do módulo de visão computacional quando um descarte ilegal é detectado. As detecções são registradas no banco de dados e na blockchain, e notificações são enviadas via WhatsApp
