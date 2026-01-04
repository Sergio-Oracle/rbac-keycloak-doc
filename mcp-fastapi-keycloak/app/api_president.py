from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import President
from app.schemas import PresidentCreate, PresidentResponse
from app.crud import get_all, create, delete
from app.auth import verify_token

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/presidents", tags=["Presidents"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[PresidentResponse])
def list_presidents(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    return get_all(db)

@router.post("/", response_model=PresidentResponse)
def create_president(
    data: PresidentCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    pres = President(**data.dict())
    return create(db, pres)

@router.delete("/{code}")
def delete_president(
    code: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    return delete(db, code)
