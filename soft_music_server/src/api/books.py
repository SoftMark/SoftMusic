from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class Book(BaseModel):
    title: str

BOOKS = [
    {
        'book_id': uuid4(),
        'name': 'Python Bases',
    },

]
BOOKS = {
    i['book_id']: i
    for i in BOOKS
}


@router.get("/books", tags=['Books',])
async def read_books():
    return {'books': [BOOKS.values()]}


@router.get('/books/{book_id}/', tags=['Books',])
def get_book(book_id: int):
    if book := BOOKS.get(book_id):
        return book
    raise HTTPException(status_code=404, detail='Not found')


@router.post('/books', tags=['Books',], summary='Create a new book')
def create_book(book: BaseModel):
    book_id = uuid4()
    BOOKS[book_id] = {
        'book_id': book_id,
        'title': book.title,
    }

