from sqlalchemy.orm import Session
from app.models import President

def get_all(db: Session):
    return db.query(President).all()

def get_one(db: Session, code: int):
    return db.query(President).filter(President.code == code).first()

def create(db: Session, pres: President):
    db.add(pres)
    db.commit()
    db.refresh(pres)
    return pres

def delete(db: Session, code: int):
    pres = get_one(db, code)
    if pres:
        db.delete(pres)
        db.commit()
    return pres
