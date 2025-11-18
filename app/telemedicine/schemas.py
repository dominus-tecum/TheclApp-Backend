from pydantic import BaseModel

class VideoTokenRequest(BaseModel):
    channel_name: str
    uid: int

class VideoTokenResponse(BaseModel):
    token: str
    channel_name: str
    uid: int
    expire_in: int