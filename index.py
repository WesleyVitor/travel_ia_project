import os
import openai
from langchain_core.messages import HumanMessage

from langchain_openai import ChatOpenAI


from tools import airbnb_search, duffel_search
from agent import Agent


llm = ChatOpenAI(
    temperature=0.0, 
    model="gpt-4o-mini", 
    api_key=os.getenv("OPENAI_API_KEY")
)

agent = Agent(
    model=llm,
    tools=[airbnb_search, duffel_search]
)

# Transcribe the audio file

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()
audio_file = open("gravacao.ogg", "rb")

translation = client.audio.translations.create(
    model="whisper-1", 
    file=audio_file
)

# user_m = """
# Entre a data 2025-08-10 e a data 2025-08-13, eu quero passar 5 dias na cidade Miami. 
# Estou disposto a gastar o valor 400 em passagens e 1000 em hospedagem. 
# Para a hospedagem, quero ficar em um quarto com as seguintes características: com wifi. 
# Quais opções eu tenho?
# """
messages = [HumanMessage(content=translation.text),]
result = agent.graph.invoke({"messages": messages})
print(result['messages'][-1].content)