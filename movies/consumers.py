import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("seat_updates", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("seat_updates", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            "seat_updates",
            {
                "type": "send_update",
                "message": data["message"]
            }
        )

    async def send_update(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))
