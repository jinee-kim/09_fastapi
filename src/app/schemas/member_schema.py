from pydantic import BaseModel
from datetime import datetime
from app.enums.member_enum import MemberProvider

class MemberVO(BaseModel):
    id:int
    member_email:str
    member_pw:str|None=None
    member_name:str|None=None
    member_age:int|None=None
    member_profile:str|None="/members/default.jpg"
    member_provider_id:str|None=None
    member_provider:MemberProvider
    member_created_at:datetime|None=None

class MemberCreateDTO(BaseModel):
    member_email:str
    member_pw:str|None=None
    member_name:str|None=None
    member_age:int|None=None
    member_profile:str|None="/members/default.jpg"
    member_provider: MemberProvider|None

    #ORM->Pydantic DTO
    class Config:
        from_attributes=True

class MemberClaimDTO(BaseModel):
    id:int
    member_email:str
    member_provider:str
    class Config:
        from_attributes=True