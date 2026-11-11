import os
from dotenv import load_dotenv
from fastapi import APIRouter, Query, Depends,Response
from app.services.default_service import get_default_service, DefaultService
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.member_schema import MemberClaimDTO
from app.enums.member_enum import MemberProvider
from app.schemas.auth_schema import JwtTokenDTO, LoginRequestDTO, SocialLoginRequestDTO
from app.services.auth_service import AuthService,get_auth_service
from app.dependencies.auth_dependency import get_current_member,get_tokens

#소셜 로그인용
import httpx #백엔드발 추가요청 처리
from fastapi.responses import RedirectResponse #페이지 전환
from urllib.parse import urlencode #요청주소를 조합하는 라이브러리

router = APIRouter()
load_dotenv()

#로그인
@router.post(
    "/login",
    response_model=ApiResponseDTO,
    summary="로컬 로그인",
    responses={
        200:{"description":"로그인 성공"},
        400:{
            "description": "비밀번호 불일치 등 잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "아이디 또는 비밀번호가 일치하지 않습니다."
                    }
                }
            }
        },
        404:{
            "description": "존재하지 않는 회원",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "회원이 존재하지 않습니다."
                    }
                }
            }
        }
    }
)
async def login(
    login_member:LoginRequestDTO,
    response:Response,
    auth_service:AuthService=Depends(get_auth_service)
):
    login_member.member_provider=MemberProvider.LOCAL.value
    tokens=await auth_service.login_local(login_member)
    access_token=tokens.access_token
    refresh_token=tokens.refresh_token

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*30
    )

    return ApiResponseDTO(
        success=True,
        message="로그인 성공!",
    )

GOOGLE_AUTH_URL=os.getenv("GOOGLE_AUTH_URL")
GOOGLE_TOKEN_URL=os.getenv("GOOGLE_TOKEN_URL")
GOOGLE_USERINFO_URL=os.getenv("GOOGLE_USERINFO_URL")

GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL=os.getenv("FRONTEND_URL")

#구글 로그인
@router.get(
    "/google",
    summary="구글 로그인"
)
async def login_google():
    params={
        "client_id":GOOGLE_CLIENT_ID,
        "redirect_uri":GOOGLE_REDIRECT_URI,
        "response_type":"code",
        "scope":"openid email profile",
        "access_type":"offline",
        "prompt":"consent"
    }
    url=f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)
#구글 로그인 콜백
@router.get(
    "/google/callback",
    summary="구글 로그인 콜백"
)
async def login_google_callback(
    code:str,
    response:RedirectResponse,
    auth_service:AuthService=Depends(get_auth_service)
):
    async with httpx.AsyncClient() as client:
        token_res=await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code":code,
                "client_id":GOOGLE_CLIENT_ID,
                "client_secret":GOOGLE_CLIENT_SECRET,
                "redirect_uri":GOOGLE_REDIRECT_URI,
                "grant_type":"authorization_code"
            }
        )
        token_data=token_res.json()
        access_token=token_data.get("access_token")

        async with httpx.AsyncClient() as client:
            user_res=await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization":f"Bearer {access_token}"}
            )
        user=user_res.json()
        user_params={
            "member_email":user.get("email"),
            "member_provider":MemberProvider.GOOGLE.value,
            "member_provider_id":user.get("sub")
        }
        return await _handle_social_login_or_join(user_params,auth_service)

KAKAO_CLIENT_ID=os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET=os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI=os.getenv("KAKAO_REDIRECT_URI")
KAKAO_AUTH_URL=os.getenv("KAKAO_AUTH_URL")
KAKAO_TOKEN_URL=os.getenv("KAKAO_TOKEN_URL")
KAKAO_USERINFO_URL=os.getenv("KAKAO_USERINFO_URL")

#카카오 로그인
@router.get(
    "/kakao",
    summary="카카오 로그인"
)
async def login_kakao():
    params={
        "client_id":KAKAO_CLIENT_ID,
        "redirect_uri":KAKAO_REDIRECT_URI,
        "response_type":"code",
    }
    url=f"{KAKAO_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)

@router.get(
    "/kakao/callback",
    summary="카카오 로그인 콜백"
)
async def login_kakao_callback(
    code:str,
    response:Response,
    auth_service:AuthService=Depends(get_auth_service)
):
    async with httpx.AsyncClient() as client:
        token_res=await client.post(
            KAKAO_TOKEN_URL,
            data={
                "code":code,
                "client_id":KAKAO_CLIENT_ID,
                "client_secret":KAKAO_CLIENT_SECRET,
                "redirect_uri":KAKAO_REDIRECT_URI,
                "grant_type":"authorization_code"
            }
        )
        token_data=token_res.json()
        access_token=token_data.get("access_token")
        async with httpx.AsyncClient() as client:
            user_res=await client.get(
                KAKAO_USERINFO_URL,
                headers={"Authorization":f"Bearer {access_token}"}
            )
        user=user_res.json()
        user_profile=user.get("kakao_account")
        user_params={
            "member_email":user_profile.get("email"),
            "member_provider":MemberProvider.KAKAO.value,
            "member_provider_id":str(user.get("id"))
        }
        return await _handle_social_login_or_join(user_params,auth_service)

NAVER_CLIENT_ID=os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET=os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI=os.getenv("NAVER_REDIRECT_URI")
NAVER_AUTH_URL=os.getenv("NAVER_AUTH_URL")
NAVER_TOKEN_URL=os.getenv("NAVER_TOKEN_URL")
NAVER_USERINFO_URL=os.getenv("NAVER_USERINFO_URL")

#네이버 로그인
@router.get(
    "/naver",
    summary="네이버 로그인"
)
async def login_naver():
    params={
        "client_id":NAVER_CLIENT_ID,
        "redirect_uri":NAVER_REDIRECT_URI,
        "response_type":"code",
    }
    url=f"{NAVER_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)
#네이버 로그인 콜백
@router.get(
    "/naver/callback",
    summary="네이버 로그인 콜백"
)
async def login_naver_callback(
    code:str,
    response:Response,
    auth_service:AuthService=Depends(get_auth_service)
):
    async with httpx.AsyncClient() as client:
        token_res=await client.post(
            NAVER_TOKEN_URL,
            data={
                "code":code,
                "client_id":NAVER_CLIENT_ID,
                "client_secret":NAVER_CLIENT_SECRET,
                "redirect_uri":NAVER_REDIRECT_URI,
                "grant_type":"authorization_code"
            }
        )
        token_data=token_res.json()
        access_token=token_data.get("access_token")
        async with httpx.AsyncClient() as client:
            user_res=await client.get(
                NAVER_USERINFO_URL,
                headers={"Authorization":f"Bearer {access_token}"}
            )
        user=user_res.json()
        user_profile=user.get("response")
        user_params={
            "member_email":user_profile.get("email"),
            "member_provider":MemberProvider.NAVER.value,
            "member_provider_id":str(user_profile.get("id"))
        }
        return await _handle_social_login_or_join(user_params,auth_service)

#로그아웃
@router.post(
    "/logout",
    summary="로그아웃",
    response_model=ApiResponseDTO
)
async def logout(
    response:Response,
    member_claims:MemberClaimDTO=Depends(get_current_member),
    tokens:JwtTokenDTO=Depends(get_tokens),
    auth_service:AuthService=Depends(get_auth_service)
):
    #1. 토큰을 decode후 멤버id,액세스토큰,리프레시토큰 순으로 서비스에 전달
    await auth_service.logout(member_claims.id,tokens)
    #2. 로그아웃 서비스 실행
    #3. 화면 쿠키 삭제
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
     #4. 화면으로 ApiResponseDTO전달
    return ApiResponseDTO(
        success=True,
        message="로그아웃 성공"
    )

@router.get(
        "/refresh",
        response_model=ApiResponseDTO,
        summary="토큰 재발급"
)
async def refresh(
    response:Response,
    tokens:JwtTokenDTO=Depends(get_tokens),
    auth_service:AuthService=Depends(get_auth_service)
):
    refresh_token=tokens.refresh_token
    try:
        access_token=await auth_service.refresh(refresh_token)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60*60*24
        )
        return ApiResponseDTO(
            success=True,
            message="Access Token 재발급 성공"
        )
    except Exception as e:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return ApiResponseDTO(
            success=False,
            message="Refresh Token 오류"
        )



async def _handle_social_login_or_join(user_params:dict,auth_service:AuthService):
    social_member=SocialLoginRequestDTO.model_validate(user_params)
    tokens=await auth_service.login_social_or_join(social_member)

    #비회원(최초 로그인)시 추가정보 입력창으로
    if not tokens:
        url=f"{FRONTEND_URL}/join-social-additional?{urlencode(user_params)}"
        return RedirectResponse(url)

    #정상 로그인
    access_token=tokens.access_token
    refresh_token=tokens.refresh_token

    response=RedirectResponse(url=FRONTEND_URL)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*30
    )

    return response