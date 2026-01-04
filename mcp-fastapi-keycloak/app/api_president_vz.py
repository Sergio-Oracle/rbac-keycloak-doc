from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.models import President
from app.schemas import PresidentCreate, PresidentResponse
from app.crud import get_all, create, delete
from app.auth import require_role

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/presidents", tags=["Presidents"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔓 READ → reader
@router.get(
    "/",
    response_model=list[PresidentResponse],
    dependencies=[Depends(require_role("president_reader"))]
)
def list_presidents(db: Session = Depends(get_db)):
    return get_all(db)

# 🔒 WRITE → admin
@router.post(
    "/",
    response_model=PresidentResponse,
    dependencies=[Depends(require_role("president_admin"))]
)
def create_president(data: PresidentCreate, db: Session = Depends(get_db)):
    pres = President(**data.dict())
    return create(db, pres)

# 🔒 DELETE → admin
@router.delete(
    "/{code}",
    dependencies=[Depends(require_role("president_admin"))]
)
def delete_president(code: int, db: Session = Depends(get_db)):
    return delete(db, code)
