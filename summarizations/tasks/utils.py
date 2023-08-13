import secrets
import string
from pathlib import Path
from summarizations.models import VoiceMessage


def secure_random_string(length: int = 10) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def get_voice_massage_key(vm: VoiceMessage) -> str:
    p = Path(vm.voice_path)
    ext = p.suffix
    secure_string = secure_random_string()
    return f"VM-{vm.pk}-{secure_string}{ext}"
