from fastapi import APIRouter, Query, Depends
from app.services.post_service import get_post_service, PostService
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.post_schema import PostCreateDTO,PostVO,PostDetailResponseDTO,PostResponseDTO
from app.enums.post_enum import PostSortEnum,PostSearchEnum

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
#게시글 검색 전체 조회(페이지네이션+정렬
@router.get(
        "/get_keyword",
        summary="게시판 전체 조회(검색)",
        response_model=ApiResponseDTO
)
async def get_posts(
    offset:int=Query(0,ge=0),
    limit:int=Query(10,ge=1,le=100),
    sort_by:PostSortEnum=Query(PostSortEnum.LATEST.value,description="정렬기준(LATEST,OLDEST,VIEWS)"),
    search_keyword:PostSearchEnum=Query(PostSearchEnum.TITLE,description="검색 기준(TITLE,CONTENT,WRITER,TITLE_CONTENT)"),
    search_detail:str|None=Query(None,description="검색어"),
    post_service:PostService=Depends(get_post_service),
):
    paged_posts=await post_service.search_posts_by_paging(
        offset,
        limit,
        sort_by,
        search_keyword,
        search_detail
    )
    return ApiResponseDTO(
        success=True,
        message="전체 게시글 조회 성공",
        data=paged_posts
    )
    pass
    #paged_posts=await post_service.read_posts_by_paging(offset,limit,sort_by)
    #return ApiResponseDTO(
    #    success=True,
    #    message="전체 게시글 조회 성공",
    #   data=paged_posts,
    #)

@router.patch(
        "/update",
        summary="게시글 id를 통해 게시글 특정 후 제목과 내용 수정",
        response_model=ApiResponseDTO[PostResponseDTO]
)
async def update_post_by_id(
    post_id:int,
    post_title:str,
    post_content:str,
    post_service:PostService=Depends(get_post_service)
):
    update_post=await post_service.update_post_by_id(post_id,post_title,post_content)
    update_post=PostResponseDTO.model_validate(update_post)
    return ApiResponseDTO(
        success=True,
        message="게시글 수정 성공",
        data=update_post
    )

@router.delete(
        "/delete{post_id}",
        summary="게시글 id로 게시글 삭제",
        response_model=ApiResponseDTO
)
async def delete_post_by_id(
    post_id:int,
    post_service:PostService=Depends(get_post_service)
):
    delete_post=await post_service.delete_post_by_id(post_id)
    return ApiResponseDTO(
        success=True,
        message="게시글 삭제 성공",
        data=delete_post
    )

@router.get(
    "/{post_id}",
    summary="게시글 id로 게시글 검색",
    response_model=ApiResponseDTO[PostDetailResponseDTO]    
)
async def find_post_by_id(post_id:int, post_service:PostService=Depends(get_post_service)):
    found_post=await post_service.find_post_by_id(post_id)
    return ApiResponseDTO(
        success=True,
        message="게시글 검색 성공",
        data=found_post
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

#게시글 전체 조회(페이지네이션+정렬
@router.get(
        "",
        summary="게시판 전체 조회",
        response_model=ApiResponseDTO
)
async def get_posts(
    offset:int=Query(0,ge=0),
    limit:int=Query(10,ge=1,le=100),
    sort_by:PostSortEnum=Query(PostSortEnum.LATEST.value,description="정렬기준(LATEST,OLDEST,VIEWS)"),
    post_service:PostService=Depends(get_post_service)
):
    paged_posts=await post_service.read_posts_by_paging(offset,limit,sort_by)
    return ApiResponseDTO(
        success=True,
        message="전체 게시글 조회 성공",
        data=paged_posts,
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