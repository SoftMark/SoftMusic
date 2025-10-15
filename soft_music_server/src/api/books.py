from fastapi import APIRouter

router = APIRouter()


@router.get("/books")
async def read_books():
    return {'data': 1}