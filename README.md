# BiiRD - Base de Inteligência e Inovação do Recife para Descartes

## Visão Geral

Este projeto é uma POC (Prova de Conceito) para um sistema integrado de monitoramento de descarte ilegal de resíduos em Recife. O sistema utiliza visão computacional para analisar imagens de câmeras, detectar possíveis descartes ilegais, emitir alertas e registrar os eventos em uma blockchain para auditoria imutável.

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
- WAHA Whatsapp API para notificações

## Contribuição

Este projeto foi desenvolvido como parte do Hacker Cidadão 13.0 e visa demonstrar a viabilidade de um sistema de monitoramento de descarte ilegal de resíduos com tecnologias open-source. 
## Desenvolvedores

<table>
    <tr>
    <td widith:"90px" align="center"><a href="https://github.com/matheuslimaandrade"><img src="https://avatars.githubusercontent.com/u/90625499?v=4" width="90px;" alt="Matheus Lima"/><br /><sub><b>Matheus Andrade</b></sub></a><br />Desenvolvimento</td>
    <td align="center"><a href="https://github.com/luizwebnet"><img src="https://avatars.githubusercontent.com/u/98424992?v=4" width="90px;" alt="Samuel Lemos "/><br /><sub><b>Luiz Penna</b></sub></a><br />Desenvolvimento</td>

## Licença
>Você pode checar a licença completa [aqui](https://github.com/IgorAntun/node-chat/blob/master/LICENSE)

Esse projeto é lincenciado pelos termos da licença **MIT**.

