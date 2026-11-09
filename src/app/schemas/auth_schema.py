from pydantic import BaseModel
from app.enums.member_enum import MemberProvider

class LoginRequestDTO(BaseModel):
    member_email:str
    member_pw:str|None=None
    member_provider:MemberProvider|None=None
    class Config:
        from_attributes=True

class SocialLoginRequestDTO(BaseModel):
    member_email:str
    member_provider_id:str|None=None
    member_provider:MemberProvider|None=None
    class Config:
        from_attributes=True

class JwtTokenDTO(BaseModel):
    access_token:str|None=None
    refresh_token:str|None=None
    class Config:
        from_attributes=True