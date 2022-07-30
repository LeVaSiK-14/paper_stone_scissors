from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_asyncalchemy.models import *


async def get_offer_list(session: AsyncSession) -> list[Offer]:
    result = await session.execute(select(Offer))
    return result.scalars().all()


def add_offer(session: AsyncSession, user_id: str, nft_id: str):
    new_offer = Offer(user_id=int(user_id), nft_id=int(nft_id))
    session.add(new_offer)
    return new_offer


def add_accept(session: AsyncSession, offer_id: str, user_id: str, nft_id: str):
    new_offer_accept = OfferAccept(offer_id=int(offer_id), user_id=int(user_id), nft_id=int(nft_id))
    session.add(new_offer_accept)
    return new_offer_accept


def battle_start(session: AsyncSession, offer_id: str, accept_id: str):
    new_battle = Battle(offer_id=int(offer_id), accept_id=int(accept_id))
    session.add(new_battle)
    return new_battle


def battle_round(session: AsyncSession, user_id: str, battle_id: str, choice: str, round_: str):
    new_round = BattleRound(
        battle_id=int(battle_id), user_id=int(user_id),
        choice=int(choice), battle_round=int(round_)
        )
    session.add(new_round)
    return new_round
