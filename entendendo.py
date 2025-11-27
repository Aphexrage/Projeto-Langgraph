# 1) receber a query/pergunta de um usuário

# 2) ele vai passar por um nó que responde a pergunta

# 3) Outro nó vai ler a resposta e o sistema human in the loop precisará ser ativado para que o usuário diga se o resultado foi
# satisfatório ou não... se foi interrompe o fluxo, se não foi, começa do zero 

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(
    model= "gpt-3.5-turbo",
    temperature= 0.5,
    api_key= OPENAI_API_KEY
)

print("Digite Encerrar para finalizar")

while True:
    perguntaUser = input("Qual a sua pergunta? ")
    resposta = model.invoke(perguntaUser)
    print (resposta.content)
    if "Encerrar" in perguntaUser:
        break