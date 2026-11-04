from sqlalchemy import BigInteger,Sequence,String,UniqueConstraint,DateTime,Identity,Text,Integer,Enum as SQLEnum
from sqlalchemy.orm import Mapped,mapped_column,relationship
from datetime import datetime, timedelta,timezone
from app.infrastructure.postgresql import Base
from app.enums.member_enum import MemberProvider

KST=timezone(timedelta(hours=9))

class Member(Base):
    __tablename__="members"
    id:Mapped[int]=mapped_column(BigInteger,Identity(),primary_key=True)
    member_email:Mapped[str]=mapped_column(Text,nullable=False)
    member_pw:Mapped[str|None]=mapped_column(Text)
    member_name:Mapped[str|None]=mapped_column(Text)
    member_age:Mapped[int|None]=mapped_column(Integer)
    member_profile:Mapped[str|None]=mapped_column(Text,default="")
    member_provider_id:Mapped[str|None]=mapped_column(Text,unique=True)
    member_provider:Mapped[MemberProvider]=mapped_column(
        SQLEnum(MemberProvider,native_enum=False),
        nullable=False,
        default=MemberProvider.LOCAL.value
    )
    member_created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True), default=lambda:datetime.now(KST))

    __table_args__=(
        UniqueConstraint("member_email","member_provider",name="uq_member_email_provider"),
    )
