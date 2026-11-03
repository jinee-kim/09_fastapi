from fastapi import Depends, HTTPException
from app.repositories.member_repository import MemberRepository, get_member_repository
from app.models.member_model import Member
from app.schemas.member_schema import(
    MemberCreateDTO
)

#예외처리, 서비스가 드러나도록 이름을 선정해서 제작한다.
#트랜잭션 관리
class MemberService:
    def __init__(self,repo:MemberRepository):
        self.repo=repo

    async def check_duplicate_member(self,member_email:str,member_provider:str):
        result= await self.repo.exists_member(member_email,member_provider)
        if result:
            raise HTTPException(
                status_code=409,
                detail="이미 가입된 이메일입니다."
            )

#레포지토리 주입 팩토리 함수
def get_member_service(repo:MemberRepository=Depends(get_member_repository)):
    return MemberService(repo)