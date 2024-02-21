from channels.generic.websocket import AsyncWebsocketConsumer


class RealtimeDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Add the WebSocket connection to a group
        await self.channel_layer.group_add("data_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the group
        await self.channel_layer.group_discard("data_group", self.channel_name)

    async def receive(self, text_data):
        # Handle incoming WebSocket messages
        # Process the received data and send a response
        response = f"Received: {text_data}"
        await self.send(text_data=response)

    async def send_data(self, event):
        # Send data to the WebSocket connection
        await self.send(text_data=event["text"])
