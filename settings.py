import os

from langchain_openai import ChatOpenAI

os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

CHROMA_HOST = os.getenv("CHROMA_HOST", "api.trychroma.com")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
CHROMA_TOKEN = os.getenv("CHROMA_TOKEN")

MODELS = {
    "gpt-3.5-turbo": ChatOpenAI(model="gpt-3.5-turbo"),
    "gpt-4o-mini": ChatOpenAI(model="gpt-4o-mini"),
    "gpt-4o": ChatOpenAI(model="gpt-4o", temperature=0.0),
    "o3-mini": ChatOpenAI(model="o3-mini"),
}
