from fastapi import Depends, HTTPException
from app.repositories.member_repository import MemberRepository, get_member_repository
from app.models.member_model import Member
from app.schemas.member_schema import(
    MemberCreateDTO,MemberClaimDTO
)
from app.utils.security_util import get_pw_hash,vertify_pw

#예외처리, 서비스가 드러나도록 이름을 선정해서 제작한다.
#트랜잭션 관리
class MemberService:
    def __init__(self,repo:MemberRepository):
        self.repo=repo

    #이메일 중복확인
    async def check_duplicate_member(self,member_email:str,member_provider:str):
        result= await self.repo.exists_member(member_email,member_provider)
        if result:
            raise HTTPException(
                status_code=409,
                detail="이미 가입된 이메일입니다."
            )

    #회원 가입
    async def join(self,member:MemberCreateDTO)->MemberClaimDTO:
        await self.check_duplicate_member(member.member_email,member.member_provider)
        #이메일,비밀번호,이름,나이,휴대폰 번호 를 입력받아서 db에 저장
        #비밀번호는 암호화
        encrypted_pw=get_pw_hash(member.member_pw)
        new_member=MemberCreateDTO(
            **member.model_dump(exclude={"member_pw"}),
            member_pw=encrypted_pw
        )
        return await self.repo.create_member(new_member)


#레포지토리 주입 팩토리 함수
def get_member_service(repo:MemberRepository=Depends(get_member_repository)):
    return MemberService(repo)