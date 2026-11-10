from fastapi import APIRouter,Query,Depends
from app.services.member_service import get_member_service,MemberService
from app.enums.member_enum import MemberProvider
from app.schemas.member_schema import MemberResponseDTO,MemberCreateDTO,MemberClaimDTO,SocialMemberClaimDTO,MemberUpdateDTO
from app.schemas.common_schema import ApiResponseDTO

router=APIRouter()

@router.post(
    "/check-member",
    summary="로컬 회원 가입",
    response_model=ApiResponseDTO
)
async def check_member(member_email:str,member_provider:str,member_service:MemberService=Depends(get_member_service)):
    await member_service.check_duplicate_member(member_email,member_provider)
    return ApiResponseDTO(
        success=True,
        message="중복되지 않은 사용자"
    )

@router.post(
        "/join",
        response_model=ApiResponseDTO
    )
async def join(
    member:MemberCreateDTO,
    member_service:MemberService=Depends(get_member_service)
):
    if not member.member_provider:
        member.member_provider=MemberProvider.LOCAL.value
    member_claim:MemberClaimDTO=await member_service.join(member)

    return ApiResponseDTO(
        success=True,
        message="회원가입 성공",
        data=member_claim
    )

@router.get(
    "/get-email",
    response_model=ApiResponseDTO[list[SocialMemberClaimDTO]]
)
async def get_email_and_provider(member_service:MemberService=Depends(get_member_service)):
    found_data=await member_service.get_all_data()
    return ApiResponseDTO(
        success=True,
        message="전체 유저 이메일 정보 취득 성공",
        data=found_data
    )

@router.get(
    "/get-all",
    response_model=ApiResponseDTO[list[MemberResponseDTO]]
)
async def get_all_data(member_service:MemberService=Depends(get_member_service)):
    found_data=await member_service.get_all_data()
    return ApiResponseDTO(
        success=True,
        message="전체 유저 전체 정보 취득 성공",
        data=found_data
    )

@router.get(
    "",
    summary="페이징된만큼 유저 정보 조회",
    response_model=ApiResponseDTO
)
async def get_all_data_page(
    offset:int=Query(1,ge=1),
    limit:int=Query(10,ge=1,le=100),
    member_service:MemberService=Depends(get_member_service)
):
    paged_result=await member_service.get_all_data_paging(offset,limit)
    return ApiResponseDTO(
        success=True,
        message="유저 정보 취득 성공",
        data=paged_result
    )

@router.delete(
        "/delete",
        summary="회원 정보 삭제",
        response_model=ApiResponseDTO
)
async def withdraw(
    id:int,
    member_service=Depends(get_member_service)
):
    is_deleted=await member_service.withdraw(id)
    return ApiResponseDTO(
        success=True,
        message="회원 탈퇴 성공",
        data=is_deleted,        
    )

@router.put(
    "/{id}",
    summary="회원 정보 수정",
    response_model=ApiResponseDTO
)
async def update_member(
    id:int,
    member:MemberUpdateDTO,
    member_service=Depends(get_member_service)
):
    updated_member=await member_service.update_member(id,member)
    return ApiResponseDTO(
        success=True,
        message="회원 정보 업데이트 성공",
        data=updated_member,
    )


@router.get("/{id}",
    response_model=ApiResponseDTO[MemberResponseDTO] #비밀번호가 프론트에 노출되면 절대 안되니 MemberResponse로 필터링을 거친다.
)
async def get_members_by_id(id:int,member_service:MemberService=Depends(get_member_service)):
    found_member=await member_service.get_member_by_id(id)
    return ApiResponseDTO(
        success=True,
        message="유저 정보 취득 성공",
        data=MemberResponseDTO.model_validate(found_member),
    )

