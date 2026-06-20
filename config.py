"""
Configuração do Jarvis Gordo — Fase 0 (esqueleto do agente).

O cérebro é o Gemma 4 12B-it rodando local via Ollama (API compatível com OpenAI).
Troque BASE_URL/MODEL se usar llama.cpp (llama-server) ou outro endpoint.
"""

import os

# Endpoint local compatível com OpenAI.
# LM Studio:     http://localhost:1234/v1   (padrão do "Local Server" do LM Studio)
# Ollama:        http://localhost:11434/v1
# llama-server:  http://localhost:8080/v1
BASE_URL = os.environ.get("GORDAO_BASE_URL", "http://localhost:1234/v1")

# Nome do modelo no servidor.
# LM Studio: o id que aparece no painel do modelo carregado (ex.: "google/gemma-4-12b-it")
# Ollama:    "gemma-4-12b-it" ou similar, após `ollama pull ...`
MODEL = os.environ.get("GORDAO_MODEL", "google/gemma-4-12b-it")

# Chave de API — local não exige, mas o cliente OpenAI precisa de algo.
API_KEY = os.environ.get("GORDAO_API_KEY", "lm-studio")

# Amostragem recomendada pelo Gemma 4.
TEMPERATURE = 1.0
TOP_P = 0.95

# Caminho do system prompt (a "alma" do Gordão).
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "gordao_system_prompt.txt")


def load_system_prompt() -> str:
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()
