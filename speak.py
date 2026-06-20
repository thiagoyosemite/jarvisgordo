"""
Voz do Gordão — TTS com a voz clonada do Luiz.

Suporta dois provedores (escolha com GORDAO_TTS):
  - "fish"   → Fish Audio (usa o modelo de voz já criado lá)
  - "eleven" → ElevenLabs

Toca o áudio no macOS com `afplay`.

CONFIG — Fish Audio (recomendado, você já tem a voz pronta):
  export GORDAO_VOICE=1
  export GORDAO_TTS=fish
  export FISH_API_KEY="sua_api_key_fish"
  export FISH_MODEL_ID="id_do_modelo_da_voz_do_luiz"   # "reference_id" no Fish

CONFIG — ElevenLabs (alternativa):
  export GORDAO_VOICE=1
  export GORDAO_TTS=eleven
  export ELEVENLABS_API_KEY="sua_api_key"
  export GORDAO_VOICE_ID="id_da_voz"

Se nada estiver configurado, o agente roda normal só em texto.
"""

import json
import os
import subprocess
import tempfile
import urllib.request

ENABLED = os.environ.get("GORDAO_VOICE", "0") == "1"

# Provedor: explícito via GORDAO_TTS, ou auto-detecta pelo que estiver configurado.
#   "local"  → Chatterbox (roda no Mac, sem token)
#   "fish"   → Fish Audio (API)
#   "eleven" → ElevenLabs (API)
_PROVIDER = os.environ.get("GORDAO_TTS", "").lower().strip()

# Local (Chatterbox)
REF_AUDIO = os.environ.get(
    "GORDAO_REF_AUDIO",
    os.path.join(os.path.dirname(__file__), "voz", "ref_gordao.wav"),
)
LOCAL_LANG = os.environ.get("GORDAO_LANG", "pt")

# Fish Audio
FISH_API_KEY = os.environ.get("FISH_API_KEY", "")
FISH_MODEL_ID = os.environ.get("FISH_MODEL_ID", "")

# ElevenLabs
ELEVEN_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVEN_VOICE_ID = os.environ.get("GORDAO_VOICE_ID", "")
ELEVEN_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")

# Modelo Chatterbox carregado uma vez só (é pesado).
_local_model = None


def _provider() -> str:
    if _PROVIDER in ("local", "fish", "eleven"):
        return _PROVIDER
    if os.path.exists(REF_AUDIO):
        return "local"
    if FISH_MODEL_ID and FISH_API_KEY:
        return "fish"
    if ELEVEN_VOICE_ID and ELEVEN_API_KEY:
        return "eleven"
    return ""


def is_enabled() -> bool:
    if not ENABLED:
        return False
    p = _provider()
    if p == "local":
        return os.path.exists(REF_AUDIO)
    if p == "fish":
        return bool(FISH_API_KEY and FISH_MODEL_ID)
    if p == "eleven":
        return bool(ELEVEN_API_KEY and ELEVEN_VOICE_ID)
    return False


def status() -> str:
    if not ENABLED:
        return "voz: desligada (GORDAO_VOICE != 1)"
    p = _provider()
    if not p:
        return "voz: ligada, mas falta configurar um provedor (local/Fish/ElevenLabs)"
    if p == "local" and not os.path.exists(REF_AUDIO):
        return f"voz: ligada (local), mas falta o áudio de referência em {REF_AUDIO}"
    if not is_enabled():
        return f"voz: ligada ({p}), mas faltam credenciais"
    return f"voz: ligada (provedor: {p})"


def _pick_device() -> str:
    try:
        import torch

        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
    except Exception:  # noqa: BLE001
        pass
    return "cpu"


def _speak_local(text: str) -> None:
    """TTS local com Chatterbox (clona a voz a partir de REF_AUDIO). Sem token."""
    global _local_model
    try:
        import torchaudio as ta
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    except ImportError:
        print("   \033[90m[voz local indisponível: rode `pip install chatterbox-tts torchaudio`]\033[0m")
        return

    if _local_model is None:
        # O watermarker (perth) às vezes instala quebrado e fica None, derrubando o
        # carregamento. Ele é opcional (marca d'água inaudível); substituímos por um
        # stub que não altera o áudio.
        try:
            import perth

            if getattr(perth, "PerthImplicitWatermarker", None) is None:
                class _NoOpWatermarker:
                    def apply_watermark(self, wav, sample_rate=None, **kw):
                        return wav

                perth.PerthImplicitWatermarker = _NoOpWatermarker
        except Exception:  # noqa: BLE001
            pass

        device = _pick_device()
        print(f"   \033[90m[carregando Chatterbox em {device}... (só na 1ª vez)]\033[0m")
        _local_model = ChatterboxMultilingualTTS.from_pretrained(device=device)

    wav = _local_model.generate(text, language_id=LOCAL_LANG, audio_prompt_path=REF_AUDIO)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    import torchaudio as ta
    ta.save(path, wav, _local_model.sr)
    _play(path)
    os.remove(path)


def _play(path: str) -> None:
    subprocess.run(["afplay", path], check=False)


def _speak_fish(text: str) -> None:
    """TTS via Fish Audio. Usa o SDK se disponível; senão, a API msgpack."""
    audio = None
    # Caminho 1: SDK oficial (mais simples).
    try:
        from fish_audio_sdk import Session, TTSRequest

        session = Session(FISH_API_KEY)
        buf = bytearray()
        for chunk in session.tts(TTSRequest(reference_id=FISH_MODEL_ID, text=text)):
            buf.extend(chunk)
        audio = bytes(buf)
    except ImportError:
        # Caminho 2: API crua via msgpack (sem o SDK).
        try:
            import msgpack
        except ImportError:
            print("   \033[90m[voz Fish indisponível: rode `pip install fish-audio-sdk`]\033[0m")
            return
        body = msgpack.packb({"text": text, "reference_id": FISH_MODEL_ID, "format": "mp3"})
        req = urllib.request.Request(
            "https://api.fish.audio/v1/tts",
            data=body,
            headers={
                "Authorization": f"Bearer {FISH_API_KEY}",
                "Content-Type": "application/msgpack",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            audio = resp.read()

    if audio:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio)
            path = f.name
        _play(path)
        os.remove(path)


def _speak_eleven(text: str) -> None:
    """TTS via ElevenLabs."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    body = json.dumps(
        {
            "text": text,
            "model_id": ELEVEN_MODEL,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.85, "style": 0.3},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        audio = resp.read()
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio)
        path = f.name
    _play(path)
    os.remove(path)


def speak(text: str) -> None:
    """Sintetiza o texto com a voz clonada e toca. Silencioso se desativado."""
    if not is_enabled():
        return
    text = (text or "").strip()
    if not text:
        return
    try:
        p = _provider()
        if p == "local":
            _speak_local(text)
        elif p == "fish":
            _speak_fish(text)
        else:
            _speak_eleven(text)
    except Exception as e:  # noqa: BLE001
        print(f"   \033[90m[voz indisponível: {e}]\033[0m")
