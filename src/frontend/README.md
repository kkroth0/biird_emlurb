# 🦅 BiiRD - Instalação do Frontend

## Sobre o Módulo

O frontend do BiiRD é uma interface web interativa construída com React, Chakra UI e React Leaflet para visualização e gestão das detecções de descarte ilegal.

## Pré-requisitos

- Node.js 14+
- NPM ou Yarn

## Instalação

### 1. Instalação das Dependências

```bash
# Navegar para o diretório do frontend
cd src/frontend

# Instalar as dependências
npm install
# OU
yarn install
```

### 2. Configuração das Variáveis de Ambiente

Crie um arquivo `.env.local` na raiz do diretório do frontend com as seguintes variáveis:

```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_BLOCKCHAIN_URL=http://localhost:8080
REACT_APP_TITLE=EMLURB 2.0 - Monitoramento de Descarte Ilegal
```

## Execução

Para iniciar o servidor de desenvolvimento:

```bash
# A partir do diretório do frontend
npm start
# OU
yarn start
```

O frontend estará acessível em [http://localhost:3000](http://localhost:3000).

## Estrutura de Arquivos

```
src/frontend/
│
├── public/              # Arquivos estáticos
├── src/
│   ├── components/      # Componentes React reutilizáveis
│   │   ├── Map.js       # Mapa interativo com React Leaflet
│   │   ├── DetectionsTable.js  # Tabela de detecções
│   │   ├── DetectionDetails.js # Detalhes de uma detecção
│   │   └── BlockchainViewer.js # Visualizador da blockchain
│   ├── contexts/        # Contextos React para gerenciamento de estado
│   ├── services/        # Serviços para comunicação com APIs
│   ├── utils/           # Funções utilitárias
│   ├── App.js           # Componente principal e configuração de rotas
│   ├── index.js         # Ponto de entrada da aplicação
│   └── theme.js         # Configuração do tema Chakra UI
└── package.json         # Dependências e scripts
```

## Principais Funcionalidades

### Mapa Interativo
- Visualização geográfica das câmeras e detecções
- Marcadores diferenciados por status
- Popups com informações resumidas

### Tabela de Detecções
- Listagem de todas as detecções com paginação
- Filtros por data, status e localização
- Ações rápidas para atualização de status

### Detalhes da Detecção
- Visualização detalhada de cada caso
- Histórico de atualizações
- Imagens capturadas
- Opções para atualizar status e adicionar observações

### Visualização da Blockchain
- Explorador de blocos para auditoria
- Verificação de integridade da cadeia
- Detalhes de transações

## Build para Produção

Para criar uma build otimizada para produção:

```bash
# A partir do diretório do frontend
npm run build
# OU
yarn build
```

Os arquivos gerados estarão na pasta `build`.

## Integração com o Backend

O frontend se comunica com o backend através de chamadas API REST. Certifique-se de que:

1. O backend está em execução na URL configurada em `REACT_APP_API_URL`
2. A blockchain está acessível na URL configurada em `REACT_APP_BLOCKCHAIN_URL`

## Customização

### Tema e Aparência
O tema da aplicação pode ser personalizado no arquivo `src/theme.js` usando as convenções do Chakra UI.

### Logotipos e Marcas
Substitua os arquivos de logo e favicon no diretório `public/` para personalizar a identidade visual.
