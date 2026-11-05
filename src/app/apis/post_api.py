from fastapi import APIRouter, Query, Depends
from app.services.post_service import get_post_service, PostService
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.post_schema import PostCreateDTO

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

