# 1) receber a query/pergunta de um usuário
# 2) ele vai passar por um nó que responde a pergunta
# 3) Outro nó vai ler a resposta e o sistema human in the loop precisará ser ativado para que o usuário diga se o resultado foi
# satisfatório ou não... se foi interrompe o fluxo, se não foi, começa do zero 

# ANOTACOES:
# Seria interessante que ao inves de repetir apenas o fluxo, a condicional do usuario mudasse a temperatura ou adicionasse
# um prompt explicando para a AI realizar uma melhora

from langgraph.graph import StateGraph 
from langgraph.graph import END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LLM = ChatOpenAI(
    model= "gpt-3.5-turbo",
    temperature= 0.7,
    api_key= OPENAI_API_KEY)

print("Digite encerrar para finalizar")

# Classe de estado
class State(TypedDict):
    
    pergunta: str
    resposta: str
    satisfacao: str
    
# Pega o input do user e define como state["pergunta"]
def perguntar(state: State):
    pergunta = input("Qual a sua pergunta? ")
    state["pergunta"] = pergunta
    return state
    
# Retorna como state["resposta"]
def responder(state: State):
    
    perguntaUser = state["pergunta"]
    resposta = LLM.invoke(perguntaUser)
    enviar = state["resposta"] = resposta.content
    return state

# Pega a avalicao do user e torna o state["satisfacao"] 
# para que a condicao seja possivel
def avaliar(state: State):
    
    print(state['resposta'])
    avalicao = input("Vc gostou da resposta? ")
    state["satisfacao"] = avalicao
    return state

#human in the loop:
def verificar(state: State):
    return state["satisfacao"]

# Grafos:
# Aqui estamos criando uma instancia graph que recebe os atributos da classe State que criamos
# A class StateGraph serve para montar o fluxo
graph = StateGraph(State)

# O metodo recebe dois valores, sendo o primeiro o nome (identificador do nó) que estamos dando ao
# nó e o segundo a função que estamos nomeando
graph.add_node("perguntar", perguntar)
graph.add_node("responder", responder)
graph.add_node("avaliar", avaliar)

graph.set_entry_point("perguntar")

graph.add_edge("perguntar", "responder")
graph.add_edge("responder", "avaliar")

graph.add_conditional_edges(
    "avaliar",
    verificar,
    {
        "sim": END,
        "nao": "perguntar"
    }
)

# Execucao
app = graph.compile()
fluxo = {"pergunta": "", "resposta": "", "satisfacao": ""}
app.invoke(fluxo)