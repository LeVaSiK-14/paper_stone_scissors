import asyncio
import typer
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi_asyncalchemy.exceptions import DuplicatedEntryError
from fastapi_asyncalchemy.db.base import init_models, get_session
from fastapi_asyncalchemy import service, schemas, models
from fastapi_asyncalchemy.managers import ConnectionManager
import json

from typing import List

from fastapi.responses import HTMLResponse


app = FastAPI()
cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            # service.add_offer(get_session, data['user_id'], data['nft_id'])
            # print(type(data['user_id']), type(data['nft_id']))
            await websocket.send_text(f"Message text was: {data}")
            
            # await service.add_offer(get_session, data['user_id'], data['nft_id'])
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except:
        pass


@app.post("/battles_create/")
async def add_offer(offer: schemas.OfferSchemaCreate, session: AsyncSession = Depends(get_session)):
    offer = service.add_offer(session, offer.user_id, offer.nft_id)
    try:
        await session.commit()
        return offer
    except IntegrityError as ex:
        await session.rollback()
        raise DuplicatedEntryError("The offer is already stored")
    
    
@app.get("/battles_list/", response_model=list[schemas.OfferSchemaGet])
async def get_offers(session: AsyncSession = Depends(get_session)):
    offers = await service.get_offer_list(session)
    return [schemas.OfferSchemaGet(user_id=offer.user_id, nft_id=offer.nft_id, offer_id=offer.offer_id) for offer in offers]


@app.post("/battles/accept/")
async def add_offer_accept(offer_accept: schemas.OfferAcceptSchema, session: AsyncSession = Depends(get_session)):
    offer_accept = service.add_accept(session, offer_accept.offer_id, offer_accept.user_id, offer_accept.nft_id)
    try:
        await session.commit()
        return offer_accept
    except IntegrityError as ex:
        await session.rollback()
        raise DuplicatedEntryError("The offer accept is already stored")
    
    
@app.post("/battle_start/")
async def battle_start(battle_new: schemas.BattleSchema, session: AsyncSession = Depends(get_session)):
    battle = service.battle_start(session, battle_new.offer_id, battle_new.accept_id)
    try:
        await session.commit()
        return battle
    except IntegrityError as ex:
        await session.rollback()
        raise DuplicatedEntryError("The battle is already stored")

if __name__ == "__main__":
    cli()
