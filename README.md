# Sistema de Monitoramento de Descarte Ilegal de Resíduos

## Visão Geral

Este projeto é um POC/MVP para um sistema integrado de monitoramento de descarte ilegal de resíduos em Recife. O sistema utiliza visão computacional para analisar imagens de câmeras, detectar possíveis descartes ilegais, emitir alertas e registrar os eventos em uma blockchain para auditoria imutável.

## Componentes Principais

- **Módulo de Visão Computacional**: Detecta descartes ilegais em imagens estáticas usando Python e OpenCV.
- **Backend/API**: Recebe notificações de descarte, registra eventos e fornece APIs para o frontend.
- **Frontend Web**: Dashboard interativo com mapa e lista de eventos usando React e Leaflet.js.
- **Blockchain**: Registro imutável de eventos de descarte implementado em Go.
- **Sistema de Notificações**: Envia alertas via WhatsApp/Telegram usando WAHA ou Bot API.

## Estrutura do Projeto

```
emlurb2.0/
├── src/
│   ├── computer_vision/  # Módulo de detecção de descartes ilegais
│   ├── backend/          # Servidor API e lógica de negócios
│   ├── frontend/         # Interface web para visualização
│   ├── blockchain/       # Implementação da blockchain em Go
│   └── data/             # Dados de exemplo e configurações
│       └── sample_images/# Imagens de exemplo para simulação
├── README.md
└── requirements.txt      # Dependências Python
```

## Como Executar

(Instruções detalhadas de execução serão adicionadas conforme o desenvolvimento avança)

## Tecnologias Utilizadas

- Python + OpenCV para visão computacional
- FastAPI para o backend
- React e Leaflet.js para o frontend
- Go para a implementação da blockchain
- WAHA/Telegram Bot API para notificações

## Contribuição

Este projeto foi desenvolvido como parte de um hackathon e visa demonstrar a viabilidade de um sistema de monitoramento de descarte ilegal de resíduos com tecnologias open-source. 