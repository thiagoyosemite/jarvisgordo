"""
Ferramentas (tools) do Jarvis Gordo.

Cada ferramenta tem:
  1. um SCHEMA (formato OpenAI/Gemma function calling) que o modelo enxerga;
  2. uma função Python que executa de verdade.

Fase 0: ferramentas de teste (hora, agenda fake, dado).
Fase 2: busca na web REAL (web_search). Próximas: agenda real, e-mail, arquivos.
"""

from datetime import datetime
import random

from memory import remember_fact


def web_search(query: str, max_results: int = 5) -> str:
    """Busca real na web via DuckDuckGo (sem API key). Retorna títulos, trechos e links."""
    try:
        try:
            from ddgs import DDGS          # pacote novo
        except ImportError:
            from duckduckgo_search import DDGS  # nome antigo, fallback
    except ImportError:
        return ("[web_search indisponível] Falta a lib. Rode: "
                "pip install ddgs")
    try:
        n = max(1, min(int(max_results), 8))
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=n))
    except Exception as e:  # noqa: BLE001
        return f"[erro na busca] {e}"
    if not resultados:
        return f"Nenhum resultado para: {query}"
    linhas = []
    for i, r in enumerate(resultados, 1):
        titulo = r.get("title", "(sem título)")
        corpo = (r.get("body") or "").strip().replace("\n", " ")
        link = r.get("href") or r.get("url") or ""
        linhas.append(f"{i}. {titulo}\n   {corpo}\n   {link}")
    return "\n".join(linhas)

# --- implementações reais ---------------------------------------------------

def get_current_time(timezone: str = "local") -> str:
    """Retorna a data e hora atuais."""
    agora = datetime.now()
    return agora.strftime("%A, %d/%m/%Y %H:%M:%S")


def get_fake_calendar(day: str = "hoje") -> str:
    """Stub de agenda — devolve eventos fixos só pra testar o fluxo de tool."""
    eventos = {
        "hoje": ["10:00 Reunião com o time", "14:30 Code review", "18:00 Academia (vai que vai)"],
        "amanhã": ["09:00 Dentista", "15:00 Call com cliente"],
    }
    lista = eventos.get(day.lower(), [])
    if not lista:
        return f"Sem eventos para '{day}'."
    return f"Eventos de {day}: " + "; ".join(lista)


def roll_dice(sides: int = 6) -> str:
    """Rola um dado de N lados — ferramenta boba pra testar argumentos numéricos."""
    if sides < 2:
        return "Dado precisa de pelo menos 2 lados, bicho."
    return f"Tirei {random.randint(1, sides)} num dado de {sides} lados."


# --- schemas que o modelo vê ------------------------------------------------

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Busca na internet em tempo real. Use SEMPRE que precisar de fatos atuais, notícias, preços, resultados, ou qualquer coisa que você não saiba de cabeça ou que possa ter mudado. Não invente — busque.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "O que pesquisar, em linguagem natural.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Quantos resultados trazer (1 a 8). Padrão: 5.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Salva na memória de longo prazo um fato sobre o Thiago ou algo que ele pediu pra lembrar (preferências, nomes, projetos, gostos, etc.). Use quando ele contar algo que valha a pena lembrar nas próximas conversas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "O fato a lembrar, em uma frase curta e clara.",
                    }
                },
                "required": ["fact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Retorna a data e hora atuais. Use quando perguntarem que horas são ou que dia é hoje.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Fuso horário (opcional). Padrão: local.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fake_calendar",
            "description": "Consulta a agenda do Thiago (versão de teste). Use quando perguntarem sobre compromissos/eventos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "Dia a consultar, ex.: 'hoje' ou 'amanhã'.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "roll_dice",
            "description": "Rola um dado de N lados. Ferramenta de teste para argumentos numéricos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sides": {
                        "type": "integer",
                        "description": "Número de lados do dado. Padrão: 6.",
                    }
                },
                "required": [],
            },
        },
    },
]

# Mapa nome -> função, usado pelo loop do agente para despachar a chamada.
TOOLS_REGISTRY = {
    "web_search": web_search,
    "remember": remember_fact,
    "get_current_time": get_current_time,
    "get_fake_calendar": get_fake_calendar,
    "roll_dice": roll_dice,
}
