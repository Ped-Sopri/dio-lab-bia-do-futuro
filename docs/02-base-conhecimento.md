# Base de Conhecimento

## Dados Utilizados


| Arquivo | Formato | Utilização por Sexta-feira |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores (conhecer melhor o cliente) |
| `perfil_investidor.json` | JSON | Personalizar recomendações sobre investimentos para o cliente |
| `produtos_financeiros.json` | JSON | Sugerir produtos adequados ao perfil e como funciona |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente (conhecer melhor o cliente)|



---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.
Não
---

## Estratégia de Integração

### Como os dados são carregados?

Injetar diretamente no prompt ou carregar via código como exemplo:

```python
import pandas as pd
import json

# Carregar arquivos CSV com pandas
historico_atendimento = pd.read_csv('data/historico_atendimento.csv')
transacoes = pd.read_csv('data/transacoes.csv')

# Carregar arquivos JSON
with open("perfil_investidor.json", "r", encoding="utf-8") as f:
    perfil_investidor = json.load(f)

with open("produtos_financeiros.json", "r", encoding="utf-8") as f:
    produtos_financeiros = json.load(f)
```


### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

> Injetar os dados mokados na pasta data diretamente no prompt garantindo garantindo que o agente tenha todas os dados da forma mais silples e rapida possivel para o seu melhor desempenho, mas se as informações forem carregadas dinamicamente se ganha flexibilidade. 
---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```
Dados do Cliente:
- Nome: João Silva
- Perfil: Moderado
- Saldo disponível: R$ 5.000

Últimas transações:
- 01/11: Supermercado - R$ 450
- 03/11: Streaming - R$ 55
...
```
