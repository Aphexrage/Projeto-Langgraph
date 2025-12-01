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

# Classe de estado
class State(TypedDict):
    
    pergunta: str
    resposta: str
    satisfacao: str
    
# Pega o input do user e define como state["pergunta"]
def perguntar(state: State):
    
    state["pergunta"] = input("Qual a sua pergunta? ")
    return state
    
# Retorna como state["resposta"]
def responder(state: State):
    
    pergunta = LLM.invoke(state["pergunta"])
    state["pergunta"] = pergunta.content
    print(state["pergunta"])
    return state

# Quando o usuario dizer não, essa função deve pegar a resposta
# anterior e melhorar e mandar pro user novamente
def melhorarResposta(state: State):

    perguntaUser = state["pergunta"]
    state["pergunta"] = f"O usuario acredita que sua resposta deve ser melhor. Seja mais explicativo, detalhe e resuma mais e fale que vai tentar novamente. Pergunta que precisa de melhoria: {perguntaUser}"
    return state

# Pega a avalicao do user e torna o state["satisfacao"] 
# para que a condicao seja possivel
def avaliar(state: State):
    
    print(state['resposta'])
    state["satisfacao"] = input("Vc gostou da resposta? ")
    return state

#human in the loop:
def verificar(state: State):
    return state["satisfacao"]

# Grafos:
# Aqui estamos criando uma instancia graph que recebe os atributos da classe State que eu fiz
# A class StateGraph serve para montar o fluxo
graph = StateGraph(State)

# O metodo recebe dois valores, sendo o primeiro o nome (identificador do nó) que estamos dando ao
# nó e o segundo a função que estamos nomeando
graph.add_node("perguntar", perguntar)
graph.add_node("responder", responder)
graph.add_node("avaliar", avaliar)
# Adicionando um nó de melhoria
graph.add_node("melhoria", melhorarResposta)

# Aqui estou definindo qual grafo será executado primeiro
graph.set_entry_point("perguntar")

# Fluxo padrao:
graph.add_edge("perguntar", "responder")
graph.add_edge("responder", "avaliar")

# Fluxo implementando melhoria na resposta:
graph.add_edge("melhoria", "responder")
graph.add_edge("responder", "avaliar")

# Aqui estou basicamente criando uma adge entre dois nós (funcs) 
# Ou seja, quando perguntar retornar, responder sera ativada e 

# Aqui estou criando uma condicional de execucao de grafos 
# dependendo do resultado do state["satisfacao"]
graph.add_conditional_edges(
    "avaliar",
    verificar,
    {
        "sim": END,
        "nao": "melhoria"
    }
)

# Execucao
app = graph.compile()
fluxo = {"pergunta": "", "resposta": "", "satisfacao": ""}

app.invoke(fluxo)
