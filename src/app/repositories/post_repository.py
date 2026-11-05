from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert,select,update,delete,func,exists
from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends
from app.models.post_model import Post
from app.schemas.post_schema import PostCreateDTO

class PostRepository:

    #생성자 주입
    def __init__(self,db):
        self.db=db

    #게시글 작성
    async def create_post(self, member_id:int, post:PostCreateDTO):
        post.model_dump()

        query=(
            insert(Post)
            .values(
                **post.model_dump(),
                member_id=member_id
            )
            .returning(
                Post.id
            )
        )
        result=await self.db.execute(query)
        await self.db.commit()
        new_post_id=result.scalar_one()
        return new_post_id

    #게시글 1개 조회
    async def find_post_by_id(self,id:int):
        pass
    #게시글 전체 조회
    #게시글 수정
    #게시글 삭제


#주입 팩토리 메서드
def get_post_repository(db:AsyncSession=Depends(get_postgresql_db)):
    return PostRepository(db)