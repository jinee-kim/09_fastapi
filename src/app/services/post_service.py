from fastapi import Depends, HTTPException
from app.repositories.post_repository import PostRepository, get_post_repository
from app.repositories.member_repository import MemberRepository,get_member_repository
from app.models.post_model import Post
from app.schemas.post_schema import PostCreateDTO
from app.schemas.common_schema import PageResponseDTO
from app.utils.security_util import get_pw_hash,vertify_pw
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
    async def find_post_by_id(self,id:int):
        found_post=await self.post_repo.find_post_by_id(id)
        if not found_post:
            raise HTTPException(
                status_code=404,
                detail="게시글 id가 존재하지 않습니다."
            )
        return found_post

    #유저id로 모든 게시글 찾기
    async def find_all_posts_by_memberid(self,member_id:int):
        found_posts=await self.post_repo.find_all_post_by_memberid(member_id)
        return found_posts
    


def get_post_service(
    post_repo:PostRepository=Depends(get_post_repository),
    member_repo:MemberRepository=Depends(get_member_repository)
):
    return PostService(post_repo,member_repo)