import os
from dotenv import load_dotenv
from fastapi import Response, Request,HTTPException,status

from app.schemas.member_schema import MemberClaimDTO
from app.schemas.auth_schema import JwtTokenDTO
from app.utils.jwt_token_util import parse_token

#로그인 정보를 요구하는 페이지들에 대해 토큰을 받고
#decode한다음 요소들을 백엔드에 보내는 공통로직 분리
#마이페이지,설정페이지,쿠폰창,회원전용 서비스 등 굉장히 많음(반대로 로그인,회원가입창처럼 회원에게 보여지면 안되는 서비스도 있고)

#1. request->access_token->decode->member_claims
def get_current_member(request:Request)->MemberClaimDTO:
    access_token=request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="get_current_member 로그인 세션이 만료되었습니다."
        )
    try:
        claims=parse_token(access_token)
        return claims
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="get_current_member>parse_token 유효하지 않은 토큰입니다."
        )
    
#2. request->access_token,refresh_token(JwtTokenDTO)
def get_tokens(request:Request)->JwtTokenDTO:
    access_token=request.cookies.get("access_token")
    refresh_token=request.cookies.get("refresh_token")
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="get_token 로그인 세션이 만료되었습니다."
        )
    
    return JwtTokenDTO(
        access_token=access_token,
        refresh_token=refresh_token
    )