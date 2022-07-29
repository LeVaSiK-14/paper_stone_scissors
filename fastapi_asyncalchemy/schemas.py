from pydantic import BaseModel, Field


class OfferSchemaCreate(BaseModel):
    nft_id: int = Field(...)
    user_id: int = Field(...)

    
    class Config:
        orm_mode = True
        
        

class OfferSchemaGet(BaseModel):
    nft_id: int
    user_id: int
    offer_id: int
    
    class Config:
        orm_mode = True
        
        
class OfferAcceptSchema(BaseModel):
    nft_id: int = Field(...)
    user_id: int = Field(...)
    offer_id: int = Field(...)

    
    class Config:
        orm_mode = True
        
        
class BattleSchema(BaseModel):
    
    offer_id: int = Field(...)
    accept_id: int = Field(...)
    
    class Config:
        orm_mode = True