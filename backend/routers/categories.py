from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.db import get_session
from backend.models import Category
from backend.schemas import CategoryCreate
from backend.services import task_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[Category])
def list_categories(session: Session = Depends(get_session)):
    return task_service.list_categories(session)


@router.post("", response_model=Category, status_code=201)
def create_category(data: CategoryCreate, session: Session = Depends(get_session)):
    return task_service.create_category(session, data)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, session: Session = Depends(get_session)):
    deleted = task_service.delete_category(session, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
