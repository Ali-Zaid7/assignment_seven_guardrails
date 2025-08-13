
import os
from pydantic import BaseModel
from agents import(
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig,
    set_default_openai_client,
    set_tracing_disabled
)
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")


if not gemini_api_key:
  raise ValueError("API key is Missing!")

external_clients = AsyncOpenAI(api_key=gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model =OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=external_clients)
config =RunConfig

set_default_openai_client(external_clients)
set_tracing_disabled(True)