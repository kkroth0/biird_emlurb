# 🦅 BiiRD - Instalação do Backend 

O backend é construído com FastAPI (Python) e gerencia as detecções de descartes ilegais, integrando-se com a blockchain para registro imutável e enviando notificações via WhatsApp.

Obs: A integração de notificações ainda está em andamento.

![image](https://github.com/user-attachments/assets/87342879-da1f-4c02-a199-851cece43feb)

## Pré-requisitos

- Python 3.13
- SQLite
- WAHA (para integração com WhatsApp)

## Instalação

### 1. Configuração do Ambiente Virtual

Recomendamos a criação de um ambiente virtual para isolar as dependências:

```bash
# Criar o ambiente virtual
python -m venv .venv

# Ativar o ambiente (Windows)
.\.venv\Scripts\activate

# Ativar o ambiente (Linux/Mac)
source .venv/bin/activate
```

### 2. Instalação das Dependências

```bash
# Navegar para o diretório do backend
cd src/backend

# Instalar as dependências
pip install -r ../../requirements.txt
```

### 3. Configuração das Variáveis de Ambiente

Crie um arquivo `.env` no diretório do backend com as seguintes variáveis:

```
# API da blockchain
BLOCKCHAIN_API_URL=http://localhost:8080

# Configurações da API WAHA para WhatsApp
WAHA_URL=http://localhost:3000
WAHA_TOKEN=your_waha_token

# URL do Dashboard para links em notificações
DASHBOARD_URL=http://localhost:3000
```

## Execução

Para iniciar o servidor em modo de desenvolvimento:

```bash
# A partir do diretório do backend
python run.py --reload
```

O servidor estará disponível em [http://localhost:8000](http://localhost:8000).

## Estrutura de Arquivos

```
src/backend/
│
├── main.py              # Arquivo principal com os endpoints da API
├── models.py            # Modelos de dados com Pydantic
├── database.py          # Operações de banco de dados com SQLite
├── blockchain_client.py # Cliente para comunicação com a blockchain
├── notifications.py     # Serviço para envio de notificações
└── run.py               # Script para iniciar o servidor
```

## Endpoints da API

### Câmeras
- `GET /api/cameras` - Lista todas as câmeras
- `POST /api/cameras` - Adiciona uma nova câmera
- `GET /api/cameras/{camera_id}` - Obtém detalhes de uma câmera específica

### Detecções de Descarte
- `GET /api/waste-detections` - Lista todas as detecções
- `POST /api/waste-detection` - Cria uma nova detecção
- `GET /api/waste-detections/{detection_id}` - Obtém detalhes de uma detecção
- `PUT /api/waste-detections/{detection_id}` - Atualiza uma detecção

### Blockchain
- `GET /api/blockchain/chain` - Obtém a cadeia de blocos
- `GET /api/blockchain/validate` - Valida a integridade da blockchain

## Integração com Outros Módulos

### Visão Computacional
O backend recebe notificações do módulo de visão computacional quando um descarte ilegal é detectado, processando e armazenando as detecções.

### Blockchain
Todas as detecções e alterações de status são registradas na blockchain para garantir um histórico imutável.

### Notificações
O sistema envia notificações automáticas via WhatsApp para alertar os fiscais sobre novas detecções.

## Resolução de Problemas

### Incompatibilidade com Python 3.13
Certifique-se de que está usando as versões corretas de Pydantic e FastAPI:

```bash
pip install pydantic>=2.0.0 fastapi>=0.100.0
```

### Erro na Conexão com a Blockchain
Verifique se o serviço da blockchain está em execução e acessível na URL configurada.

### Falha no Envio de Notificações
Confirme se o serviço WAHA está configurado corretamente e se o token de acesso é válido.
