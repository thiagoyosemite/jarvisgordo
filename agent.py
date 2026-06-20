"""
Jarvis Gordo — esqueleto do agente (Fase 0).

Loop de chat em texto com o Gemma 4 12B-it local:
  - carrega a persona do Gordão como system prompt;
  - manda a conversa pro modelo via API OpenAI-compatível (Ollama/llama.cpp);
  - se o modelo pedir uma tool, executa e devolve o resultado;
  - repete até o modelo dar a resposta final em texto.

Rodar:  python agent.py
Sair:   /sair  (ou Ctrl+C)
"""

import json
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Falta a lib 'openai'. Rode: pip install -r requirements.txt")
    sys.exit(1)

import config
from tools import TOOLS_SCHEMA, TOOLS_REGISTRY

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)

MAX_TOOL_HOPS = 5  # trava de segurança contra loop infinito de tool calls


def executar_tool(name: str, args: dict) -> str:
    """Despacha uma chamada de ferramenta para a função Python correspondente."""
    fn = TOOLS_REGISTRY.get(name)
    if fn is None:
        return f"[erro] ferramenta desconhecida: {name}"
    try:
        return str(fn(**args))
    except Exception as e:  # noqa: BLE001
        return f"[erro ao executar {name}] {e}"


def responder(messages: list) -> str:
    """Uma rodada completa: pode envolver várias chamadas de tool até a resposta final."""
    for _ in range(MAX_TOOL_HOPS):
        resp = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
        )
        msg = resp.choices[0].message

        # Sem tool call -> resposta final em texto.
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content or ""})
            return msg.content or ""

        # Registra a intenção do assistente de chamar ferramentas.
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            }
        )

        # Executa cada ferramenta pedida e injeta o resultado.
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            resultado = executar_tool(name, args)
            print(f"   \033[90m[tool] {name}({args}) -> {resultado}\033[0m")
            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "name": name, "content": resultado}
            )

    return "(Gordão se enrolou com as ferramentas e desistiu. Tenta de novo, bicho.)"


def main() -> None:
    system_prompt = config.load_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]

    print("\033[1mJarvis Gordo — Fase 0\033[0m  (cérebro: %s @ %s)" % (config.MODEL, config.BASE_URL))
    print("Digite e dê enter. Pra sair: /sair\n")

    while True:
        try:
            user = input("\033[94mVocê:\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGordão: Falou.")
            break

        if not user:
            continue
        if user.lower() in ("/sair", "/quit", "/exit"):
            print("Gordão: Finalmente. Sai fora bicho. 👋")
            break

        messages.append({"role": "user", "content": user})
        try:
            saida = responder(messages)
        except Exception as e:  # noqa: BLE001
            print(f"\033[91m[erro de conexão]\033[0m {e}")
            print("Confirma que o servidor do modelo tá rodando (ex.: `ollama serve`).")
            continue

        print(f"\033[92mGordão:\033[0m {saida}\n")


if __name__ == "__main__":
    main()
