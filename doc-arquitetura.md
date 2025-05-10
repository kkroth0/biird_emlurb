# Documentação de Arquitetura: Sistema de Monitoramento de Descarte Ilegal

Este documento descreve a arquitetura técnica do sistema de monitoramento de descarte ilegal de resíduos, desenvolvido como POC/MVP.

## Visão Geral do Sistema

O sistema é composto por quatro módulos principais:

1. **Módulo de Visão Computacional**: Detecta descartes ilegais em imagens utilizando OpenCV
2. **Backend API**: Recebe, processa e armazena detecções de descartes
3. **Frontend Web**: Interface para visualização e gestão das detecções
4. **Blockchain**: Registro imutável dos eventos para auditoria

## Arquitetura de Alto Nível

```
┌─────────────────┐     ┌─────────────────┐      ┌─────────────────┐
│   Detecção via  │     │                 │      │                 │
│ Visão Computac. │────▶│   Backend API   │◀────▶│  Frontend Web   │
│    (Python)     │     │    (FastAPI)    │      │     (React)     │
└─────────────────┘     └────────┬────────┘      └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐      ┌─────────────────┐
                        │   Blockchain    │      │Notificações     │
                        │      (Go)       │      │(WhatsApp/Telegr)│
                        └─────────────────┘      └─────────────────┘
```

## Descrição dos Componentes

### 1. Módulo de Visão Computacional

**Tecnologias:** Python, OpenCV

Responsável por:
- Analisar imagens estáticas que simulam câmeras de vigilância
- Detectar objetos de interesse (possíveis descartes) usando subtração de fundo
- Reportar detecções ao backend via API REST

Para executar:
```bash
cd src/computer_vision
python run_detector.py --cameras-folder ../data/sample_images --backend-url http://localhost:8000
```

### 2. Backend API

**Tecnologias:** Python, FastAPI, SQLite

Responsável por:
- Receber notificações de detecções do módulo de visão 
- Armazenar detecções em banco de dados
- Registrar detecções na blockchain
- Enviar notificações via WhatsApp/Telegram
- Fornecer endpoints para o frontend consumir

Para executar:
```bash
cd src/backend
python run.py --reload
```

Endpoints principais:
- `GET /api/cameras` - Lista todas as câmeras
- `GET /api/waste-detections` - Lista todas as detecções
- `POST /api/waste-detection` - Cria uma nova detecção
- `PUT /api/waste-detections/{detection_id}` - Atualiza uma detecção
- `GET /api/blockchain/chain` - Obtém a blockchain
- `GET /api/blockchain/validate` - Valida a integridade da blockchain

### 3. Frontend Web

**Tecnologias:** React, Chakra UI, Leaflet

Responsável por:
- Exibir mapa interativo com câmeras e detecções
- Listar detecções em formato tabular com filtros
- Permitir visualização de detalhes das detecções
- Facilitar a gestão de status (atendimento, conclusão)
- Fornecer visualização da blockchain para auditoria

Para executar:
```bash
cd src/frontend
npm install
npm start
```

### 4. Blockchain

**Tecnologias:** Go, Gin

Responsável por:
- Manter um registro imutável de todas as detecções
- Fornecer mecanismos de verificação de integridade
- Expor APIs para registro e consulta de blocos

Para executar:
```bash
cd src/blockchain
go mod download
go run main.go
```

## Fluxo de Dados

1. O módulo de visão computacional detecta um possível descarte ilegal em uma imagem
2. O módulo envia a detecção (imagem + metadados) para o backend via API
3. O backend armazena a detecção no banco de dados
4. O backend registra a detecção na blockchain como registro imutável
5. O backend envia notificações via WhatsApp/Telegram para os fiscais
6. O frontend consulta o backend para exibir as detecções no mapa e na tabela
7. Os fiscais podem atualizar o status das detecções (em atendimento, concluído)
8. Qualquer atualização de status também é registrada na blockchain

## Configuração do Ambiente

### Requisitos

- Python 3.8+
- Node.js 14+
- Go 1.21+
- SQLite
- WAHA (WhatsApp HTTP API) ou token do Telegram Bot

### Variáveis de Ambiente

**Backend**:
```
BLOCKCHAIN_API_URL=http://localhost:8080
WAHA_URL=http://localhost:3000
WAHA_TOKEN=your_waha_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
DASHBOARD_URL=http://localhost:3000
```

**Frontend**:
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_BLOCKCHAIN_URL=http://localhost:8080
```

## Segurança e Escalabilidade

Este projeto é um POC/MVP e, portanto, não inclui todas as medidas de segurança necessárias para um ambiente de produção. Para produção, recomenda-se:

- Implementar autenticação e autorização
- Utilizar HTTPS para todas as comunicações
- Considerar bancos de dados mais robustos (PostgreSQL, MongoDB)
- Implementar controle de acesso baseado em papéis
- Adicionar testes automatizados

## Limitações da POC

- A detecção de visão computacional usa técnicas simples para demonstração
- A blockchain é uma implementação simplificada, não distribuída
- Não há implementação real de WAHA - exigiria um número de telefone real
- As imagens são simuladas e não vêm de câmeras reais

## Próximos Passos

- Integração com câmeras reais ou feeds de vídeo
- Melhoria nos algoritmos de detecção (uso de modelos de deep learning)
- Expansão das funcionalidades do dashboard
- Implementação de autenticação e autorização
- Testes com usuários reais e em ambiente real 