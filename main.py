import asyncio
import typer
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi_asyncalchemy.exceptions import DuplicatedEntryError
from fastapi_asyncalchemy.db.base import init_models, get_session
from fastapi_asyncalchemy import service, schemas
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


async def send_result(text):
    await manager.active_connections[0].send_json({
        "round_win": text
    })
    await manager.active_connections[1].send_json({
        "round_win": text
    })
    manager.user_move.clear()
    print(manager.user_lifes)
    print(manager.user_move, 'after clear', '\n\n\n')
    
    
@app.websocket("/ws/battles_move")
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            
            user_choice = {"user_id": data['user_id'], "choice": data['choice'], 'web_socket': websocket}
            if user_choice not in manager.user_move:
                service.battle_round(session, data['user_id'], data['battle_id'], data['choice'], data['round'])
                await session.commit()
                
                manager.user_move.append(user_choice)
            
            else:
                await websocket.send_json(
                    {"message": "вы уже сделали свой ход ожидайте противника"}
                )
            #     print(manager.user_move, '\n\n\n user move in else')
            
            # print(manager.user_move, '\n'*8)
            # print(len(manager.user_move))
            
            if len(manager.user_move) == 1:
                await websocket.send_json({
                    "message": "Waiting ather player",
                })
            if len(manager.user_move) == 2:
                data = manager.user_move
                if int(data[0]['choice']) == int(data[1]['choice']):
                    await send_result('Ничья')
                    
                elif int(data[0]['choice']) == 1 and int(data[1]['choice']) == 2:
                    
                    await send_result(f"Выйграл игрок с ID {data[0]['user_id']}")
                
                elif int(data[0]['choice']) == 1 and int(data[1]['choice']) == 3:
                    await send_result(f"Выйграл игрок с ID {data[1]['user_id']}")
                    
                elif int(data[0]['choice']) == 3 and int(data[1]['choice']) == 2:
                    await send_result(f"Выйграл игрок с ID {data[1]['user_id']}")
                    
                    
                    
                elif int(data[0]['choice']) == 2 and int(data[1]['choice']) == 1:
                    await send_result(f"Выйграл игрок с ID {data[1]['user_id']}")
                
                elif int(data[0]['choice']) == 3 and int(data[1]['choice']) == 1:
                    await send_result(f"Выйграл игрок с ID {data[0]['user_id']}")
                    
                elif int(data[0]['choice']) == 2 and int(data[1]['choice']) == 3:
                    await send_result(f"Выйграл игрок с ID {data[0]['user_id']}")
                    
                else:print('___________________')

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
