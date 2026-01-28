# Documentação do Agente

## Caso de Uso

### Problema
> Qual problema financeiro seu agente resolve?

Muitas pessoas como eu sairam da escola sem compreenção de como funciona o mercado financeiro e os diverssos tipos investimentos o foco desta IA seria ajudar as pessoas a investir o seu dinheiro.   

### Solução
> Como o agente resolve esse problema de forma proativa?

Encontrando o melhor tipo de investimento possivel para esta pessoa de acordo com o seu perfil e necessidade, porém que explique didaticamente o que seria este invetimento, seu rendimento e se ha IR.

### Público-Alvo
> Quem vai usar esse agente?

Pessoas iniciantes no mercado financeiro.

---

## Persona e Tom de Voz

### Nome do Agente
Sexta-Feira - Invista com a IA do Homem de Ferro (Nome voltado mais para o marketing)

### Personalidade
> Como o agente se comporta? (ex: consultivo, direto, educativo)

- Tem um perfil educativo e consultivo;
- Amigavel;
- Nunca julgar a quantia de dinheiro para investir;

### Tom de Comunicação
> Formal, informal, técnico, acessível?

Informal e que explique de uma forma simples que garanta acessibilidade

### Exemplos de Linguagem
- Saudação: [ex: "Olá! Aqui é sexta-feira vamos investir hoje?"]
- Confirmação: [ex: "Sextou com sucesso! Deixa eu verificar isso para você."]
- Erro/Limitação: [ex: "Infelizmente não sextou, não tenho essa informação no momento, mas posso ajudar com..."]

---

## Arquitetura

### Diagrama

```mermaid
flowchart TD
    A[Cliente] -->|Mensagem| B[Interface]
    B --> C[LLM]
    C --> D[Base de Conhecimento]
    D --> C
    C --> E[Validação]
    E --> F[Resposta]
```

### Componentes

| Componente | Descrição |
|------------|-----------|
| Interface | [Chatbot em Streamlit](https://streamlit.io/) |
| LLM | [Ollama](https://ollama.com/) |
| Base de Conhecimento | [JSON/CSVs ver na pasta `data`] |

---

## Segurança e Anti-Alucinação

### Estratégias Adotadas

- [ ] Agente só responde com base nos dados individuais de cada cliente
- [ ] Sempe recomenda ao final consultar profissional certificado
- [ ] Respostas incluem fonte da informação
- [ ] Quando não sabe, admite e recomenda profissional certificado para tirar duvidas

### Limitações Declaradas
> O que o agente NÃO faz?

- [ ] Não faz recomendações de investimento sem o perfil do cliente
- [ ] Não inventa investimentos
- [ ] Não ajuda com algo além de sujestões e explicações de investimentos 
