---
title: travel_ai_project
app_file: index.py
sdk: gradio
sdk_version: 5.38.0
---
# Goal

Build an application that transcribes and translates audio input to generate a personalized travel itinerary.
It retrieves flight data from the Duffel API and lodging options from Airbnb’s MCP, combining both into a complete travel plan.

# How run project

### Add environments variables

- OPENAI_API_KEY
- DUFFEL_API_KEY

### run 
```
python index.py
```

# Tecnologies 

- LangChain
- Airbnb MCP
- LangGraph
- Pydantic
- Whisper model(OpenAI)
- Duffel API