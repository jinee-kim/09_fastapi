from enum import Enum

class PostSortEnum(str,Enum):
    LATEST="LATEST"
    OLDEST="OLDEST"
    VIEWS="VIEWS"

class PostSearchEnum(str,Enum):
    TITLE="TITLE" #제목으로 찾기
    CONTENT="CONTENT" #작성자로 찾기
    WRITER="WRITER" #내용으로 찾기
    TITLE_CONTENT="TITLE_CONTENT" #제목+내용으로 찾기
    