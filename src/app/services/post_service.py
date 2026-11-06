from fastapi import Depends, HTTPException
from app.repositories.post_repository import PostRepository, get_post_repository
from app.repositories.member_repository import MemberRepository,get_member_repository
from app.schemas.post_schema import PostCreateDTO,PostDetailResponseDTO,PostListResponseDTO,PostResponseDTO
from app.schemas.common_schema import PageResponseDTO
from app.enums.post_enum import PostSortEnum,PostSearchEnum
import math

class PostService:
    def __init__(self,post_repo:PostRepository,member_repo:MemberRepository):
        self.post_repo=post_repo
        self.member_repo=member_repo


    #게시글 작성
    async def write_post(self,member_id:int,post:PostCreateDTO)->int:
        if not member_id:
            raise HTTPException(
                status_code=404,
                detail="유효하지 않는 유저id입니다."
            )
        is_member_exist=await self.member_repo.exists_member_by_id(member_id)
        if not is_member_exist:
            raise HTTPException(
                status_code=404,
                detail="존재하지 않는 유저id입니다."
            )

        new_post_id=await self.post_repo.create_post(member_id,post)
        return new_post_id

    #게시글id로 게시글 1개 찾기
    async def find_post_by_id(self,id:int)->PostDetailResponseDTO:
        found_post=await self.post_repo.find_post_by_id(id)
        if not found_post:
            raise HTTPException(
                status_code=404,
                detail="게시글 id가 존재하지 않습니다."
            )
        return PostDetailResponseDTO.model_validate(found_post)

    #유저id로 모든 게시글 찾기
    async def find_all_posts_by_memberid(self,member_id:int):
        found_posts=await self.post_repo.find_all_post_by_memberid(member_id)
        return found_posts

    #게시글 전체 조회(페이지+정렬)
    async def read_posts_by_paging(
            self,
            offset:int=1,
            limit:int=10,
            sort_by:PostSortEnum=PostSortEnum.LATEST.value,
    )->PageResponseDTO:
        posts=await self.post_repo.find_post_by_paging(offset,limit,sort_by)
        total_count=await self.post_repo.count_posts()
        total_pages=(total_count+limit-1)//limit if limit>0 else 1
        items=[PostListResponseDTO.model_validate(post)for post in posts]
        return PageResponseDTO(
            total_count=total_count,
            total_pages=total_pages,
            offset=offset,
            limit=limit,
            items=items,
        )

    ##게시글 검색(제목,내용,작성자,제목+내용)
    async def search_posts_by_paging(
            self,
            offset:int=1,
            limit:int=10,
            sort_by:PostSortEnum=PostSortEnum.LATEST.value,
            search_keyword:PostSearchEnum=PostSearchEnum.TITLE.value,
            search_detail:str|None=None
    )->PageResponseDTO:
        posts,total_count=await self.post_repo.search_filter(offset,limit,sort_by,search_keyword,search_detail)
        total_count=await self.post_repo.count_posts()
        total_pages=(total_count+limit-1)//limit if limit>0 else 1
        items=[PostListResponseDTO.model_validate(post)for post in posts]
        return PageResponseDTO(
            total_count=total_count,
            total_pages=total_pages,
            offset=offset,
            limit=limit,
            items=items,
        )

    #게시글 수정
    async def update_post_by_id(
            self,
            post_id:int,
            post_title:str,
            post_content:str
    ):
        updated=await self.post_repo.update_post(post_id,post_title,post_content)

        if updated is None:
            raise HTTPException(
                status_code=404,
                detail="게시글 id가 존재하지 않습니다."
            )
        return updated

    #게시글 삭제
    async def delete_post_by_id(
            self,
            post_id:int
    ):
        is_deleted=await self.post_repo.delete_post(post_id)
        if not is_deleted:
            raise HTTPException(
                status_code=404,
                detail="게시글 id가 존재하지 않습니다."
            )
        return is_deleted
        


def get_post_service(
    post_repo:PostRepository=Depends(get_post_repository),
    member_repo:MemberRepository=Depends(get_member_repository)
):
    return PostService(post_repo,member_repo)