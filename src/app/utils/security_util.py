from passlib.context import CryptContext

#CryptContext를 쓰는이유
#1. 권장 방법이 아닌 코드를 사용할 때 자동 업데이트
#2. 알고리즘 추상화
#   - 나중에 알고리즘이 바껴도 코드수정 최소화

pws_context=CryptContext(schemes=["sha256_crypt"],deprecated="auto")

def get_pw_hash(password:str)->str:
    return pws_context.hash(password)

def vertify_pw(plain_password:str,hashed_password:str)->bool:
    return pws_context.verify(plain_password,hashed_password)