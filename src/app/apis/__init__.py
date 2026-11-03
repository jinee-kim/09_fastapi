from fastapi import APIRouter,Query,Depends
from app.services.member_service import get_member_service,MemberService
from app.enums.member_enum import MemberProvider