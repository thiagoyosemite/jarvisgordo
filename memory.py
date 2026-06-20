"""
Memória persistente do Jarvis Gordo.

Guarda fatos sobre o Thiago (e o que ele pedir pra lembrar) num arquivo
local `memory.json`, que é carregado no início de cada sessão e injetado
no system prompt. Assim o Gordão não esquece tudo ao fechar.

memory.json contém dados pessoais → fica FORA do repositório (.gitignore).
"""

import json
import os

MEM_PATH = os.path.join(os.path.dirname(__file__), "memory.json")


def _load() -> dict:
    if not os.path.exists(MEM_PATH):
        return {"fatos": []}
    try:
        with open(MEM_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "fatos" not in data or not isinstance(data["fatos"], list):
                return {"fatos": []}
            return data
    except Exception:  # noqa: BLE001
        return {"fatos": []}


def _save(data: dict) -> None:
    with open(MEM_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def remember_fact(fact: str) -> str:
    """Salva um fato pra lembrar nas próximas conversas."""
    fact = (fact or "").strip()
    if not fact:
        return "Não tem nada pra anotar, bicho."
    data = _load()
    if fact in data["fatos"]:
        return "Já sei disso, não precisa repetir."
    data["fatos"].append(fact)
    _save(data)
    return f"Anotado (e não vou esquecer): {fact}"


def get_memory_text() -> str:
    """Devolve os fatos salvos como texto, pra injetar no system prompt."""
    data = _load()
    if not data["fatos"]:
        return ""
    return "\n".join(f"- {f}" for f in data["fatos"])


def forget_all() -> str:
    """Apaga toda a memória."""
    _save({"fatos": []})
    return "Pronto, esqueci tudo. Tábula rasa."
