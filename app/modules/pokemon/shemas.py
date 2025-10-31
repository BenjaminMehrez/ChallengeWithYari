from pydantic import BaseModel, Field



class Pokemon(BaseModel):
  id: int = Field(..., ge=1, le=1025, description="Pokemon ID from PokeAPI")
  name: str = Field(..., min_length=1, description="Pokemon name")
