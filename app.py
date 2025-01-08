__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3') 

from crewai import Agent, Task, Crew
import os
from dotenv import load_dotenv

# Importando ferramentas
from crewai_tools import tool
import wikipedia

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# Chave da API OpenAI
os.environ["OPENAI_API_KEY"] = api_key
llm = "gpt-4o-mini"

@tool("pesquisa_wikipedia")
def pesquisa_wikipedia(q: str) -> str:
    "Pesquise uma consulta na Wikipedia e retorne um resumo"
    return wikipedia.page(q).summary

# Definindo os agentes
pesquisador_agente = Agent(
        role="Pesquisador",
        goal="Você pesquisa tópicos usando a Wikipedia e relata os resultados",
        backstory="Você é um escritor e editor experiente",
        tools=[pesquisa_wikipedia],
        llm=llm
    )
escritor_agente = Agent(
        role="Escritor",
        goal="Você reescreve artigos para que sejam divertidos, informativos e didáticos para crianças de 8 anos",
        backstory="Você é um escritor e editor experiente",
        llm=llm
    )
editor_agente = Agent(
        role="Editor",
        goal="Você garante que o texto fornecido está gramaticalmente correto em pt-br e com o tamanho apropriado",
        backstory="Você é um escritor e editor experiente",
        llm=llm
    )

# Função para executar a tarefa
def executar(s: str):
    tarefa1 = Task(
        description=s,
        expected_output='Um texto curto com base nos resultados da ferramenta',
        agent=pesquisador_agente,
        tools=[pesquisa_wikipedia]
    )
    tarefa2 = Task(
        description="Reescreva o texto para ser divertido, informativo e didático para leitores de 8 anos",
        expected_output='Um texto curto com base nos resultados da ferramenta',
        agent=escritor_agente,
    )
    tarefa3 = Task(
        description="Edite o texto para garantir que está gramaticalmente correto e não ultrapasse 50 palavras",
        expected_output='Um texto curto com base nos resultados da ferramenta',
        agent=editor_agente,
    )

    # Definindo o Crew
    equipe = Crew(
        agents=[pesquisador_agente, escritor_agente, editor_agente],
        tasks=[tarefa1, tarefa2, tarefa3],
        verbose=True
    )
    resultado = equipe.kickoff()
    return resultado.raw

###############################

# Interface no Streamlit
import streamlit as st

st.header("Wikipedia Divertida")

# Botão e entrada de texto
if "resposta" not in st.session_state:
    st.session_state.resposta = ""

# Entrada da pergunta
if q := st.text_input("Digite sua pergunta"):
    if st.button("Buscar Resposta"):
        resposta = executar(q)
        st.session_state.resposta = resposta

# Exibe a resposta
if st.session_state.resposta:
    st.markdown(f"**Resposta:**\n\n{st.session_state.resposta}")