from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert,select,update,delete,func,exists,desc,asc,or_
from app.infrastructure.postgresql import get_postgresql_db
from fastapi import Depends
from app.models.post_model import Post, KST
from app.models.member_model import Member
from app.schemas.post_schema import PostCreateDTO
from app.enums.post_enum import PostSortEnum,PostSearchEnum
from sqlalchemy.orm import joinedload
from datetime import datetime

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

    #게시글id로 게시글 1개 조회
    async def find_post_by_id(self,id:int):
        query=(
            select(Post)
            .options(joinedload(Post.member))
            .where(Post.id==id)
        )
        result=await self.db.execute(query)
        return result.scalar_one_or_none()
    #멤버id로 게시글 전체 조회
    async def find_all_post_by_memberid(self,member_id:int):
        query=(
            select(Post)
            .where(Post.member_id==member_id)
        )
        result=await self.db.execute(query)
        return result.scalars().all()

    #게시글 페이지네이션+정렬 전체조회
    async def find_post_by_paging(
            self,
            offset:int,
            limit:int,
            sort_by:PostSortEnum=PostSortEnum.LATEST.value
    ):
        query=(
            select(Post).options(joinedload(Post.member))
        )
        if sort_by==PostSortEnum.OLDEST:
            query=query.order_by(asc(Post.id))
        elif sort_by==PostSortEnum.LATEST:
            query=query.order_by(desc(Post.id))
        else:
            query=query.order_by(desc(Post.post_read_count))
        #정렬된 상태에서 offset,limit처리
        query=query.offset(offset).limit(limit)
        result=await self.db.execute(query)
        return result.scalars().all()

    #게시글 전체 갯수 조회
    async def count_posts(self)->int:
        query=(select(func.count()).select_from(Post))
        result=await self.db.execute(query)
        return result.scalar_one()

    #게시글 검색(제목,내용,작성자,제목+내용)
    async def search_filter(
            self, 
            offset:int,
            limit:int,
            sort_by:PostSortEnum=PostSortEnum.LATEST.value,
            search_keyword:PostSearchEnum=PostSearchEnum.TITLE.value,
            search_detail:str|None=None
            ):
        
        query=(select(Post).options(joinedload(Post.member)))
        count_query=(select(func.count()).select_from(Post))

        if search_keyword and search_detail:
            search_word=f"%{search_detail}%"
            condition=None

            if search_keyword==PostSearchEnum.TITLE:
                condition=Post.post_title.like(search_word)
            elif search_keyword==PostSearchEnum.CONTENT:
                condition=Post.post_content.like(search_word)
            elif search_keyword==PostSearchEnum.WRITER:
                query=query.join(Post.member)
                count_query=count_query.join(Post.member)
                condition=Member.member_name.like(search_word)
            elif search_keyword==PostSearchEnum.TITLE_CONTENT:
                condition=or_(
                    Post.post_title.like(search_word),
                    Post.post_content.like(search_word)
                )
            if condition is not None:
                query=query.where(condition)
                count_query=count_query.where(condition)

        if sort_by==PostSortEnum.OLDEST:
            query=query.order_by(asc(Post.id))
        elif sort_by==PostSortEnum.LATEST:
            query=query.order_by(desc(Post.id))
        else:
            query=query.order_by(desc(Post.post_read_count),(Post.id))

        #정렬된 상태에서 offset,limit처리
        query=query.offset(offset).limit(limit)
        result=await self.db.execute(query)
        posts=list(result.scalars().all())
        count_result=await self.db.execute(count_query)
        total_count=count_result.scalar_one()

        return posts,total_count


    #게시글 수정
    async def update_post(
        self,
        post_id:int,
        post_title:str,
        post_content:str
    ):
        cur_time=datetime.now(KST)
        query=(
            update(Post)
            .where(Post.id==post_id)
            .values(post_title=post_title,post_content=post_content,post_updated_at=cur_time)
            .returning(Post)
        )
        result=await self.db.execute(query)
        await self.db.commit()
        return result.scalar_one_or_none()


    #게시글 삭제
    async def delete_post(
            self,
            post_id:int
    )->bool:
        query=(
            delete(Post).where(Post.id==post_id)
        )
        result=await self.db.execute(query)
        await self.db.commit()
        return result.rowcount>0

#주입 팩토리 메서드
def get_post_repository(db:AsyncSession=Depends(get_postgresql_db)):
    return PostRepository(db)