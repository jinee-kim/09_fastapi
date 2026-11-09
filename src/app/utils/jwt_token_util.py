import os
from dotenv import load_dotenv
from datetime import timedelta,datetime,timezone
from jose import jwt,JWTError
from app.schemas.member_schema import MemberClaimDTO

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

#1. access_token을 생성하는 함수
def generate_access_token(member_claims:MemberClaimDTO)->str:
    #dto를 dict로 변환
    claims=member_claims.model_dump()

    #access토큰 지속시간은 1분에서 5분가량
    expire=datetime.now(timezone.utc)+timedelta(days=1)
    access_token=jwt.encode({
        **claims,
        "exp":expire
    },SECRET_KEY,algorithm=ALGORITHM)
    return access_token

#2. refresh_token을 생성하는 함수
def generate_refresh_token(member_claims:MemberClaimDTO)->str:
    #dto를 dict로 변환
    claims=member_claims.model_dump()

    #refresh토큰 지속시간은 한달가량
    expire=datetime.now(timezone.utc)+timedelta(days=30)
    refresh_token=jwt.encode({
        **claims,
        "exp":expire
    },SECRET_KEY,algorithm=ALGORITHM)
    return refresh_token

#3. token_parsing함수 (token을 가지고 유저정보를 들고오는거)
def parse_token(token:str)->MemberClaimDTO:
    payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    member_id=payload["id"]
    member_email=payload["member_email"]
    member_provider=payload["member_provider"]
    return MemberClaimDTO(
        id=member_id,
        member_email=member_email,
        member_provider=member_provider
    )

#4. refresh_token으로 access_token을 재발급하는 함수
def reissue_acces_token(refresh_token:str)->str:
    claims=parse_token(refresh_token)
    new_access_token=generate_access_token(claims)
    return new_access_token