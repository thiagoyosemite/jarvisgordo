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

- "Quem ganhou o último jogo do Palmeiras?" → deve chamar `web_search` (busca real na web).
- "Que horas são?" → deve chamar `get_current_time`.
- "O que tenho na agenda hoje?" → deve chamar `get_fake_calendar`.
- "Rola um dado de 20." → deve chamar `roll_dice` com `sides=20`.

As linhas cinzas `[tool] ...` mostram a ferramenta sendo chamada de verdade.
Se o Gordão responde com a hora/agenda corretas **e** mantém o personagem
(reclamando antes), o cérebro + persona + tools estão funcionando. ✅

## Voz (TTS com voz clonada do Luiz)

O Gordão fala com a voz clonada. Há três provedores (escolha com `GORDAO_TTS`):
`local` (Chatterbox, roda no Mac, sem token — recomendado), `fish` (Fish Audio API)
ou `eleven` (ElevenLabs API).

### Opção recomendada: voz local com Chatterbox

Precisa de **Python 3.11** (o multilíngue do Chatterbox não roda em 3.9) e um áudio
de referência limpo do Luiz em `voz/ref_gordao.wav`.

```bash
# ambiente isolado com Python 3.11
brew install python@3.11
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install openai ddgs chatterbox-tts torchaudio

# rodar com voz local
export GORDAO_VOICE=1
export GORDAO_TTS=local
python agent.py
```

Na 1ª vez baixa os pesos do modelo (~2 GB) e a primeira fala demora; depois fica em
cache e acelera. Roda no Apple Silicon (MPS). Nenhuma API key necessária.

> Nota técnica: o `speak.py` desativa o watermarker `perth` (que instala quebrado e
> derruba o carregamento) com um stub — não afeta a qualidade da voz.

### Opção nuvem: Fish Audio ou ElevenLabs

Via ElevenLabs, a clonagem é feita uma vez no site (upload dos áudios); depois é só
configurar 3 variáveis. (Fish Audio é análogo, com `GORDAO_TTS=fish`.)

1. Crie conta em https://elevenlabs.io e gere uma **API key** (Profile → API Keys).
2. Em **Voices → Add Voice → Instant Voice Clone**, suba os áudios do Luiz
   (use trechos limpos, só a voz dele). Dê um nome (ex.: "Gordão") e crie.
3. Copie o **Voice ID** da voz criada.
4. Ative no terminal e rode:

```bash
export GORDAO_VOICE=1
export ELEVENLABS_API_KEY="sua_api_key"
export GORDAO_VOICE_ID="id_da_voz"
python3 agent.py
```

Agora cada resposta do Gordão é falada (usa `afplay`, nativo do macOS). Para
desligar a voz, feche o terminal ou rode `export GORDAO_VOICE=0`.

> Consentimento: a voz é de uma pessoa real (Luiz), clonada com autorização dele
> para uso entre amigos. Não publique a voz nem os áudios.

## Próximos passos

- Agenda real (Google Calendar), e-mail e arquivos como ferramentas.
- Entrada por voz (áudio nativo do Gemma 4) para conversa falada nos dois sentidos.
- Fallback de TTS local (XTTS/Coqui) para uso 100% offline.
