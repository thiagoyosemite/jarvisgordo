"""
Ferramentas (tools) do Jarvis Gordo — Fase 0.

Cada ferramenta tem:
  1. um SCHEMA (formato OpenAI/Gemma function calling) que o modelo enxerga;
  2. uma função Python que executa de verdade.

Aqui ficam só ferramentas de TESTE, pra validar que o Gemma chama tool
corretamente. Nas próximas fases entram agenda, e-mail, busca web, arquivos.
"""

from datetime import datetime
import random

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
    "get_current_time": get_current_time,
    "get_fake_calendar": get_fake_calendar,
    "roll_dice": roll_dice,
}
