from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

SessionDep = Annotated(AsyncSession, Depends(get_session)) # TODO: learn