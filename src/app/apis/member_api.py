from fastapi import APIRouter,Query,Depends
from app.services.member_service import get_member_service,MemberService
from app.enums.member_enum import MemberProvider
from app.schemas.member_schema import MemberCreateDTO,MemberClaimDTO

router=APIRouter()

@router.post("/check-member")
async def check_member(member_email:str,member_provider:str,member_service=Depends(get_member_service)):
    await member_service.check_duplicate_member(member_email,member_provider)
    return {
        "message":"회원 가입이 가능한 이메일!"
    }

@router.post("/join")
async def join(member:MemberCreateDTO,member_service=Depends(get_member_service)):
    member.member_provider=MemberProvider.LOCAL.value
    member_claim:MemberClaimDTO=await member_service.join(member)
    return member_claim
