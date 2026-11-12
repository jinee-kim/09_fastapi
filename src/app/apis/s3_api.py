import os
from dotenv import load_dotenv
from fastapi import APIRouter, Query, Depends,UploadFile,File,Form
from app.services.s3_service import S3Service,get_s3_service
from app.schemas.common_schema import ApiResponseDTO
from app.enums.s3_enums import S3Folder
from fastapi.responses import RedirectResponse



router = APIRouter()

@router.post(
    "/image",
    summary="이미지 업로드",
    response_model=ApiResponseDTO,
)
async def upload_image(
    file:UploadFile=File(...),
    folder:S3Folder=Form(...),
    s3_service:S3Service=Depends(get_s3_service)
):
    result=await s3_service.upload_image_with_thumbnail(
        file=file,
        folder=folder.value
    )
    return ApiResponseDTO(
        success=True,
        message="이미지 업로드 성공",
        data=result
    )

@router.post(
        "/general-file",
        summary="파일 업로드",
        response_model=ApiResponseDTO,
)
async def upload_general_file(
    file:UploadFile=File(...),
    folder:S3Folder=Form(...),
    s3_service:S3Service=Depends(get_s3_service)
):
    result=await s3_service.upload_file(
        file=file,
        folder=folder.value
    )
    return ApiResponseDTO(
        success=True,
        message="파일 업로드 성공",
        data=result
    )

@router.get(
    "/get-image",
    summary="이미지 보기(url로)"
)
async def get_image(
    key:str,
    s3_service:S3Service=Depends(get_s3_service)
):
    image_url=s3_service.get_url(key)
    return RedirectResponse(image_url)

@router.get(
    "/download",
    summary="이미지 다운로드"
)
async def download_file(
    key:str,
    s3_service:S3Service=Depends(get_s3_service)
):
    download_url=await s3_service.get_download_url(key)
    return RedirectResponse(download_url)
