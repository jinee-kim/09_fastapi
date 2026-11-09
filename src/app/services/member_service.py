from fastapi import Depends, HTTPException
from app.repositories.member_repository import MemberRepository, get_member_repository
from app.models.member_model import Member
from app.schemas.member_schema import(
    MemberCreateDTO,MemberClaimDTO,SocialMemberClaimDTO,MemberResponseDTO,MemberUpdateDTO
)
from app.enums.member_enum import MemberProvider
from app.schemas.common_schema import PageResponseDTO
from app.utils.security_util import get_pw_hash,vertify_pw
import math

#예외처리, 서비스가 드러나도록 이름을 선정해서 제작한다.
#트랜잭션 관리
class MemberService:
    def __init__(self,repo:MemberRepository):
        self.repo=repo

    #이메일 중복확인
    async def check_duplicate_member(self,member_email:str,member_provider:str):
        result= await self.repo.exists_member_by_email(member_email,member_provider)
        if result:
            raise HTTPException(
                status_code=409,
                detail="이미 가입된 이메일입니다."
            )

    #이메일로 유저 검증
    async def check_member_by_email(self,member_email:str,member_provider:str):
        result= await self.repo.exists_member_by_email(member_email,member_provider)
        return result

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

    #id로 회원정보 조회
    async def get_member_by_id(self,id:int):
        found_member=await self.repo.find_member_by_id(id)
        if not found_member:
            raise HTTPException(
                status_code=404,
                detail="회원 정보가 존재하지 않습니다."
            )
        return found_member
        #return MemberResponse.validate(found_member)

    async def get_member_by_email(self,member_email:str,member_provider:MemberProvider)->Member:
        found_member=await self.repo.find_member_by_email(member_email,member_provider)

        if not found_member:
            raise HTTPException(
                status_code=404,
                detail="회원 정보가 존재하지 않습니다."
            )
        return found_member
    
    #전체 멤버의 이메일과 프로바이더 조회
    async def get_email_and_provider(self)->list[SocialMemberClaimDTO]:
        found_data=await self.repo.get_email_and_provider()
        if not found_data:
            raise HTTPException(
                status_code=404,
                detail="검색 가능한 회원이 존재하지 않습니다."
            )
        return found_data

    #전체 멤버의 비번 제외한 전체 정보 조회
    async def get_all_data(self)->list[MemberResponseDTO]:
        found_data=await self.repo.get_all_data()
        if not found_data:
            raise HTTPException(
                status_code=404,
                detail="검색 가능한 회원이 존재하지 않습니다."
            )
        return found_data

    async def get_all_data_paging(self,offset:int,limit:int)->PageResponseDTO[MemberResponseDTO]:
        current_page=offset
        offset=(offset-1)*limit
        total_count=await self.repo.count_members()
        members=await self.repo.get_data_by_paging(offset,limit)
        total_pages=math.ceil(total_count/limit)
        return PageResponseDTO(
            total_count=total_count,
            total_pages=total_pages,
            offset=current_page,
            limit=limit,
            items=members
        )

    async def update_member(self,id,member:MemberUpdateDTO)->MemberResponseDTO:
        is_member_exist=await self.repo.exists_member_by_id(id)
        if not is_member_exist:
            raise HTTPException(
                status_code=404,
                detail="유효하지 않은 회원번호입니다."
            )
        update_data=member.model_dump(exclude_unset=True)

        if"member_pw"in update_data and update_data["member_pw"]:
            update_data["member_pw"]=get_pw_hash(update_data["member_pw"])

        updated_member=await self.repo.update_member(id,MemberUpdateDTO.model_validate(update_data))
        return MemberResponseDTO.model_validate(updated_member)

    async def withdraw(self,id:int)->bool:
        is_deleted=await self.repo.delete_member(id)
        if not is_deleted:
            raise HTTPException(
                status_code=404,
                detail="유효하지 않는 회원번호입니다."
            )
        return is_deleted




#레포지토리 주입 팩토리 함수
def get_member_service(repo:MemberRepository=Depends(get_member_repository)):
    return MemberService(repo)