# 🤖 Desafio de Projeto: A BIA do Futuro com IA Generativa

## Contexto

A **BIA** (Bradesco Inteligência Artificial) já é uma assistente virtual consolidada, auxiliando milhões de clientes em consultas e operações do dia a dia. Agora, queremos pensar no próximo passo: como a IA Generativa pode transformar a BIA em uma **agente financeira ainda mais inteligente, proativa e personalizada**? Neste desafio, você vai idealizar e prototipar uma evolução da BIA que:

- **Antecipa necessidades** ao invés de apenas responder perguntas
- **Personaliza** sugestões com base no contexto de cada cliente
- **Coparticipa** ativamente da vida financeira do usuário
- **Conecta-se** a múltiplos canais de forma fluida
- **Garante segurança** e confiabilidade em cada interação

---

## O Que Você Deve Entregar

### 1. Caso de Uso Prioritário

Escolha **um cenário específico** onde sua BIA do Futuro agregaria valor. Exemplos:

- Consultoria financeira proativa
- Planejamento de metas e orçamento pessoal
- Recomendação personalizada de produtos/investimentos
- Educação financeira adaptativa
- Prevenção e alertas de fraudes

**Entregáveis:**
- Descrição clara do problema que você quer resolver
- Justificativa: por que esse caso é relevante para o cliente e para o banco?

📄 **Template:** [`docs/caso-de-uso.md`](./docs/caso-de-uso.md)

---

### 2. Features da Solução

Liste as **funcionalidades principais** que compõem sua ideia. Pense em:

- Qual a capacidade central da sua BIA? (ex: motor de recomendação, análise preditiva)
- Quais integrações seriam necessárias? (canais, APIs, sistemas)
- Como garantir segurança e compliance nas respostas?

**Entregáveis:**
- Lista objetiva das features com breve descrição de cada uma

📄 **Template:** [`docs/features.md`](./docs/features.md)

---

### 3. Desenho da Solução

Crie uma **visão arquitetural** que responda:

- **Fluxo de dados:** como a informação transita do usuário até a resposta da BIA?
- **Papel da IA Generativa:** em que momento ela atua e como?
- **Segurança:** como evitar alucinações e garantir respostas confiáveis?
- **Omnichannel:** como a solução se adapta a diferentes canais (app, WhatsApp, voz)?

**Entregáveis:**
- Diagrama ou fluxograma da arquitetura
- Breve explicação das camadas e componentes

📄 **Template:** [`docs/arquitetura.md`](./docs/arquitetura.md)

---

### 4. Prototipagem

Aqui é a parte prática! Você pode escolher o nível de profundidade conforme sua experiência:

#### 4.1 Prompt Engineering
Documente os prompts que fariam sua BIA funcionar:
- System prompt (instruções de comportamento para a IA)
- Exemplos de interações (mensagem do usuário + resposta esperada)
- Testes de edge cases (situações limite)

📄 **Template:** [`prompts/prompts-exemplo.md`](./prompts/prompts-exemplo.md)

#### 4.2 Código MVP (Opcional)
Se quiser ir além, crie um protótipo funcional:
- Um chatbot simples que demonstre a interação
- Integração básica com APIs de LLMs
- Use a linguagem e ferramentas que preferir

📁 **Pasta:** [`src/`](./src/) (coloque aqui seus arquivos de código)

#### 4.3 Interface Visual (Opcional)
Crie mockups ou protótipos navegáveis da experiência do usuário.

📁 **Pasta:** [`assets/`](./assets/) (coloque aqui imagens, prints e protótipos)

---

### 5. Validação

Descreva como você testaria sua solução antes de colocá-la em produção:

**Cenários de Teste:**
- Quais situações seriam simuladas?
- Como garantir que a IA responde corretamente em casos críticos?
- Como testar escalabilidade?

**Métricas de Sucesso:**
- Precisão e relevância das respostas
- Tempo de resposta
- Satisfação do usuário
- Taxa de resolução sem escalonamento humano

**Entregáveis:**
- Descrição dos cenários de teste
- Lista de métricas que você acompanharia

📄 **Template:** [`docs/validacao.md`](./docs/validacao.md)

---

## Ferramentas Sugeridas

Todas as ferramentas abaixo possuem versões (ou camadas) gratuitas:

| Categoria | Ferramentas |
|-----------|-------------|
| **LLMs para testes** | [ChatGPT](https://chat.openai.com/), [Copilot](https://copilot.microsoft.com/), [Gemini](https://gemini.google.com/), [Claude](https://claude.ai/), [Ollama](https://ollama.ai/) (modelos open-source locais) |
| **Diagramas** | [Mermaid](https://mermaid.js.org/) (renderiza no GitHub), [Draw.io](https://app.diagrams.net/), [Excalidraw](https://excalidraw.com/) |
| **Prototipagem visual** | [Figma](https://www.figma.com/), [Canva](https://www.canva.com/), [v0.dev](https://v0.dev/) |
| **Desenvolvimento rápido** | [Streamlit](https://streamlit.io/), [Google Colab](https://colab.research.google.com/) |
| **Orquestração de LLMs** | [LangChain](https://www.langchain.com/), [LangFlow](https://www.langflow.org/), [N8N](https://n8n.io/), [CrewAI](https://www.crewai.com/) |
| **Organização** | [Notion](https://www.notion.so/), [Trello](https://trello.com/) |

---

## Estrutura do Repositório

```
📁 dio-lab-bia-do-futuro/
├── 📄 README.md
├── 📁 docs/
│   ├── caso-de-uso.md
│   ├── features.md
│   ├── arquitetura.md
│   └── validacao.md
├── 📁 prompts/
│   └── prompts-exemplo.md
├── 📁 src/
│   └── (código do MVP, se houver)
└── 📁 assets/
    └── (imagens, diagramas, protótipos)
```

---

## Dicas Finais

1. **Menos é mais:** foque em resolver bem um problema específico
2. **Documente seu raciocínio:** explique o porquê das suas escolhas
3. **Pense no usuário:** a melhor tecnologia é invisível para quem usa
4. **Segurança não é opcional:** em finanças, confiança é tudo
5. **Use IA para criar:** as próprias LLMs podem ajudar a gerar diagramas, código e documentação
