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

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>


    <h4>
        <span>Камень - 1</span>
        <span>Ножницы - 2</span>
        <span>Бумага - 3</span>
    </h4>
    
    <h3 id="message"></h3>

    <input type="text" id="user_id" placeholder="user ID" >
    <input type="text" id="battle_id" placeholder="Batlle ID">
    <input type="text" id="choice" placeholder="choice" >
    <input type="text" id="round" placeholder="Round">

    
    <h3 id="is_ready"></h3>
    <button type="button" onclick="SendValue()">Отправить</button>


    <h5 id="rounds_win"></h5>

    <h5 id="battle_win"></h5>
    <!-- let battle_win = document.getElementById("battle_win"); -->


    <!-- if (data['round_win']){
        rounds_win.innerHTML += `<h4>${data['round_win']}</h4>`
    } -->

    <script>
        var ws = new WebSocket("ws://localhost:8000/ws/battles_move");

        const SendValue = () => {
            let rounds_win = document.getElementById("rounds_win"); 
            let user_id = document.getElementById("user_id").value; 
            let battle_id = document.getElementById("battle_id").value;
            let round = document.getElementById("round").value; 
            let choice = document.getElementById("choice").value;
            let data = {
                'user_id': user_id,
                'battle_id': battle_id,
                'round': round,
                'choice': choice
            }
            ws.send(JSON.stringify(data))
        }
        ws.onmessage = function(e) {
            let message = document.getElementById("message"); 
            let is_ready = document.getElementById("is_ready"); 
            data = JSON.parse(e.data)

            if (data['player'] == 1) {
                message.innerHTML = ''
                message.innerHTML = data['message']
            }

            if (data['player'] == 2 ){
                is_ready.innerHTML = ''
                is_ready.innerHTML = data['message']
            }
            
            console.log(data)
        }
        ws.onclose = function(e) {
            console.log(e)
        }
    </script>
</body>
</html>
"""


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")
    
    
@app.get("/")
async def get():
    return HTMLResponse(html)


manager = ConnectionManager()


async def send_result(text):
    await manager.connections[0]['websocket'].send_json({
        "round_win": text
    })
    await manager.connections[1]['websocket'].send_json({
        "round_win": text
    })
    manager.user_move.clear()
    
    
@app.websocket("/ws/battles_move")
async def websocket_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            
            user_choice = {
                "user_id": data['user_id'], 
                "choice": data['choice'], 
                'websocket': websocket
            }
            
            if user_choice not in manager.user_move:
                service.battle_round(
                    session, data['user_id'], data['battle_id'], 
                    data['choice'], data['round']
                )
                await session.commit()
                
                manager.user_move.append(user_choice)
            
            else:
                await websocket.send_json(
                    {"message": "вы уже сделали свой ход ожидайте противника"}
                )
            
            if len(manager.user_move) == 1:
                await websocket.send_json({
                    "message": "Waiting ather player",
                })
            if len(manager.user_move) == 2:
                data = manager.user_move
                
                if int(data[0]['choice']) == int(data[1]['choice']):
                    await send_result('Ничья')
                    
                elif int(data[0]['choice']) == 1 and int(data[1]['choice']) == 2:
                    await manager.minus_lifes(data[1]['websocket'])
                    await send_result(f"Выйграл игрок с ID {data[0]['user_id']}")
                    await manager.win_lose()
                    
                elif int(data[0]['choice']) == 1 and int(data[1]['choice']) == 3:
                    await manager.minus_lifes(data[0]['websocket'])
                    await send_result(f"Выйграл игрок с ID {data[1]['user_id']}")
                    await manager.win_lose()
                    
                elif int(data[0]['choice']) == 3 and int(data[1]['choice']) == 2:
                    await manager.minus_lifes(data[0]['websocket'])
                    await send_result(f"Выйграл игрок с ID {data[1]['user_id']}")
                    await manager.win_lose()
                    
                elif int(data[0]['choice']) == 2 and int(data[1]['choice']) == 1:
                    await manager.minus_lifes(data[0]['websocket'])
                    await send_result(f"Выйграл игрок с ID {data[1]['user_id']}")
                    await manager.win_lose()
                    
                elif int(data[0]['choice']) == 3 and int(data[1]['choice']) == 1:
                    await manager.minus_lifes(data[1]['websocket'])
                    await send_result(f"Выйграл игрок с ID {data[0]['user_id']}")
                    await manager.win_lose()
                    
                elif int(data[0]['choice']) == 2 and int(data[1]['choice']) == 3:
                    await manager.minus_lifes(data[1]['websocket'])
                    await send_result(f"Выйграл игрок с ID {data[0]['user_id']}")
                    await manager.win_lose()
                    
                else:print('___________________')

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
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
