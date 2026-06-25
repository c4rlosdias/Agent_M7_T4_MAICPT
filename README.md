# Agent_M7_T4_MAICPT

Material da Aula 04 do Módulo 7, Tema 4, com um agente em Python usando Agno para analisar extintores em um arquivo IFC via IfcOpenShell.

O repositório combina dois blocos:

- um backend AgentOS em Python, responsável por orquestrar o agente, a skill normativa e a leitura do IFC;
- uma interface web em Next.js, usada para conversar com o AgentOS em uma UI de chat.

## Objetivo da aula

Demonstrar um fluxo simples de agente aplicado a BIM:

- o usuário faz uma pergunta sobre extintores em um modelo IFC;
- o agente usa uma skill local com referência técnica da NBR 15808 e da NBR 12693;
- uma função em Python lê o arquivo IFC e extrai dados dos extintores;
- o agente devolve uma resposta curta e didática, adequada para demonstração em aula.

## Como a aplicação está organizada

### 1. Backend Python

O arquivo principal é `Aula_04_2_Agentes.py`.

Ele define:

- um modelo `Groq(id="openai/gpt-oss-120b")`;
- um agente `AgenteExtintoresIFC`;
- o carregamento de skills locais via `LocalSkills("./skills")`;
- um `AgentOS` para expor o agente por HTTP.

As instruções do agente deixam claro o comportamento esperado:

- usar a skill `nbr15808` como referência normativa;
- usar a tool de leitura IFC para obter os dados do modelo;
- responder de forma curta e didática.

### 2. Skill local

A skill está em `skills/nbr15808/SKILL.md`.

Ela concentra o conhecimento de domínio sobre:

- ABNT NBR 15808, para características e requisitos de extintores portáteis;
- ABNT NBR 12693, para critérios de instalação e distribuição na edificação;
- mapeamento para IFC, incluindo `IfcFireSuppressionTerminal` e propriedades customizadas.

Na prática, essa skill funciona como a base normativa que orienta a resposta do agente.

### 3. Leitura do IFC

O script `skills/nbr15808/scripts/ler_extintores_ifc.py` abre o arquivo IFC com IfcOpenShell e busca extintores de duas formas:

- primeiro por elementos do tipo `IfcFireSuppressionTerminal`;
- se não encontrar, por `IfcBuildingElementProxy` cujo nome contenha "extintor".

Para cada elemento encontrado, o script tenta ler o property set customizado `FireExtinguisher_NBR15808` e devolve um JSON com:

- `id`;
- `nome`;
- `tipo_agente`;
- `capacidade_extintora`;
- `certificado_inmetro`.

O arquivo IFC usado na aula é `extintores.ifc`.

### 4. Interface web

A pasta `agent-ui/` contém uma aplicação Next.js baseada no template `agent-ui` do ecossistema Agno.

Pelo código analisado, a UI:

- sobe em `http://localhost:3000`;
- tenta se conectar ao AgentOS em `http://localhost:7777` por padrão;
- lista agentes disponíveis pela rota `/agents`;
- envia mensagens e exibe streaming de resposta no chat.

Isso significa que a UI é opcional, mas útil para a demonstração da aula.

## Fluxo funcional da aplicação

1. O AgentOS é iniciado no backend Python.
2. A UI web se conecta ao endpoint do AgentOS.
3. O usuário envia uma solicitação como: "Analise o arquivo IFC e verifique os extintores".
4. O agente usa a skill `nbr15808` para contextualizar os critérios técnicos.
5. A leitura do IFC extrai os dados dos extintores do arquivo `extintores.ifc`.
6. O agente sintetiza a resposta em linguagem natural.

## Estrutura do repositório

```text
.
|-- Aula_04_2_Agentes.py          # ponto de entrada do AgentOS
|-- extintores.ifc                # modelo IFC usado na aula
|-- requirements.txt              # dependências Python
|-- skills/
|   `-- nbr15808/
|       |-- SKILL.md              # base normativa do agente
|       `-- scripts/
|           `-- ler_extintores_ifc.py
`-- agent-ui/                     # interface web em Next.js
```

## Requisitos

### Python

- Python 3.11+ recomendado
- ambiente virtual (`venv`)
- dependências do `requirements.txt`

### Node.js

- Node.js 18+ recomendado
- `pnpm` para a UI

### Credenciais

O backend depende de um modelo Groq. Portanto, é necessário definir a credencial correspondente no ambiente, normalmente em um arquivo `.env`.

Exemplo:

```env
GROQ_API_KEY=sua_chave_aqui
```

Se a UI precisar enviar token para o AgentOS, também é possível configurar:

```env
NEXT_PUBLIC_OS_SECURITY_KEY=seu_token_opcional
```

## Instalação

### 1. Backend Python

Crie e ative um ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Se houver erro informando ausência de componentes do AgentOS, instale também:

```powershell
python -m pip install fastapi uvicorn
```

### 2. Interface web

```powershell
Set-Location .\agent-ui
pnpm install
```

## Como executar

### Opção A. Executar apenas o backend

Na raiz do projeto:

```powershell
.\venv\Scripts\python.exe .\Aula_04_2_Agentes.py
```

O objetivo é expor o AgentOS localmente, em geral na porta `7777`.

### Opção B. Executar backend e UI

Terminal 1, na raiz do projeto:

```powershell
.\venv\Scripts\python.exe .\Aula_04_2_Agentes.py
```

Terminal 2, dentro de `agent-ui`:

```powershell
npm run dev
```

Depois abra:

```text
http://localhost:3000
```

Na barra lateral da UI, confirme que o endpoint do AgentOS está apontando para:

```text
http://localhost:7777
```

## Exemplo de uso

Exemplos de prompts para a aula:

- "Analise o arquivo `extintores.ifc` e liste os extintores encontrados."
- "Verifique se os extintores parecem compatíveis com a NBR 15808."
- "Quais propriedades dos extintores foram encontradas no IFC?"
- "Explique de forma simples se o modelo traz dados suficientes para avaliar conformidade."

## O que o agente consegue responder bem

- identificação dos extintores presentes no IFC;
- leitura de propriedades específicas do property set `FireExtinguisher_NBR15808`;
- explicações conceituais sobre tipo de agente, capacidade extintora e certificação;
- comentários didáticos sobre aderência aparente ao conteúdo da NBR 15808 e da NBR 12693.

## Limitações observadas na análise

Durante a análise do repositório, foram encontrados alguns pontos que merecem atenção:

### 1. Dependências de runtime do AgentOS

Na validação local, a execução com o Python do projeto falhou por falta de `fastapi`, embora o código importe `AgentOS`.

Isso sugere que, dependendo do ambiente, pode ser necessário instalar manualmente dependências extras do stack web do Agno.

### 2. Dependência do provedor de modelo

O backend usa `agno.models.groq.Groq`, então a aplicação depende de:

- pacote `groq` instalado;
- chave de API válida para Groq.

### 3. Referência do app no `serve`

No final do script principal, o código chama:

```python
agent_os.serve(app="Aula_04_2_Agentes_2:app", reload=True)
```

Mas o arquivo disponível no repositório se chama `Aula_04_2_Agentes.py`.

Se, após instalar todas as dependências, houver erro de importação ao subir o servidor, esse valor deve ser revisado para refletir o nome real do módulo Python.

### 4. Escopo da verificação normativa

O exemplo é didático. A leitura do IFC retorna um conjunto pequeno de propriedades e não executa, por si só, uma validação completa de conformidade normativa. A resposta do agente depende:

- da qualidade da modelagem BIM;
- da existência dos property sets esperados;
- da interpretação textual produzida pelo modelo.

## Sugestões para evolução

- adicionar validações explícitas de conformidade em Python, em vez de depender apenas da interpretação do modelo;
- expandir a leitura do IFC para capturar pavimento, localização, altura de instalação e área coberta;
- criar testes para a extração dos property sets;
- alinhar o script principal com um processo de inicialização reproduzível para a aula.

## Resumo

Este repositório demonstra um caso de uso claro de agentes aplicados a BIM:

- Agno para orquestração do agente;
- skill local para conhecimento normativo;
- IfcOpenShell para leitura do modelo IFC;
- Agent UI para interação via chat.

Como material didático, o projeto é adequado para mostrar a integração entre IA, regras de domínio e dados BIM estruturados.
