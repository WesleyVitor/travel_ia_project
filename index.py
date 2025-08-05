import os
import openai
from langchain_core.messages import HumanMessage

from langchain_openai import ChatOpenAI


from tools import airbnb_search, duffel_search
from agent import Agent
from agent2 import Agent as Agent2

import gradio as gr


def handle_audio(file_path):
    output = ""
    llm = ChatOpenAI(
        temperature=0.0, 
        model="gpt-4.1-mini", 
        api_key=os.getenv("OPENAI_API_KEY")
    )

    agent = Agent(
        model=llm,
        tools=[airbnb_search, duffel_search]
    )

    # Transcribe the audio file

    openai.api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI()
    #audio_file = open("gravacao.ogg", "rb")
    with open(file_path, "rb") as file:
        translation = client.audio.translations.create(
            model="whisper-1", 
            file=file
        )

        # user_m = """
        # Eu moro em são paulo e entre 10 de agosto de 2025 e 13 de agosto de 2025, eu quero passar 3 dias na cidade de Miami. 
        # Estou disposto a gastar o valor 400 dolares em passagens e 1000 dolares em hospedagem. 
        # Para a hospedagem, quero ficar em um quarto com wifi. 
        # Quais opções eu tenho?
        # """
        messages = [HumanMessage(content=translation.text),]
        print(messages)
        result = agent.graph.invoke({"messages": messages})
        #print(result['messages'][-1].content)
        output = result['messages'][-1].content
    return output  

input_audio = gr.Audio(
    sources=["microphone"],
    type="filepath",  # importante: retorna caminho para arquivo .ogg
    label="Grave seu áudio",
    waveform_options=gr.WaveformOptions(
        waveform_color="#01C6FF",
        waveform_progress_color="#0066B4",
        skip_length=2,
        show_controls=False,
    ),
)

output = gr.Textbox(label="Output")

demo = gr.Interface(
    fn=handle_audio,
    inputs=input_audio,
    outputs=output
)

demo.launch(share=False)