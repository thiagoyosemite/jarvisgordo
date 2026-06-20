# Jarvis Gordo — Fase 0 (esqueleto do agente)

Chat de texto com o **Gordão** rodando local no **Gemma 4 12B-it**, já com
**function calling** validado por ferramentas de teste. É a fundação do projeto:
quando o tom e as tools estiverem ok aqui, a gente avança pra voz e automação.

## O que tem aqui

| Arquivo | Função |
|---|---|
| `gordao_system_prompt.txt` | A alma do Gordão (persona) que vira o system prompt |
| `config.py` | Endpoint do modelo, nome, amostragem |
| `tools.py` | Ferramentas de teste (hora, agenda fake, dado) + schemas |
| `agent.py` | Loop do agente: conversa + execução de tools |
| `requirements.txt` | Dependência (lib `openai`) |

## Pré-requisitos

1. **LM Studio** instalado (https://lmstudio.ai) — ou Ollama, se preferir.
2. **Python 3.9+**.

## Passo a passo (LM Studio — recomendado)

1. No LM Studio, busque e baixe **Gemma 4 12B-it** (quantização Q4_K_M).
2. Aba **Developer / Local Server** → carregue o modelo → **Start Server**
   (sobe em `http://localhost:1234/v1`).
3. Instale a dependência e rode o Gordão:

```bash
pip install -r requirements.txt
python agent.py
```

O `config.py` já aponta pro LM Studio por padrão. Se o id do modelo for diferente
do exibido no painel, ajuste:

```bash
export GORDAO_MODEL="google/gemma-4-12b-it"   # use o id que o LM Studio mostra
python agent.py
```

### Alternativa: Ollama

```bash
ollama pull gemma-4-12b-it
ollama serve
export GORDAO_BASE_URL="http://localhost:11434/v1"
export GORDAO_MODEL="gemma-4-12b-it"
python agent.py
```

### Alternativa: llama.cpp

```bash
export GORDAO_BASE_URL="http://localhost:8080/v1"
export GORDAO_MODEL="gemma-4-12B-it"
```

## Como testar o function calling

Dentro do chat, experimente:

- "Que horas são?" → deve chamar `get_current_time`.
- "O que tenho na agenda hoje?" → deve chamar `get_fake_calendar`.
- "Rola um dado de 20." → deve chamar `roll_dice` com `sides=20`.

As linhas cinzas `[tool] ...` mostram a ferramenta sendo chamada de verdade.
Se o Gordão responde com a hora/agenda corretas **e** mantém o personagem
(reclamando antes), o cérebro + persona + tools estão funcionando. ✅

## Próximos passos (fora desta fase)

- Trocar as tools de teste por agenda real, e-mail, busca web e arquivos.
- Adicionar voz: entrada por áudio (nativo do Gemma) e saída TTS com a voz clonada do Luiz.
- Memória de conversa entre sessões.
