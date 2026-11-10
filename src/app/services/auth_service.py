import os
from dotenv import load_dotenv
from fastapi import Depends,HTTPException,status
from app.repositories.redis_repository import RedisRepository, get_redis_repository
from app.utils.jwt_token_util import (
    parse_token,generate_access_token,generate_refresh_token,reissue_acces_token

)
from app.utils.jwt_token_util import(
    generate_access_token,generate_refresh_token,parse_token,reissue_acces_token
)
from app.utils.security_util import vertify_pw
from app.services.member_service import get_member_service,MemberService
from app.schemas.auth_schema import JwtTokenDTO,LoginRequestDTO,SocialLoginRequestDTO
from app.schemas.member_schema import MemberClaimDTO

load_dotenv()
TOKEN_BLACKLIST_PREFIX=os.getenv("TOKEN_BLACKLIST_PREFIX")
REFRESH_TOKEN_PREFIX=os.getenv("REFRESH_TOKEN_PREFIX")


# 예외처리
# 트랜잭션 관리
class AuthService:

    def __init__(
            self, 
            redis_repo: RedisRepository,
            member_service:MemberService
        ):
        self.redis_repo = redis_repo
        self.member_service=member_service

    #redis에 refresh_token 저장
    #key: 콜론 체이닝 방식
    async def save_refresh_token(self,member_id:int,refresh_token:str)->None:
        try:
            key=f"{REFRESH_TOKEN_PREFIX}{member_id}"
            ex=60*60*24*30 #한달
            await self.redis_repo.set(key,refresh_token,ex=ex)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="오류지점: save_refresh_token"
            )
    #redis에 등록된 refresh_token이 유효한지 검사
    async def validate_refresh_token(self,member_id:int,refresh_token:str)->bool:
        key=f"{REFRESH_TOKEN_PREFIX}{member_id}"
        saved_token=await self.redis_repo.get(key)
        return refresh_token==saved_token

    #redis에 등록된 refresh_token삭제
    async def delete_refresh_token(self,member_id:int):
        key=f"{REFRESH_TOKEN_PREFIX}{member_id}"
        await self.redis.repo.delete(key)

    #redis에 등록된 access_token블랙리스트에 등록(로그아웃)
    async def save_blacklisted_token(self,access_token:str)->None:
        try:
            key=f"{TOKEN_BLACKLIST_PREFIX}{access_token}"
            ex=60*60*24 #하루

            await self.redis_repo.set(key,"blacklisted",ex=ex)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="오류지점: save_blacklisted_token"
            )
        
    #redis에 블랙리스트에 등록되어있는지 확인
    async def is_blacklisted_token(self,access_token:str)->bool:
        key=f"{TOKEN_BLACKLIST_PREFIX}{access_token}"
        #여기서는 True면 블랙리스트 등록되어있으니 사용불가, 아니면 사용가능
        return await self.redis_repo.exists(key)

    #로그인(로컬)
    async def login_local(self,login_request_dto:LoginRequestDTO)->JwtTokenDTO:
        #1. 회원 조회
        member_in_db=await self.member_service.get_member_by_email(
            login_request_dto.member_email,
            login_request_dto.member_provider
        )
        #2. 비밀번호 검증
        if not vertify_pw(
            login_request_dto.member_pw,
            member_in_db.member_pw
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="오류지점: login_local->verify_pw"
            )
        #3. JWT토큰 만들기
        member_id=member_in_db.id
        claims=MemberClaimDTO(
            id=member_id,
            member_email=member_in_db.member_email,
            member_provider=member_in_db.member_provider
        )
        access_token=generate_access_token(claims)
        refresh_token=generate_refresh_token(claims)
        #4. refresh를 redis에 저장
        await self.save_refresh_token(member_id,refresh_token)
        #5. 토큰 반환
        return JwtTokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )

    #로그인(소셜)
    async def login_social(self,login_request_dto:SocialLoginRequestDTO)->JwtTokenDTO|None:
        member_in_db=await self.member_service.get_member_by_email(
            login_request_dto.member_email,
            login_request_dto.member_provider
        )
        if not member_in_db:
            return None
        
        member_id=member_in_db.id
        claims=MemberClaimDTO(
            id=member_id,
            member_email=member_in_db.member_email,
            member_provider=member_in_db.member_provider
        )
        access_token=generate_access_token(claims)
        refresh_token=generate_refresh_token(claims)

        await self.save_refresh_token(member_id,refresh_token)

        return JwtTokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    #로그아웃
    async def logout(self,member_id:int,tokens:JwtTokenDTO)->None:
        access_token=tokens.access_token
        await self.save_blacklisted_token(access_token)
        await self.redis_repo.delete(access_token)
        #1. 토큰을 받아 decode해 필수정보를 가져옴(이건 컨트롤러가 담당)
        #2. 블랙리스트에 accessToken등록


    #refresh토큰으로 access토큰 재발급






# 레포지토리 주입 팩토리 함수
def get_auth_service(
    redis_repo: RedisRepository=Depends(get_redis_repository),
    member_service:MemberService=Depends(get_member_service)
):
    return AuthService(redis_repo,member_service)