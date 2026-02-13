# Base de Conhecimento

## Dados Utilizados


| Arquivo | Formato | Utilização por Sexta-Feira |
|---------|---------|---------------------|
| `historico_atendimento.sql` | SQL | Contextualizar interações anteriores (conhecer melhor o cliente) |
| `perfil_investidor.sql` | SQL | Personalizar recomendações sobre investimentos para o cliente |
| `produtos_financeiros.sql` | SQL | Sugerir produtos adequados ao perfil e como funciona |
| `transacoes.sql` | SQL | Analisar padrão de gastos do cliente (conhecer melhor o cliente)|
| `metas_investidor.sql` | SQL | Compreender os objetivos do cliente (conhecer melhor o cliente)|



---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.
Sim, primeiro que no arquivo de perfil_invertidor só havia um tipo de perfil eu criei mais seis pessoas cada um com um perfil diferente do outro, assim sendo automaticamente expandi o histórico de atendimento e as transacoes implementando dados de cada um deles após isso apliquei estes dados em em banco de dados no postgresql e para dar certo criei mais uma tabela que é a de metas aplicando as metas de cada um dos sete investidores.
> Obs.:no perfil_investidor o campo das senhas foi criptografado pelo metodo hash
---

## Estratégia de Integração

### Como os dados são carregados?

Injetar diretamente no prompt ou carregar via código como exemplo:

```python
import pandas as pd
from sqlalchemy import create_engine, text

def get_engine():       #criação de uma função para estabelecer a conexão com o banco de dados PostgreSQL usando SQLAlchemy, utilizando as credenciais armazenadas em st.secrets para segurança.
    host = "localhost"  # endereço do servidor do banco de dados 
    port = 5432         # porta padrão do PostgreSQL
    dbname = "sextafeira"       # nome do banco de dados a ser acessado
    user = "postgres"           # nome de usuário para autenticação no banco de dados
    password = st.secrets["DB_PASSWORD"]        # senha para autenticação, armazenada de forma segura em st.secrets.

    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}" # URL de conexão formatada para SQLAlchemy, especificando o driver (psycopg) e as credenciais necessárias para acessar o banco de dados PostgreSQL escritas acima.
    return create_engine(url, pool_pre_ping=True)       #retorna uma engine de conexão com a url especificada. O parâmetro pool_pre_ping=True é usado para garantir que a conexão seja verificada antes de ser reutilizada, evitando erros de conexão ociosas.
                                                        #pool_pre _ping "pinga" na url e a engine é a ponte que conecta este código ao banco de dados.

```


### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

> Os dados são consultados dinamicamente... Como ha dados de varios usuarios diferentes o usuario após se identificar é que vai ter os seus dados pegos no banco de dados pelo numero do CPF filtrando o banco e só assim pegando os dados relevantes para a IA e após isso sera enviado para a IA quando ela for responder uma pergunta e claro tem a opção de entrar sem se cadastrar a opção de visitante mas ai só sera carregado para a IA os dados de produtos financeiros
---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```
"id_produto","nome","categoria","risco","rentabilidade","aporte_minimo","indicado_para"
1,"Tesouro Selic","renda_fixa","baixo","100% da Selic","30.00","Reserva de emergência e iniciantes"
2,"CDB Liquidez Diária","renda_fixa","baixo","102% do CDI","100.00","Quem busca segurança com rendimento diário"
3,"LCI/LCA","renda_fixa","baixo","95% do CDI","1000.00","Quem pode esperar 90 dias (isento de IR)"
...
```
