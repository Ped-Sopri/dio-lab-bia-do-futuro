# ============================================================
# CHATBOT "SEXTA-FEIRA" (Streamlit + Ollama + Áudio + PostgreSQL)
# ============================================================
# ESTE ARQUIVO É UM APP STREAMLIT. Para conclusão, do curso da DIO+Bradesco.
# Principal objetivo para mim neste projeto é tentar criar algo que juntasse todas as técnologias que aprendi no curso.
# Que seria a integraçao de um banco de dados IA e programação. 
# Observações: 
# TTL demonstrativo para fins educacionais. Em produção, o valor deve variar conforme a natureza dos dados: - dados estáticos → TTL alto - dados dinâmicos → TTL baixo
# Implementei audio conforme desenvolvido durante aula em curso, mas sabemos que ja existe tipos mais realistas como ja sitado no curso.
# Foi escolhido o modelo gpt-oss:120b-cloud do Ollama por ser gratuito, estar na nuvem e ter um número de parâmetros muito alto, o que pode proporcionar respostas mais ricas e detalhadas para as interações do chatbot, especialmente considerando a complexidade do tema de investimentos financeiros.
# Foi escolhido o PostgreSQL para o banco de dados por ser um sistema de gerenciamento de banco de dados relacional robusto, amplamente utilizado e ser gratuito.
# Fui adepto ao Streamlit por sua facilidade para criação de interface.
# Criptografia de senhas com hash e SALT para segurança dos dados dos usuários não era o foco do projeto, mas quis implementar para demonstrar o conceito de segurança de senhas e boas práticas no armazenamento de informações sensíveis. 
# ============================================================
#=========================BIBLIOTECAS=========================
import hashlib          #importa a biblioteca hashlib para funções de hash (segurança de senhas,criptografia)
import streamlit as st  #importa a biblioteca Streamlit para criar a interface
import pandas as pd     #importa a biblioteca Pandas para manipulação de dados(Tabelas, DataFrames)
import requests         #importa a biblioteca Requests para fazer requisições HTTP (comunicação com Ollama)
import speech_recognition as sr    #importa a biblioteca SpeechRecognition para transcrição de áudio (TTS)
import tempfile             #importa a biblioteca tempfile para criar arquivos temporários (armazenar áudio recebido do usuario)
from gtts import gTTS       #importa a biblioteca gTTS (Google Text-to-Speech) para converter texto em áudio (respostas faladas da sexta-feira)
import io          #importa a biblioteca io para manipulação de fluxos de dados em memória (gerar áudio em bytes para o Streamlit)
import os           #importa a biblioteca os para operações do sistema (ex: remover arquivos temporários de áudio)
import re           #importa a biblioteca re para expressões regulares (validação e formatação de CPF, limpeza de texto para TTS)
from sqlalchemy import create_engine, text        #importa funções do SQLAlchemy para conexão e execução de consultas no banco PostgreSQL (armazenamento de dados dos usuários, produtos, histórico)
#===============================================================
#comando em streamlit para configurar titulo(Chatbot-Investimentos) da pagina icone (🤖) e como layout vai ser wide que é para ocupar toda a largura da tela.
st.set_page_config(page_title="Chatbot-Investimentos", page_icon="🤖", layout="wide") 
#===============================================================
#=========================CONEXÃO COM POSTGRES=========================
@st.cache_resource(show_spinner=False) # uma das dificuldades ao utilizar os bancos de dados foi melhorar a velocidade e evitar conexões repetidas, com esse comando do Streamlit a função get_engine só é executada uma vez e o resultado é armazenado em cache, ou seja, a conexão com o banco é criada apenas na primeira vez que a função é chamada e reutilizada nas chamadas seguintes, melhorando a performance do app.
def get_engine():       #criação de uma função para estabelecer a conexão com o banco de dados PostgreSQL usando SQLAlchemy, utilizando as credenciais armazenadas em st.secrets para segurança.
    host = "localhost"  # endereço do servidor do banco de dados 
    port = 5432         # porta padrão do PostgreSQL
    dbname = "sextafeira"       # nome do banco de dados a ser acessado
    user = "postgres"           # nome de usuário para autenticação no banco de dados
    password = st.secrets["DB_PASSWORD"]        # senha para autenticação, armazenada de forma segura em st.secrets.

    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}" # URL de conexão formatada para SQLAlchemy, especificando o driver (psycopg) e as credenciais necessárias para acessar o banco de dados PostgreSQL escritas acima.
    return create_engine(url, pool_pre_ping=True)       #retorna uma engine de conexão com a url especificada. O parâmetro pool_pre_ping=True é usado para garantir que a conexão seja verificada antes de ser reutilizada, evitando erros de conexão ociosas.
                                                        #pool_pre _ping "pinga" na url e a engine é a ponte que conecta este código ao banco de dados.
#=============================================================
#=========================CONFIG. SENHA=========================
def cpf_para_digitos(cpf_formatado: str) -> str:  #criação de uma função para converter um CPF formatado (com pontos e traço) em apenas dígitos, utilizando expressões regulares para remover qualquer caractere que não seja número, garantindo que o CPF seja processado corretamente para consultas no banco de dados.
    return re.sub(r"\D", "", cpf_formatado or "")

def cpf_formatado_ok(cpf: str) -> bool:         #criação de uma função para validar se um CPF está no formato correto (000.000.000-00) usando expressões regulares, garantindo que os usuários insiram o CPF de forma adequada antes de tentar fazer login ou acessar seus dados.
    return bool(re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf or ""))

SALT = st.secrets["SALT_VAL"]  # variavel utilizada para "misturar" com a senha real do usuario criando o valor secreto para o hash

def hash_senha(senha: str) -> str:    #função para criar um hash seguro da senha do usuário, combinando a senha com um valor de SALT, converte para bytes com UTF-8 e utilizando o algoritmo SHA-256 para gerar um hash hexadecimal, protegendo as informações dos usuários.
    return hashlib.sha256((senha + SALT).encode("utf-8")).hexdigest()  #poderia ter utilizado outros como brcrypt ou argon2 que são mais robustos para senhas, mas para este projeto e com o uso do SALT, o SHA-256 é suficiente para demonstrar o conceito de hashing de senhas.

def buscar_senha_hash_banco(cpf_digits: str) -> str | None: #função para buscar o hash da senha do usuário no banco de dados, utilizando a conexão estabelecida pela função get_engine, executando uma consulta SQL que seleciona o campo senha_hash da tabela perfil_investidor onde o CPF (apenas dígitos) corresponde ao CPF fornecido, e retornando o hash encontrado ou None se o CPF não for encontrado ou se o campo senha_hash for nulo.
    engine = get_engine()       #obtém a engine de conexão com o banco de dados usando a função get_engine definida anteriormente.

    with engine.connect() as conn:  # com a conexão SQL estabelecida ececuta um comando sql para encontrar o cpf do usuário e retornar o hash da senha correspondente, utilizando uma expressão regular para garantir que o CPF seja comparado apenas pelos dígitos.
        result = conn.execute(
            text("""
                SELECT senha_hash
                FROM perfil_investidor
                WHERE regexp_replace(cpf::text, '[^0-9]', '', 'g') = :cpf
                LIMIT 1
            """),
            {"cpf": cpf_digits}
        )

        row = result.fetchone()         #fetchone() é usado para obter a primeira linha do resultado da consulta, que deve conter o hash da senha se o CPF for encontrado. 

    if not row or row[0] is None: # se não houver resultado ou se o campo senha_hash for nulo, a função retorna None, indicando que o CPF não foi encontrado.
        return None

    return str(row[0])  # se o hash da senha for encontrado, ele é convertido para string e retornado para ser comparado com o hash da senha fornecida pelo usuário durante o login.

# ====================================================================
# =====================PAGINA DE ACESSO=========================
st.session_state.setdefault("logado", False)   #inicializa a variável de estado "logado" como False, indicando que o usuário não está logado por padrão. O setdefault é usado para garantir que essa variável exista no session_state, evitando erros caso seja acessada antes de ser definida.
st.session_state.setdefault("visitante", False)  #inicializa a variável de estado "visitante" como False, indicando que o usuário não escolheu continuar como visitante por padrão. Assim como "logado", o setdefault garante que essa variável exista no session_state para evitar erros.
st.session_state.setdefault("cpf_formatado", "") #inicializa a variável de estado "cpf_formatado" como uma string vazia, que será usada para armazenar o CPF formatado do usuário quando ele fizer login. O setdefault garante que essa variável exista no session_state, permitindo que seja atualizada posteriormente com o CPF do usuário logado.
if not st.session_state.logado and not st.session_state.visitante:  #condição para que caso não esteja logado permaneça nesta pagina de acesso, onde o usuário pode escolher entre fazer login ou continuar como visitante. Se nenhuma das condições for verdadeira (ou seja, o usuário não está logado e não escolheu ser visitante), o código dentro deste bloco será executado, exibindo a interface de login e opções para o usuário.
    st.title("🔐 Acesso ao Sistema")        #titulo da pagina
    st.warning("Faça login ou continue como visitante.")        #aviso para usuário.
    st.warning("Usuários não identificados terão acesso limitado a recomendações genéricas.") #aviso para usuário.

    cpf = st.text_input("CPF", placeholder="000.000.000-00") #campo para usuário digitar cpf, com placeholder para indicar o formato esperado.
    senha = st.text_input("Senha", type="password") #campo para usuário digitar senha, com type="password" para ocultar os caracteres digitados.

    col1, col2 = st.columns(2)  #divisão da interface abaixo co campo senha em duas colunas.

    # BOTÃO LOGIN
    with col1:   #na coluna 1
        if st.button("Entrar"):  # criação do botão entrar e condição para processar o login quando o botão for clicado.
            if not cpf_formatado_ok(cpf):       #condição para que cpf esteja no formato certo se não estiver  aparece a mensagem de st.error.
                st.error("Digite o CPF no formato 000.000.000-00.")
                st.stop()             #st.stop() é usado para interromper a execução do código após exibir a mensagem de erro, garantindo que o restante do código de login não seja executado se o CPF estiver no formato incorreto.

            cpf_digits = cpf_para_digitos(cpf)  # variável cpf_digits recebe o resultado da função cpf_para_digitos, que converte o CPF formatado em apenas dígitos, removendo pontos e traços.
            if len(cpf_digits) != 11:      #condição para verificar se o CPF convertido tem exatamente 11 dígitos, que é o formato correto para CPFs no Brasil. Se não tiver 11 dígitos, exibe uma mensagem de erro indicando que o CPF é inválido e interrompe a execução do código de login.
                st.error("CPF inválido.")  #exibe mensagem de erro para CPF inválido
                st.stop()     #interrompe a execução do código para evitar que o login continue com um CPF inválido.

            senha_hash_db = buscar_senha_hash_banco(cpf_digits)   #a variavel senha_hash_db recebe o resultado da função buscar_senha_hash_banco, que consulta o banco de dados para obter o hash da senha correspondente ao CPF fornecido. Se o CPF não for encontrado ou se o campo senha_hash for nulo, a função retornará None.

            if senha_hash_db is None:  # condição para caso senha for none, exibe a mensagem de erro, e interrompe a execução do código de login.
                st.error("CPF não encontrado ou usuário sem senha cadastrada.")
                st.stop()

            if hash_senha(senha) != senha_hash_db:   #condição para caso senha for diferente, exibe a mensagem de erro, e interrompe a execução do código de login.
                st.error("Senha incorreta.")
                st.stop()

            st.session_state.logado = True  #se o login for bem-sucedido, a variável muda para True, fazendo com que usuário mude de interface.
            st.session_state.cpf_formatado = cpf  #armazena o CPF formatado no session_state para uso posterior, como carregar os dados do usuário e personalizar as recomendações de investimento.
            st.rerun()  #recarrega a página para refletir o estado de login atualizado, permitindo que o usuário acesse a interface principal do chatbot após um login bem-sucedido.

    with col2:  #na coluna 2
        if st.button("Continuar sem identificação"): #condição e criação do botão como visitante, caso o usuário clique neste botão, a variável de estado "visitante" é definida como True, indicando que o usuário escolheu continuar sem se identificar. Em seguida, a página é recarregada para refletir essa escolha e permitir que o usuário acesse a interface do chatbot com acesso limitado a recomendações genéricas.
            st.session_state.visitante = True  #variável muda para True, fazendo com que usuário mude de interface.
            st.rerun()  #recarrega a página para refletir o estado de login atualizado, permitindo que o usuário acesse a interface principal do chatbot após um login bem-sucedido.
    st.stop()  # interrompe a execução do código para garantir que o restante do app não seja carregado enquanto o usuário estiver na página de acesso, evitando que ele veja ou interaja com a interface principal do chatbot antes de fazer login ou escolher continuar como visitante.
#=============================================================
#=========================CONFIG. Ollama====================
Ollama_BASE = "http://localhost:11434"   #variavel é a URL base para acessar a API do OLLAMA.
OLLAMA_CHAT_URL = f"{Ollama_BASE}/api/chat"  #variavel especifica o endpoint para enviar mensagens de chat e receber respostas do modelo, utilizado na função ollama_chat para comunicação com o modelo de linguagem.
OLLAMA_GEN_URL = f"{Ollama_BASE}/api/generate"  #variavel especifica o endpoint para enviar prompts de geração de texto e receber respostas do modelo, que poderia ser utilizado para tarefas de geração de texto mais simples ou específicas.

DEFAULT_MODEL = "gpt-oss:120b-cloud"  #variavel define o modelo padrão a ser utilizado nas chamadas para o Ollama, que é um modelo de linguagem grande (120 bilhões de parâmetros) otimizado para execução em nuvem, oferecendo respostas mais rápidas e eficientes para as interações do chatbot.
# foi preferivel utilizar isto pois agrega o melhor dos dois mundos é gratuito e esta na nuvem sem problema de lentidão e alem disso com 120B parâmetros = absurdamente pesado.
REQUEST_TIMEOUT = 180 # Tempo máximo (segundos) esperando resposta do Ollama.

def ler_df(sql_query: str, params=None) -> pd.DataFrame: #função para ler dados do banco de dados e retornar um DataFrame do Pandas.
    engine = get_engine()       #obtém a engine de conexão com o banco de dados usando a função get_engine definida anteriormente.
    return pd.read_sql_query(sql_query, engine, params=params)      #executa a consulta SQL fornecida na variável sql_query usando a conexão estabelecida pela engine, e retorna os resultados como um DataFrame do Pandas. O parâmetro params é opcional e pode ser usado para passar parâmetros para consultas parametrizadas, ajudando a evitar injeção de SQL e melhorar a segurança das consultas.
#definindo o que a IA é e suas regras de funcionalidade.
SYSTEM_PROMPT_DEFAULT = """Você é Sexta-Feira, uma inteligência artificial especializada em recomendar investimentos aos clientes de acordo com suas necessidades.

REGRAS:
1. Sempre baseie suas respostas nos dados fornecidos.
2. Nunca invente informações.
3. Respostas sempre concisas, objetivas, educadas e didaticas.
4. Se você não souber algo, admita e ofereça ao usuario se consultar com profissional certificado.
5. Se o cliente disser que quer ou está pensando em investir e não especificou sempre ofereça produtos de acordo com o seu perfil de investimento porém se for um usuario sem identificação pergunte, caso o usuario não tenha especificado:
- Qual o nível de risco que você está disposto a assumir nesta transação?
- Qual o valor que você está disposto a investir?
6. Apresente as opções de investimento especificando: nome, categoria, investimento mínimo, risco e retorno.
7. Sempre informe se o investimento exigirá o pagamento de imposto de renda ou não.
8. Jamais responda qualquer pergunta além do tema de investimentos financeiros e lembre ao usuário que seu papel não é esse.
9. Se o usuario fizer uma pergunta se a ação, moeda ou qualquer um ira aumentar ou diminuir o valor ou a cotação diga que o melhor a se fazer é consultar um profissional certificado, pois o mercado financeiro é muito volátil e não se pode confiar totalmente em previsões.
10. Se o cliente fizer perguntas sobre o mercado financeiro, investimentos ou produtos de investimento, responda com base nos dados fornecidos e informe que o mercado é volátil e que é importante consultar um profissional certificado para decisões de investimento.
11. Nunca divulgue informações pessoais do cliente.
12. Sempre que possível, eduque o cliente sobre conceitos financeiros relacionados à pergunta ou recomendação.
13. Exemplo de fala de confirmação:"Sextou com sucesso!...(restante do texto).Exemplo de fala de erro ou limitação:Infelizmente não Sextou...(restante do texto).
"""
st.session_state.setdefault("mensagens", [{"role": "assistant", "content": "Sextou! Como posso ajudar?"}]) # mensagens do chat são armazenadas no session_state do Streamlit, permitindo que o histórico de mensagens seja mantido durante a interação do usuário com o chatbot. A mensagem inicial é definida como "Sextou! Como posso ajudar?", indicando que o chatbot está pronto para receber perguntas e fornecer recomendações de investimento.
#=============================================================
#=========================MEMORIA DA IA=========================
st.session_state.setdefault("summary", "")  # resumo acumulado do chat
def obter_historico_curto(max_msgs=8):        #função para obter o histórico de mensagens curto para enviar ao Ollama.
    historico = st.session_state.get("mensagens", []) #declara a variavel historico que recebe as mensagens do session_state, ou uma lista vazia caso não haja mensagens. O session_state é onde o Streamlit armazena o estado da aplicação, e "mensagens" é a chave onde o histórico de mensagens do chat é mantido.
    return historico[-max_msgs:]                #retorna apenas as últimas max_msgs mensagens do histórico, o que pode melhorar a qualidade das respostas geradas pelo modelo.

def mensagem_para_texto(mensagens: list[dict]) -> str: #função para converter uma lista de mensagens (dicionários com "role" e "content") em um texto formatado, onde cada mensagem é representada por seu papel (USER ou ASSISTANT) seguido do conteúdo da mensagem, separados por quebras de linha. Isso é útil para criar um bloco de texto que pode ser enviado ao modelo de linguagem para resumir ou analisar o histórico da conversa.
    linhas = []     #lista para armazenar as linhas formatadas do histórico de mensagens.
    for m in mensagens:    #itera sobre cada m = mensagem na lista de mensagens, onde cada mensagem é um dicionário que deve conter as chaves "role" e "content".
        role = m.get("role", "")        #obtém o valor da chave "role" da mensagem, que indica se a mensagem foi enviada pelo usuário ("user") ou pela IA. Se a chave "role" não estiver presente, retorna uma string vazia por padrão.
        content = (m.get("content") or "").strip()  #obtem o valor da mensagem em si. se a chave "content" não estiver presente ou for None, retorna uma string vazia. O método strip() é usado para remover espaços em branco no início e no final do conteúdo da mensagem, garantindo que o texto seja limpo antes de ser adicionado à lista de linhas.
        if role in ("user", "assistant") and content:   #verifica se o papel da mensagem é "user" ou "assistant"(IA) e se o conteúdo não está vazio. Isso garante que apenas mensagens relevantes sejam incluídas no histórico formatado.
            linhas.append(f"{role.upper()}: {content}")  #adiciona uma linha formatada a lista de linhas, onde o papel da mensagem é convertido para letra maiúscula.
    return "\n".join(linhas) #retorna o histórico de mensagens formatado como um único bloco de texto, onde cada mensagem é separada por uma quebra de linha. Isso facilita o envio do histórico para o modelo de linguagem para análise ou resumo.

def ollama_resumir(modelo: str, resumo_atual: str, bloco: str) -> str:  #função para resumir o histórico de mensagens usando o modelo do Ollama, onde resumo_atual é o resumo acumulado até agora e bloco é o novo texto formatado do histórico de mensagens que se deseja incorporar ao resumo. A função constrói um prompt para o modelo de linguagem, solicitando que ele atualize o resumo com base nas novas mensagens, mantendo as preferências do usuário, decisões e recomendações anteriores, e garantindo que o resultado seja conciso e em português.
    prompt_resumo = f"""
        Você é um sistema que resume conversas.
        RESUMO ATUAL (se existir):
        {resumo_atual}
        NOVAS MENSAGENS PARA INCORPORAR AO RESUMO:
        {bloco}
        Tarefa:
        - Atualize o resumo incorporando as novas mensagens.
        - Mantenha em português.
        - Seja curto (máximo ~12 linhas).
        - Preserve preferências do usuário (risco, valor, objetivos), decisões já tomadas e recomendações feitas.
        - NÃO inclua dados sensíveis.
        - NÃO invente nada.
        - Produza apenas o RESUMO atualizado.
        """.strip() #prompt para o modelo de linguagem, explicando como resumir e o . strip() é usado para remover espaços em branco no início e no final do prompt, garantindo que o texto seja limpo antes de ser enviado ao modelo.
    payload = {  #este payload é o corpo da requisição que será enviada para o endpoint de chat do Ollama, contendo o modelo a ser utilizado, as mensagens (neste caso, apenas o prompt de resumo).
        "model": modelo,
        "messages": [{"role": "system", "content": prompt_resumo}],
        "options": { #opções explicada mais abaixo na função ollama_chat.
            "temperature": 0.1,
            "top_p": 0.7,
            "num_predict": 250,
            "repeat_penalty": 1.1,
        },
        "stream": False,
        }
    r = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=REQUEST_TIMEOUT) #declara a variavel r de requisição que recebe a resposta da requisição POST feita para o endpoint de chat do Ollama, onde o payload é enviado como JSON e o tempo máximo de espera pela resposta é definido por REQUEST_TIMEOUT. Esta requisição é responsável por enviar o prompt de resumo para o modelo de linguagem e obter a resposta que contém o resumo atualizado. 
    if r.status_code != 200:  #condição caso r tenha um status code diferente de 200, o que indica que houve um erro na requisição (como modelo não encontrado, problemas de conexão, etc). Se isso acontecer, a função levanta uma exceção RuntimeError com uma mensagem que inclui o status code e o texto da resposta, ajudando a identificar o motivo do erro.
        raise RuntimeError(f"Ollama resumo HTTP {r.status_code}: {r.text}") #levanta uma excessão de run time error com uma mensagem que inclui o status code e o texto da resposta, ajudando a identificar o motivo do erro caso a requisição para o Ollama não seja bem-sucedida.
    return r.json()["message"]["content"].strip() #se der certo retorna o conteudo da mensagem da resposta do modelo que tem o resumo atual.

def talvez_resumir_chat(modelo: str, limite_total: int = 19, manter_ultimas: int = 8): #função para verificar se o número total de mensagens no histórico do chat ultrapassa um limite definido (limite_total). Se ultrapassar, a função pega as mensagens mais antigas (tudo menos as últimas manter_ultimas) e as converte em um bloco de texto formatado usando a função mensagem_para_texto. Em seguida, esse bloco é enviado para a função ollama_resumir, que atualiza o resumo acumulado com base nas novas mensagens. Por fim, a função mantém apenas as últimas manter_ultimas mensagens no histórico do chat, garantindo que o histórico seja gerenciado de forma eficiente e que o modelo de linguagem tenha um contexto relevante para gerar respostas.
    msgs = st.session_state.get("mensagens", []) #declara a variavel msgs que recebe as mensagens do session_state, ou uma lista vazia caso não haja mensagens. O session_state é onde o Streamlit armazena o estado da aplicação, e "mensagens" é a chave onde o histórico de mensagens do chat é mantido.
    # só resumimos se passou do limite
    if len(msgs) <= limite_total:  #condição para verificar se o número total de mensagens no histórico do chat é menor ou igual ao limite_total definido. Se for, a função retorna imediatamente, sem fazer nada, pois não é necessário resumir o histórico. Isso ajuda a evitar chamadas desnecessárias ao modelo de linguagem para resumir quando o número de mensagens ainda está dentro do limite aceitável.
        return  #se o número de mensagens for menor ou igual aolimite, a função sai.
    antigas = msgs[:-manter_ultimas]  #declara a variavel antigas que recebe as mensagens mais antigas do histórico, ou seja, todas as mensagens exceto as últimas manter_ultimas. Essas mensagens são as que serão resumidas para atualizar o resumo acumulado, enquanto as últimas manter_ultimas mensagens serão mantidas no histórico para fornecer contexto recente ao modelo de linguagem.
    bloco = mensagem_para_texto(antigas).strip() #declara a variavel bloco que recebe o resultado da função mensagem_para_texto aplicada às mensagens antigas, convertendo-as em um texto formatado. O método strip() é usado para remover espaços em branco no início e no final do bloco de texto, garantindo que o texto seja limpo antes de ser enviado para a função de resumo.
    if not bloco:  #se não houver bloco de texto
        st.session_state["mensagens"] = msgs[-manter_ultimas:]  #mantem apenas as ultimas mensagens do histórico.
        return #retorna para evitar a função de resumo caso o bloco esteja vazio.
    resumo_atual = st.session_state.get("summary", "")  # declara a variavel resumo_atual que recebe o resumo acumulado atual do session_state, ou uma string vazia caso não haja resumo. O resumo acumulado é o resultado das chamadas anteriores à função de resumo, e é atualizado a cada vez que o histórico de mensagens ultrapassa o limite definido, permitindo que o modelo de linguagem mantenha um contexto relevante da conversa ao longo do tempo.
    try:
        novo_resumo = ollama_resumir(modelo, resumo_atual, bloco) #tenta chamar a função ollama resumir para obter o resumo atualizado. 
    except Exception: #se ocorrer qualquer exceção durante a chamada para o modelo de resumo, a função captura a exceção e simplesmente retorna, mantendo o resumo antigo e evitando que o histórico de mensagens seja perdido. Isso garante que, mesmo em caso de falhas na comunicação com o modelo de linguagem, o chatbot continue funcionando sem perder o contexto acumulado.
        return # se falhou, mantém o resumo antigo (não perde o que já tinha)
    st.session_state["summary"] = novo_resumo   # atualiza o resumo acumulado no session_state com o novo resumo obtido do modelo, garantindo que o chatbot tenha um contexto atualizado da conversa para gerar respostas mais relevantes e informadas. O resumo acumulado é uma forma de manter um histórico condensado da conversa, permitindo que o modelo de linguagem tenha acesso a informações importantes mesmo quando o número total de mensagens ultrapassa o limite definido.
    st.session_state["mensagens"] = msgs[-manter_ultimas:] # mantém apenas as últimas manter_ultimas mensagens no histórico do chat, garantindo que o histórico seja gerenciado de forma eficiente e que o modelo de linguagem tenha um contexto relevante para gerar respostas, enquanto o resumo acumulado mantém as informações importantes das mensagens mais antigas.
#=============================================================
#=========================CHAT=========================
def normalizar_mensagens(): #função para normalizar o formato das mensagens no session_state, garantindo que todas as mensagens estejam em um formato consistente (dicionários com "role" e "content").
    nova = []  #declara a variavel nova como lista vazia, que serra usada para armazenar as mensagens normalizadas.
    for item in st.session_state["mensagens"]: #para cada item na lista de mensagens do session_state, a função verifica o formato de cada mensagem e a normaliza para garantir que todas as mensagens estejam em um formato consistente, facilitando o processamento e a geração de respostas pelo modelo de linguagem.
        if isinstance(item, dict) and "role" in item and "content" in item: #se existir um item de dicionario e tiver as chaves "role" e "content".
            if item["role"] in ("user", "assistant", "system"): #se role for user, assistant ou system.
                nova.append(item) #a mensagem já está no formato correto, então é adicionada diretamente à nova lista (nova[]) de mensagens(item).
        elif isinstance(item, dict) and "text" in item: # se o item é dicionario com a chave text.
            txt = (item.get("text") or "").strip() #a variavel txt recebe o valor "text" ou vazio e remove os espaços com strip.
            if txt: # se txt não estiver vazio após o strip.
                nova.append({"role": "user", "content": txt}) # mensagem é adicionada a lista.
        elif isinstance(item, str): # se item for string
            txt = item.strip() # a variavel txt recebe o valor do item e remove os espaços com strip.
            if txt: # se txt não estiver vazio após o strip.
                nova.append({"role": "user", "content": txt}) #é adicionado a lista.
    if not nova: # se a lista estiver vazia.
        nova = [{"role": "assistant", "content": "Sextou! Como posso ajudar?"}] #sera adicionado a mensagem inicial
    st.session_state["mensagens"] = nova #atualiza o session_state com a nova lista de mensagens normalizadas, garantindo que o histórico de mensagens do chat esteja em um formato consistente para processamento e geração de respostas pelo modelo de linguagem.

def ollama_chat(modelo: str, system_prompt: str, contexto: str, pergunta: str) -> str: #cria a função ollama_chat, que é responsável por enviar a pergunta do usuário ao modelo de linguagem do Ollama, juntamente com o contexto relevante e o histórico de mensagens, e retornar a resposta gerada pelo modelo. A função constrói um payload com as mensagens formatadas, opções de geração de texto e faz uma requisição POST para o endpoint de chat do Ollama, processando a resposta para extrair o conteúdo da mensagem gerada.
    historico = obter_historico_curto(max_msgs=8) #declara a variavel que recebe as 8 mensagens mais recentes do chat.
    mensagens = [   #constrói a lista de mensagens para enviar ao modelo, começando com o system_prompt e o contexto do banco de dados, seguido pelo resumo da conversa até agora (se existir) e as mensagens recentes do histórico, garantindo que o modelo de linguagem tenha acesso a informações relevantes para gerar uma resposta informada e contextualizada.
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"DADOS DO BANCO:\n{contexto}"},
    ]
    resumo = (st.session_state.get("summary") or "").strip() #declara a variavel resumo que recebe o resumo acumulado do session_state, ou uma string vazia caso não haja resumo, e remove os espaços em branco no início e no final do resumo. O resumo acumulado é o resultado das chamadas anteriores à função de resumo, e é atualizado a cada vez que o histórico de mensagens ultrapassa o limite definido, permitindo que o modelo de linguagem mantenha um contexto relevante da conversa ao longo do tempo.
    if resumo: #se resumo não estiver vazio após o strip.
        mensagens.append({"role": "system", "content": f"RESUMO DA CONVERSA ATÉ AGORA:\n{resumo}"}) #resumo sera adicionado a lista de mensagens como uma mensagem do sistema, fornecendo ao modelo de linguagem um contexto condensado da conversa até o momento, o que pode ajudar a gerar respostas mais relevantes e informadas.

    for msg in historico: #para cada mensagem msg no historico(ultimas 8 mensagens).
        if msg.get("role") in ("user", "assistant") and (msg.get("content") or "").strip(): # se mensagem tiver role de user ou assistant e tiver conteudo (content) ou vazio e o conteudo não for vazio após o strip.
            if msg["role"] == "user" and msg["content"].strip() == pergunta.strip(): # se for usuario e a mensagem com strip for igual a pergunta com strip. 
                continue #pula esta mensagem para evitar duplicar a pergunta atual no histórico, garantindo que a pergunta seja adicionada apenas uma vez ao payload enviado para o modelo de linguagem, o que pode ajudar a evitar confusão e melhorar a qualidade da resposta gerada.
            mensagens.append({"role": msg["role"], "content": msg["content"]}) #adiciona mensagem.
    
    mensagens.append({"role": "user", "content": pergunta}) #adiciona a pergunta atual do usuário ao final da lista de mensagens, garantindo que o modelo de linguagem tenha acesso à pergunta mais recente para gerar uma resposta adequada e relevante.
   #assim o payload é construido com o system_prompt, o contexto do banco de dados a variavel resumo se existir as mensagens recentes so historico e a pergunta atual do usuario, fornecendo ao modelo de linguagem todas as informações necessárias para gerar uma resposta informada e contextualizada. 
    payload = {
        "model": modelo, #modelo a ser utilizado para gerar respostas, definido pela variável modelo passada como argumento da função.
        "messages": mensagens, #lista de mensagens formatadas que inclui o system_prompt, o contexto do banco de dados, o resumo da conversa (se existir), as mensagens recentes do histórico e a pergunta atual do usuário, fornecendo ao modelo de linguagem um contexto completo para gerar uma resposta relevante.
        "options": {
            "temperature": 0.15,       # Respostas mais focadas e menos criativas, ideal para recomendações financeiras.
            "top_p": 0.75,             # Considera as palavras mais prováveis até atingir 75% da distribuição, equilibrando qualidade e diversidade.
            "repeat_penalty": 1.18,     # Penaliza repetições, incentivando o modelo a fornecer informações novas e evitar redundâncias.
            "presence_penalty": 0.1,        # Incentiva o modelo a falar sobre novos tópicos, mas de forma leve, para manter a relevância.
            "frequency_penalty": 0.2        # Penaliza palavras que já foram usadas com mais frequência, ajudando a evitar respostas repetitivas e incentivando a variedade de vocabulário.
            },
        "stream": False #só mostra a resposta final sem enviar partes.
    }#O payload é então enviado para o endpoint de chat do Ollama, onde o modelo de linguagem processa as mensagens e gera uma resposta com base no contexto e na pergunta fornecidos.
    r = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=REQUEST_TIMEOUT) # variavel r recebe a resposta da requisição POST feita para o endpoint de chat do Ollama, onde o payload é enviado como JSON e o tempo máximo de espera pela resposta é definido por REQUEST_TIMEOUT. Esta requisição é responsável por enviar as mensagens formatadas para o modelo de linguagem e obter a resposta que contém a resposta gerada.
    if r.status_code != 200:# Se deu erro HTTP (ex: modelo não existe).
        raise RuntimeError(f"Ollama HTTP {r.status_code}: {r.text}") #manda mensagem de erro com ostatus code e o texto de resposta.
    data = r.json() #declara a variavel data que recebe o conteúdo da resposta convertida de JSON para um dicionário Python, permitindo acessar os dados retornados pelo modelo de linguagem, como a mensagem gerada, o resumo atualizado e outras informações relevantes para o chatbot.
    return data["message"]["content"] # retorna o conteudo da mensagem gerada pelo chatbot.
normalizar_mensagens() #chama a função normalizar_mensagens para garantir que o histórico de mensagens no session_state esteja em um formato consistente antes de qualquer interação com o modelo de linguagem, facilitando o processamento e a geração de respostas pelo chatbot.
#=============================================================
#==========CARREGAMENTO DE DADOS (MEMÓRIA CACHE)===============
@st.cache_data(show_spinner=False, ttl=300)  # cache com expiração (5 minutos) para os produtos financeiros, que são dados relativamente estáticos e não mudam com frequência. Isso ajuda a melhorar o desempenho do aplicativo, evitando consultas repetidas ao banco de dados para obter os mesmos dados, enquanto ainda garante que as informações sejam atualizadas periodicamente.
def carregar_produtos() -> pd.DataFrame: #função para carregar os produtos financeiros do banco de dados e retornar um DataFrame do Pandas.
    # Igual para todos → cache global
    return ler_df("SELECT * FROM produtos_financeiros;")


@st.cache_data(show_spinner=False, ttl=300)  # cache com expiração (5 minutos) para os dados do usuário, que podem mudar com o tempo (por exemplo, perfil de investidor, metas, histórico
def carregar_dados_usuario(cpf_digits: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: #função para carregar os dados do usuário (perfil, metas, histórico, transações) do banco de dados com base no CPF fornecido, retornando uma tupla de DataFrames do Pandas.
    perfil = ler_df( #query SQL para obter o perfil do investidor com base no CPF fornecido.
        """
        SELECT nome_investidor, cpf, idade, profissao, renda_mensal, perfil,
               objetivo_principal, patrimonio, reserva, risco
        FROM perfil_investidor
        WHERE regexp_replace(cpf::text, '[^0-9]', '', 'g') = %s
        LIMIT 1;
        """,
        params=(cpf_digits,) #parâmetros para a consulta SQL, onde cpf_digits é o CPF do usuário sem formatação (apenas dígitos
    )
    metas = ler_df( #query SQL para obter as metas do investidor com base no CPF fornecido.
        """
        SELECT * FROM metas_investidor
        WHERE regexp_replace(cpf_investidor::text, '[^0-9]', '', 'g') = %s;
        """,
        params=(cpf_digits,)    
    )
    historico = ler_df(  #query SQL para obter o histórico de atendimento do investidor com base no CPF fornecido.
        """
        SELECT * FROM historico_atendimento
        WHERE regexp_replace(cpf::text, '[^0-9]', '', 'g') = %s
        ORDER BY data DESC
        LIMIT 10;
        """,
        params=(cpf_digits,)
    ) #adicionei um limite de 10 para demonstração pois se fosse em um caso real poderia gerar uma sobrecarga de informações.
    transacoes = ler_df( #query SQL para obter as transações do investidor com base no CPF fornecido.
        """
        SELECT * FROM transacoes
        WHERE regexp_replace(cpf::text, '[^0-9]', '', 'g') = %s
        ORDER BY data DESC
        LIMIT 20;
        """,
        params=(cpf_digits,)
    )#adicionei um limite de 20 para demonstração pois se fosse em um caso real poderia gerar uma sobrecarga de informações.
    return perfil, metas, historico, transacoes #retorna os DataFrames do perfil, metas, histórico e transações do usuário.

@st.cache_data(show_spinner=False, ttl=300)  # cache com expiração (5 minutos) em bora os dados são fixos nesta aplicação fica aqui uma melhoria pro mundo real que é para não ficar com dados muito antigos caso o usuário deixe o app aberto por muito tempo
def montar_contexto(cpf_digits: str | None) -> tuple[str, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: #função para montar o contexto completo para o chatbot, incluindo os produtos financeiros e os dados do usuário (perfil, metas, histórico, transações) se o CPF for fornecido. A função retorna uma tupla contendo o contexto em formato de texto e os DataFrames correspondentes.
    """
    Retorna:
      contexto_texto, produtos, perfil, metas, historico, transacoes
    """
    partes = [] #declara a variavel partes como uma lista vazia
    produtos = carregar_produtos() # variavel produtos recebe o resultado da função carregar_produtos, que é um DataFrame do Pandas contendo os produtos financeiros disponíveis no banco de dados.
    partes.append("### produtos_financeiros (COMPLETO)\n" + produtos.to_csv(index=False) + "\n") # adiciona o conteudos a partes.

    if not cpf_digits: # se não tem cpf usuario esta como visitante, então não tem dados para filtrar, entao é adicionado um aviso a partes e as variaveis de perfil, metas, historico e transacoes recebem DataFrames vazios, garantindo que o chatbot funcione mesmo para usuários sem identificação, mas com acesso limitado a recomendações genéricas.
        partes.append("### AVISO\nUsuário sem identificação: não há dados pessoais para filtrar.\n")
        vazio = pd.DataFrame()  #variavel vazio recebe o DataFrame vazio do Pandas.
        return "\n".join(partes), produtos, vazio, vazio, vazio, vazio #retorna o contexto em formato de texto, os produtos financeiros e DataFrames vazios para perfil, metas, histórico e transações.

    perfil, metas, historico, transacoes = carregar_dados_usuario(cpf_digits) #se o CPF for fornecido, as variáveis perfil, metas, historico e transacoes recebem os DataFrames correspondentes aos dados do usuário, que são carregados usando a função carregar_dados_usuario com base no CPF fornecido. Esses dados serão usados para personalizar as recomendações de investimento e fornecer um contexto mais relevante para o chatbot.

    partes.append("### perfil_investidor (CPF logado)\n" + perfil.to_csv(index=False) + "\n")       #adiciona o conteudo do perfil do investidor.
    partes.append("### metas_investidor (CPF logado)\n" + metas.to_csv(index=False) + "\n")     #adiciona o conteudo das metas do investidor.
    partes.append("### historico_atendimento (CPF logado)\n" + historico.to_csv(index=False) + "\n")    #adiciona o conteudo do historico de atendimento do investidor.
    partes.append("### transacoes (CPF logado)\n" + transacoes.to_csv(index=False) + "\n")      #adiciona o conteudo das transações do investidor.
    #retorna o contexto completo em formato de texto, os produtos financeiros e os DataFrames do perfil, metas, histórico e transações do usuário, que serão usados para personalizar as recomendações de investimento e fornecer um contexto mais relevante para o chatbot.
    return "\n".join(partes), produtos, perfil, metas, historico, transacoes  

if st.session_state.get("logado"): #se o usuário estiver logado, a variável cpf_digits recebe o CPF do usuário formatado, convertido para apenas dígitos usando a função cpf_para_digitos. Isso é necessário para filtrar os dados do usuário no banco de dados e fornecer um contexto personalizado para o chatbot, permitindo que ele faça recomendações de investimento com base no perfil,
    cpf_digits = cpf_para_digitos(st.session_state.cpf_formatado) #a função cpf_para_digitos é usada para remover qualquer formatação do CPF (como pontos e traços) e retornar apenas os dígitos, garantindo que o CPF seja tratado de forma consistente ao consultar o banco de dados e montar o contexto para o chatbot.
else:
    cpf_digits = None #se o usuário não estiver logado, a variável cpf_digits é definida como None, indicando que não há um CPF específico para filtrar os dados do usuário no banco de dados. Isso significa que o chatbot funcionará em um modo mais genérico, sem acesso a informações personalizadas do usuário, e as recomendações de investimento serão baseadas apenas nos produtos financeiros disponíveis, sem considerar o perfil ou histórico do usuário.

contexto_dados, produtos, perfil, metas, historico, transacoes = montar_contexto(cpf_digits) #chama a função montar_contexto com o cpf_digits (que pode ser None para usuários não logados) para obter o contexto completo em formato de texto, os produtos financeiros e os DataFrames do perfil, metas, histórico e transações do usuário. Esses dados serão usados para personalizar as recomendações de investimento e fornecer um contexto mais relevante para o chatbot ao gerar respostas para as perguntas dos usuários.
#=============================================================
#=========================FUNÇÕES DE ÁUDIO (TTS)=========================
language = "pt-BR"  #define idioma para português, utilizado em funções de transcrição e TTS para garantir que o reconhecimento de voz e a geração de áudio sejam adequados para o público-alvo do chatbot, que é falante de português.
def transcrever_audio_google(audio_bytes: bytes, language: str = "pt-BR") -> str: #Função Transcreve áudio usando SpeechRecognition + Google Web Speech (precisa de internet).
    r = sr.Recognizer()  # declara a variavel r q recebe a instancia de reconhecer a voz da bibliteca SpeechRecognition.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f: # Cria arquivo temporario (Named) para salvar audio o delete é falso para poder usar o arquivo depois do with e o suffix é .wav porque o audio recebido do streamlit é em formato wav.
        f.write(audio_bytes) #escreve os bytes do áudio recebido para o arquivo temporário criado, permitindo que a biblioteca SpeechRecognition acesse o áudio para transcrição. O arquivo temporário é necessário porque a função AudioFile do SpeechRecognition espera um caminho de arquivo, e não pode processar diretamente os bytes do áudio.
        caminho = f.name #declara a variavel caminho que recebe o nome do arquivo temporário criado, que é o caminho para o arquivo de áudio que será processado pela biblioteca Speech

    try: #tente
        with sr.AudioFile(caminho) as source: #com o arquivo de audio variavel caminho aberto 
            audio_data = r.record(source) # a variavel audio_data recebe o conteúdo do arquivo de áudio processado pela biblioteca SpeechRecognition, que é usado para transcrição. A função record() é usada para ler o áudio do arquivo e armazená-lo em um formato que pode ser enviado para o serviço de reconhecimento de voz do Google para obter a transcrição em texto.
        texto = r.recognize_google(audio_data, language=language) # a variavel texto recebe a transcrição do áudio processado, usando o serviço de reconhecimento de voz do Google. A função recognize_google() é chamada com os dados de áudio e o idioma especificado para obter a transcrição em texto do áudio, que pode ser usada como entrada para o chatbot ou para outras funcionalidades do aplicativo.
        return texto.strip()  #retorna o texto transcrito, removendo espaços em branco no inicio e final da string
    finally: #finalmente
        try: #tente
            os.remove(caminho) #remover o caminho garantindo que o arquivo temporário seja excluido do sistema evitando acumulo de arquivos.
        except Exception: #se der erro só passa pois isso não é critico e evita do app quebrar por por um arquivo temporario.
            pass 
def texto_para_audio_mp3_bytes(texto: str, language: str = "pt") -> bytes: #Gera MP3 (bytes) com gTTS (precisa de internet).
    tts = gTTS(text=texto, lang=language) #tts recebe a instancia do gtt com o texto e idioma definido para gerar audio.
    buf = io.BytesIO()  # buf é armazenado io.BytesIO() ou seja ele vai armazenar os bytes do audio gerado na memória.
    tts.write_to_fp(buf) # tts escreve os bytes do audio armazenados em buf.
    return buf.getvalue() # retorna os bytes de audio gerados.
def limpar_para_tts(texto: str) -> str:  #limpa o texto para melhorar pronuncia em TTS removendo markdown,códigos e simbolos.
    RE_CODEBLOCK = re.compile(r"```.*?```", re.S) 
    RE_MD = re.compile(r"[*_`|>#]")
    RE_TECH = re.compile(r"[\\/+=~^]")
    RE_SPACES = re.compile(r"\s+")

    texto = RE_CODEBLOCK.sub(" ", texto) 
    texto = RE_MD.sub(" ", texto)
    texto = RE_TECH.sub(" ", texto)
    texto = RE_SPACES.sub(" ", texto).strip()
    return texto #retorna texto limpo.
#===============================================================
#=========================MENU LATERAL=========================
with st.sidebar: #declara que tudo aqui é do menu lateral do Streamlit.
    st.header("⚙️ Configurações") #título do menu lateral.

    try:  #tente
        resp = requests.get(f"{Ollama_BASE}/api/tags", timeout=20) #resp recebe a requisiçaõ GET para o end point de tags do Ollama para verificar se o serviço está online, com um tempo máximo de espera de 20 segundos. Esta requisição é usada para determinar o status do serviço do Ollama.
        cor = resp.status_code # cor recebe o status code de resp.
    except Exception as e: #exceto se der erro na requisição 
        st.write("Erro de conexão:", e) #escreve mensagem de erro exibindo a exceção que ocorreu durante tentativa de conexão.
        cor = 500 # cor recebe valor de 500 
    if cor == 200: # cor deu 200 então aparece os status text e cor verde, caso contrário vermelho.
        status_text = "🟢 Online"
        status_color = "#008000"
    else:
        status_text = "🔴 Offline"
        status_color = "#FF0000"

    st.markdown( #escreve o status do serviço do Ollama no menu lateral, usando markdown para formatar o texto com a cor definida por status_color e deixando o texto em negrito.
        f"<span style='color:{status_color}; font-weight:bold;'>Status: {status_text}</span>",
        unsafe_allow_html=True
    )
    modelo = st.text_input("Modelo (Ollama)", value=DEFAULT_MODEL) # campo de texto onde usuário ve o modelo que esta sendo utilizado.

    st.divider() #linha divisória para separar visualmente as seções do menu lateral.
    st.subheader("Usuário")  #subtítulo da seção de usuário no menu lateral.

    if st.session_state.logado: # se o usuario estive logado.
        st.sidebar.success("✅ Logado") #exibe mensagem logado.
        st.sidebar.write(f"CPF: {st.session_state.cpf_formatado}") #exibe o cpf do usuário formatado na lateral.
        carrega_no_ollama = cpf_para_digitos(st.session_state.cpf_formatado) #variavel carrega_no_ollama recebe o cpf do usuario formatado.
    
    elif st.session_state.visitante: #se o usuario for visitante.
        st.sidebar.info("👤 Visitante")  #mosta mensagem de visitante.
        carrega_no_ollama = None #variavel carrega_no_ollama recebe None.

    if st.sidebar.button("Sair"): #se clicar em sair
        st.session_state.logado = False # recebe False, ou seja, o usuário não está mais logado voltando para pagina de acesso.
        st.session_state.visitante = False # recebe False, ou seja, o usuário não está mais logado voltando para pagina de acesso.
        st.session_state.cpf_formatado = "" #limpa o cpf formatado do session_state.
        st.session_state.mensagens = [{"role": "assistant", "content": "Sextou! Como posso ajudar?"}] #reseta as mensagens para a mensagem inicial.
        carrega_no_ollama = None #variavel carrega_no_ollama recebe None.
        st.rerun() #recarrega a página para refletir as mudanças no estado, como o logout do usuário e a limpeza do histórico de mensagens, garantindo que o chatbot volte ao estado inicial e esteja pronto para um novo usuário ou para o mesmo usuário fazer login novamente.
    
    st.divider() #linha divisória para separar visualmente as seções do menu lateral.
    st.subheader("🔊 Voz")# subtitulo de seção

    permitir_audio = st.toggle("🎙️ Enviar áudio (microfone)", value=True) # botão para usuario configurar qeur utilizar microfone, inicialmente configurado com true.
    
    tts_on = st.toggle("🔊 Bot responder em áudio (TTS)", value=True) # botão para usuario configurar quer que IA fale, inicialmento configurado como true.
    
    st.divider() #linha divisória para separar visualmente as seções do menu lateral.
    st.subheader("🧹 Limpar histórico") #subtítulo da seção de limpeza de histórico no menu lateral.
    limpar = st.button("🧹 Limpar chat") #botão limpar
    if limpar: # se clicar em limpar chat
        st.session_state.mensagens = []  #limpa as mensagens do session_state, removendo todo o histórico de mensagens do chat.     
        st.session_state.mensagens = [{"role": "assistant", "content": "Conversa limpa. Sextou! Como posso ajudar?"}]   #adiciona uma mensagem inicial ao histórico.
        st.session_state.summary = "" #limpa o resumo acumulado do session_state, garantindo que o chatbot comece com um contexto limpo e sem informações anteriores.
        st.rerun() #recarrega a pagina para refletir as mudanças no estado.
    st.divider() #linha divisória para separar visualmente as seções do menu lateral.
    st.subheader("💾 Exportar histórico") 
    mensagens_txt = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.mensagens]) 
    #variavel mensagens_txt recebe uma string formatada que contém o histórico de mensagens do chat, onde cada mensagem é representada por seu papel (role) em letras maiúsculas seguido pelo conteúdo da mensagem. O método join() é usado para concatenar todas as mensagens em uma única string, separando cada mensagem por uma nova linha (\n), facilitando a leitura e exportação do histórico de mensagens.
    resumo = st.session_state.get("summary", "") #variavel resumo recebe o resumo acumulado do session_state, ou uma string vazia caso não haja resumo. O resumo acumulado é o resultado das chamadas anteriores à função de resumo, e é atualizado a cada vez que o histórico de mensagens ultrapassa o limite definido, permitindo que o modelo de linguagem mantenha um contexto relevante da conversa ao longo do tempo. Se houver um resumo disponível.
    if resumo: #seresumo não estiver vazio.
        mensagens_txt = f"RESUMO:\n{resumo}\n\n{mensagens_txt}" #é adicionado ao inicio de mensagens_txt.
    st.download_button("Baixar histórico (.txt)", mensagens_txt, file_name="historico_chat.txt") #botão para baixar o historico de mensagens.
#==============================================================
#=========================CORPO DO APP=========================
st.title("Sexta-Feira - Assistente de Investimentos 🚀") # título do app 

for m in st.session_state["mensagens"]: #para cada mensagem m no historico de mensagens.
    with st.chat_message(m["role"], avatar=("🧑‍💻" if m["role"] == "user" else "🌐")): #com se o role for de user então é um avatar se não é o outro.
        st.write(m["content"]) #escreve o conteúdo da mensagem no chat, garantindo que o histórico de mensagens seja exibido corretamente com os avatares correspondentes para o usuário e o assistente.

entrada = st.chat_input("Digite sua mensagem aqui...", accept_audio=permitir_audio) #campo de entrada para o usuário digitar sua mensagem, com um placeholder "Digite sua mensagem aqui..." e a opção de aceitar áudio configurada com base na variável permitir_audio, permitindo que o usuario tire essa opção pelo menu lateral.

texto_usuario = "" # declara a variavel como string vazia.
audio_bytes = None #declara variavel como none
audio_file = None #declara variavel como none

if entrada is not None: #se o usuário enviou uma entrada (texto ou áudio).

    if isinstance(entrada, str): #se entrada for do tipo string
        texto_usuario = entrada.strip() #a variavel texto usuario recebe este valor

    elif hasattr(entrada, "text"): #se não se for identificao como text.
        texto_usuario = (entrada.text or "").strip()    # texto recebe entrada do tipo texto ou fica vazia
        audio_file = getattr(entrada, "audio", None)    # tenta pegar audio se não consegue fica none

    else:
        texto_usuario = str(entrada).strip() #se não texto usuario é a entrada convetida em string

    if audio_file is not None: #se arquivo de audio não esta vazio
        audio_bytes = audio_file.getvalue()  #variavel recebe valor do arquivo

    if (not texto_usuario) and audio_bytes: # Se não digitou texto, mas veio áudio: transcreve
        try: #tente
            texto_usuario = transcrever_audio_google(audio_bytes, language) #chama função com os parametros audio_bytes e language
            # st.toast(f"📝 {texto_usuario}") código utilizado mais para teste porem resolvi deixar porque achei bonito e dependendo da opnião de cada um seeria mais legal deixar ou tirar essa funcionalidade
        except Exception as e:  #excessão de erro
            st.error("Erro ao transcrever áudio.")
            st.exception(e)
            texto_usuario = ""

    if texto_usuario: #Só processa se tiver texto
        st.session_state["mensagens"].append({"role": "user", "content": texto_usuario}) # salva msg do usuário
        with st.chat_message("user", avatar="🧑‍💻"): #adciona avatar de usuario
            st.write(texto_usuario) #escreve o texto no chat

        with st.chat_message("assistant", avatar="🌐"):# chama IA definindo um avatar IA
            thinking_placeholder = st.empty() #adiciona um icone de pensamento com a menssagem enquanto que IA elabora resposta
            thinking_placeholder.info("Sexta-Feira está pensando...")
            try: #tenta resposta pela função ollama chat chamando o texto do usuario, os dados do banco de dados que estão em memoria cach sua memória e seu system prompt.
                resposta = ollama_chat(modelo, SYSTEM_PROMPT_DEFAULT, contexto_dados, texto_usuario)
            except Exception as e: #caso de erro mostrar as seguntem mensagens
                st.error("Falha ao chamar o Ollama (erro real abaixo):")
                st.exception(e)  # <- mostra stack trace completo no Streamlit
                resposta = "Não consegui acessar o Ollama. Veja o erro acima."

            thinking_placeholder.empty() #icone de pensamento some
            st.write(resposta) #escreve a resposta

        st.session_state["mensagens"].append({"role": "assistant", "content": resposta}) # mostra resposta no chat.
        try: #chama função para averiguar se ja pode criar um resumo pra IA.
            talvez_resumir_chat(modelo)
        except Exception as e: #caso de erro mostrar mensagem.
            st.warning("Não consegui resumir o histórico agora.")
            st.caption(str(e))

        if tts_on: #se o botão do menu lateral tts tiver true.
            try: #chamar função  para converter texto em audio.
                texto_limpo = limpar_para_tts(resposta)
                mp3_bytes = texto_para_audio_mp3_bytes(texto_limpo, language)
                st.audio(mp3_bytes, format="audio/mp3")
            except Exception as e: #caso de erro mostrar mensagem.
                st.warning("Não consegui gerar o áudio da resposta.")
                st.caption(str(e))

        MAX_MENSAGENS = 20 
        if len(st.session_state["mensagens"]) > MAX_MENSAGENS:  ##numero maximo a ser exibida na tela de mensagem no chatbot
            st.session_state["mensagens"] = st.session_state["mensagens"][-MAX_MENSAGENS:]

#=============================================================
#=========================FIM DO APP=========================    