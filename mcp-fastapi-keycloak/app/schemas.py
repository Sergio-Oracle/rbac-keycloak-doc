from pydantic import BaseModel

class PresidentBase(BaseModel):
    prenom: str
    nom: str
    solde: int

class PresidentCreate(PresidentBase):
    code: int

class PresidentResponse(PresidentBase):
    code: int

    class Config:
        from_attributes = True
