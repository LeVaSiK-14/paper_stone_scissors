# from secrets import choice
from sqlalchemy import Column, Integer, ForeignKey, ARRAY, JSON
from fastapi_asyncalchemy.db.base import Base


class Offer(Base):
    __tablename__ = 'offers'

    offer_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, index=True)
    user_id = Column(Integer, nullable=False)
    nft_id = Column(Integer, nullable=False)
    
    
    def __repr__(self):
        return f"<Offer ID= {self.offer_id} user ID= {self.user_id} nft ID= {self.nft_id}/>"
    
    
class OfferAccept(Base):
    __tablename__ = 'offer_accepts'

    offer_accept_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, index=True)
    offer_id = Column(Integer, ForeignKey('offers.offer_id'))
    user_id = Column(Integer, nullable=False)
    nft_id = Column(Integer, nullable=False)
    
    
    def __repr__(self):
        return f"<Offer ID= {self.offer_id} user ID= {self.user_id} nft ID= {self.nft_id}/>"


class Battle(Base):
    __tablename__ = 'battles'
    
    battle_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, index=True)
    offer_id = Column(Integer, ForeignKey('offers.offer_id'))
    accept_id = Column(Integer, ForeignKey('offer_accepts.offer_accept_id'))
    win_user_id = Column(Integer, nullable=True)


class BattleRound(Base):
    __tablename__ = 'battle_rounds'
    
    battle_round_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, index=True)
    battle_id = Column(Integer, ForeignKey('battles.battle_id'))
    user_id = Column(Integer, nullable=False)
    choice = Column(Integer, nullable=False)
    battle_round = Column(Integer, nullable=False)
    

class WinBattleRound(Base):
    __tablename__ = 'win_battle_rounds'
    
    win_battle_round_id = Column(Integer, autoincrement=True, primary_key=True, unique=True, index=True)
    battle_id = Column(Integer, ForeignKey('battles.battle_id'))
    user_id = Column(Integer, nullable=False)
    