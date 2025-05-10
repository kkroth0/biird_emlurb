# 🦅BiiRD - Instalação da Blockchain 

Este componente implementa uma blockchain simples em Go para registrar detecções de descarte ilegal de resíduos de forma imutável e auditável.

## Funcionalidades

- Registro imutável de eventos de detecção
- Proof of Work simples para validação
- API HTTP para interação
- Persistência em disco via JSON
- Verificação de integridade da cadeia

## Requisitos

- Go 1.21 ou superior
- Gin Framework (instalado automaticamente via go modules)

## Executando a Blockchain

Para executar a blockchain:

```bash
# Baixar dependências
go mod download

# Compilar e executar
go run main.go
```

O servidor blockchain estará disponível em [http://localhost:8080](http://localhost:8080).

## Endpoints da API

- `GET /health` - Verificação de saúde do serviço
- `GET /chain` - Obtém toda a cadeia de blocos
- `POST /mine` - Adiciona um novo bloco à chain
- `GET /validate` - Verifica a integridade da blockchain
- `GET /blocks/:hash` - Obtém um bloco específico pelo hash
- `GET /search` - Busca um bloco pelos dados (por exemplo, por detection_id)

## Exemplo de Uso

Para adicionar um novo bloco:

Poweshell (Recomendado)
```
Invoke-RestMethod -Uri "http://localhost:8080/mine" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"data": {"detection_id": "abc123", "camera_id": "camera_01", "timestamp": "2023-01-01T12:00:00Z", "coordinates": {"latitude": -8.0476, "longitude": -34.8770}, "waste_type": "Entulho"}}'
```
CMD
```
curl -X POST http://localhost:8080/mine \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "detection_id": "abc123",
      "camera_id": "camera_01",
      "timestamp": "2023-01-01T12:00:00Z",
      "coordinates": {"latitude": -8.0476, "longitude": -34.8770},
      "waste_type": "Entulho"
    }
  }'
```

## Armazenamento

Por padrão, a blockchain é armazenada em `./data/blockchain.json` e é persistida entre reinicializações do serviço.

## Integração com o Backend (Em andamento)

Esta blockchain é consumida pelo backend Python através do componente `blockchain_client.py`, que fornece uma interface para registrar eventos e consultar a blockchain. 