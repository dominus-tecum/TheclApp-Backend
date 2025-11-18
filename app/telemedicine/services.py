import time
from config import settings
from agora_token_builder import RtcTokenBuilder

def generate_agora_token(channel_name: str, uid: int, expire_seconds: int = 3600) -> str:
    """
    Generate an Agora RTC token for a video session.
    """
    current_ts = int(time.time())
    privilege_expired_ts = current_ts + expire_seconds

    token = RtcTokenBuilder.buildTokenWithUid(
        settings.AGORA_APP_ID,
        settings.AGORA_APP_CERTIFICATE,
        channel_name,
        uid,
        RtcTokenBuilder.Role_PUBLISHER,
        privilege_expired_ts
    )
    return token