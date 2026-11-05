from fastapi import APIRouter, Query, Depends
from app.services.post_service import get_post_service, PostService
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.post_schema import PostCreateDTO,PostVO

from app.models.post_model import Post
from app.infrastructure.postgresql import get_postgresql_db, AsyncSession
import random

router = APIRouter()

@router.post(
    "",
    summary="게시글 작성",
    response_model=ApiResponseDTO
)
async def write_post(member_id:int,post:PostCreateDTO,post_service:PostService=Depends(get_post_service)):
    new_post_id=await post_service.write_post(member_id,post)
    return ApiResponseDTO(
        success=True,
        message="게시글 작성 성공",
        data={"newPostId":new_post_id}
    )

@router.get(
        "/user{member_id}",
        summary="유저id로 게시글 전체 검색",
        response_model=ApiResponseDTO[list[PostVO]]
)
async def find_all_posts_by_memberid(member_id:int, post_service:PostService=Depends(get_post_service)):
    found_posts=await post_service.find_all_posts_by_memberid(member_id)
    return ApiResponseDTO(
        success=True,
        message="해당 유저의 전체 게시글 검색 성공",
        data=found_posts
    )

@router.get(
    "/{id}",
    summary="게시글 id로 게시글 검색",
    response_model=ApiResponseDTO[PostVO]    
)
async def find_post_by_id(id:int, post_service:PostService=Depends(get_post_service)):
    found_post=await post_service.find_post_by_id(id)
    return ApiResponseDTO(
        success=True,
        message="게시글 검색 성공",
        data=PostVO.model_validate(found_post)
    )













#더미 데이터 추가
@router.post("/dummies", summary="게시판 더미데이터 추가")
async def get_dummies(count:int=100,db:AsyncSession=Depends(get_postgresql_db)):
    target_member_ids=[1,3,4]
    for i in range(1,count+1):
        random_member_id=random.choice(target_member_ids)
        random_view=random.randint(0,10000)

        new_post=Post(
            post_title=f"랜덤 테스트 제목{i}",
            post_content=f"랜덤 테스트 내용{i}",
            post_read_count=random_view,
            member_id=random_member_id,
        )
        db.add(new_post)
    await db.commit()
    return{"message":"더미데이터 생성 성공"}