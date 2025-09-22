import asyncio
import websockets


async def connect_elevenlabs_ws(url: str, headers: dict):
	return await websockets.connect(url, extra_headers=headers)


async def forward_client_to_eleven(client_ws, eleven_ws):
	while True:
		msg = await client_ws.receive()
		if msg.get("type") == "websocket.disconnect":
			break
		if (data := msg.get("bytes")) is not None:
			await eleven_ws.send(data)
		elif (text := msg.get("text")) is not None:
			await eleven_ws.send(text)


async def forward_eleven_to_client(eleven_ws, client_ws):
	async for message in eleven_ws:
		if isinstance(message, (bytes, bytearray)):
			await client_ws.send_bytes(message)
		else:
			await client_ws.send_text(message)


async def bidirectional_bridge(client_ws, eleven_ws):
	await asyncio.gather(
		forward_client_to_eleven(client_ws, eleven_ws),
		forward_eleven_to_client(eleven_ws, client_ws),
	) 