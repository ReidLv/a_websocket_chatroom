# -*- coding: utf-8 -*-
# @Author  : ReidLv
# @File    : main.py
# @Time：2022 9/9/22 5:04 AM
# @Site：https://github.com/ReidLv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()


class ConnectionManager(object):
    def __init__(self):
        self.active_connections = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self, ws):
        self.active_connections.remove(ws)

    @staticmethod
    async def send_personal_message(msg, ws):
        await ws.send_text(msg)

    async def broadcast(self, msg):
        for connection in self.active_connections:
            await connection.send_text(msg)


manager = ConnectionManager()


# http handler
@app.get("/")
def index():
    return {"hello world!"}


@app.get('/user1', response_class=HTMLResponse)
def user1():
    return open("index1.html", "r").read()


@app.get("/user2", response_class=HTMLResponse)
def user2():
    return open("index2.html", "r").read()


# /websocket handler
@app.websocket("/ws/{user}")
async def websocket_endpoint(ws: WebSocket, user: str):
    await manager.connect(ws)
    await manager.broadcast(f"用户{user}进入聊天室")

    try:
        while True:
            data = await ws.receive_text()
            await manager.send_personal_message(f"你说了：{data}", ws)
            await manager.broadcast(f"用户-{user} 说：{data}")
    except WebSocketDisconnect:
        manager.disconnect(ws)
        await manager.broadcast(f"用户-{user} 退出了聊天室")


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=5000,
        workers=4,
        reload=True,
        debug=True
    )
