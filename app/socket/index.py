import socketio

socket = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

@socket.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@socket.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@socket.event
async def message(sid, data):
    await socket.emit("message", data, room=sid)

socket_app = socketio.ASGIApp(socket)