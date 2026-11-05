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


def get_post_service(
    post_repo:PostRepository=Depends(get_post_repository),
    member_repo:MemberRepository=Depends(get_member_repository)
):
    return PostService(post_repo,member_repo)