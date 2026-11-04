from sqlalchemy import BigInteger,Sequence,String,UniqueConstraint,DateTime,Identity,Text,Integer,Enum as SQLEnum,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from datetime import datetime, timedelta,timezone
from app.infrastructure.postgresql import Base
from typing import TYPE_CHECKING

KST=timezone(timedelta(hours=9))

if TYPE_CHECKING:
    from app.models.member_model import Member

class Post(Base):
    __tablename__="members"
    id:Mapped[int]=mapped_column(BigInteger,Identity(),primary_key=True)
    post_title:Mapped[str]=mapped_column(Text,nullable=False)
    post_content:Mapped[str]=mapped_column(Text,nullable=False)
    post_read_count:Mapped[int]=mapped_column(BigInteger)
    #post_read_like 좋아요는 외부 테이블을 관계로 맺고 테이블의 길이를 세는것으로 처리하고 내부 데이터베이스에 넣지 않음(아마 실시간성?)
    post_updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True), default=lambda:datetime.now(KST))
    post_created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True), default=lambda:datetime.now(KST))

    #관계
    member_id:Mapped[int]=mapped_column(ForeignKey("members.id"),nullable=False)
    member:Mapped["Member"]=relationship("Member",back_populates="posts")
