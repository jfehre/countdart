from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])

@router.get("")
def get_hello_world():
    return "Hello World"