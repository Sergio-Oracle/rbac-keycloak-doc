from sqlalchemy import Column, Integer, String
from app.database import Base

class President(Base):
    __tablename__ = "president"

    code = Column(Integer, primary_key=True, index=True)
    prenom = Column(String(100))
    nom = Column(String(100))
    solde = Column(Integer)
