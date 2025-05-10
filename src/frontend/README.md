# Frontend do Sistema de Monitoramento de Descarte Ilegal

Este é o frontend do sistema, construído com React, Chakra UI e React Leaflet.

## Configuração do Ambiente

1. Instale as dependências:

```bash
npm install
```

2. Configure as variáveis de ambiente:

Crie um arquivo `.env.local` na raiz do projeto frontend com as seguintes variáveis:

```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_BLOCKCHAIN_URL=http://localhost:8080
REACT_APP_TITLE=EMLURB 2.0 - Monitoramento de Descarte Ilegal
```

## Executando o Frontend

Para executar o frontend em modo de desenvolvimento:

```bash
npm start
```

O frontend estará disponível em [http://localhost:3000](http://localhost:3000).

## Estrutura do Projeto

- `/src/components/` - Componentes React reutilizáveis
- `/src/App.js` - Componente principal e configuração de rotas
- `/src/theme.js` - Configuração do tema Chakra UI

## Componentes Principais

- **Map.js** - Mapa interativo utilizando React Leaflet
- **DetectionsTable.js** - Tabela de detecções com filtros
- **DetectionDetails.js** - Detalhes de uma detecção
- **BlockchainViewer.js** - Visualizador da blockchain

## Build para Produção

Para criar uma build de produção:

```bash
npm run build
```

Os arquivos gerados estarão na pasta `build`. 