import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from .utils.CacheMethods import CacheMethods


class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.taskID = None

    async def disconnect(self, close_code):
        if self.taskID:
            currentPrice = CacheMethods.getCache(f"order_info_price__${self.taskID}")
            currentTime = CacheMethods.getCache(f"order_info_time__${self.taskID}")

            if currentPrice and currentTime:
                await self.send(json.dumps({
                    "resultPrice": currentPrice,
                    "resultTime": currentTime
                }))
            else:
                await self.send(json.dumps({
                    "error": "Data was corrupted"
                }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        self.taskID = text_data_json.get("taskID")
        
        amountOfConnections = CacheMethods.getCache(f"task_control__${self.taskID}")
        
        if amountOfConnections:
            amountOfConnections = int(amountOfConnections)
            if amountOfConnections < 2:
                CacheMethods.setCache(f"task_control__${self.taskID}", amountOfConnections + 1)
            else:
                await self.send(json.dumps({
                    "error": "Reached maximum of connections"
                }))
                await self.close()
                return
        else:
            CacheMethods.setCache(f"task_control__${self.taskID}", 1)

        if self.taskID:
            try:
                while True:
                    controlStatus = CacheMethods.getCache(f"task_control__${self.taskID}")
                    
                    if controlStatus:
                        controlStatus = json.loads(controlStatus)
                        currentPrice = CacheMethods.getCache(f"order_info_price__${self.taskID}")
                        currentTime = CacheMethods.getCache(f"order_info_time__${self.taskID}")

                        if controlStatus == "stop":
                            await self.close()
                            break

                        await self.send(json.dumps({
                            "currentPrice": currentPrice,
                            "currentTime": currentTime
                        }))
                    else:
                        await self.send(json.dumps({
                            "error": "Сontrol status wasn't found"
                        }))
                        await self.close()
                        break

                    await asyncio.sleep(10)

            except Exception as e:
                await self.send(json.dumps({
                    "error": f"An error occurred: {str(e)}"
                }))
                await self.close()
        else:
            await self.send(json.dumps({
                "error": "ID wasn't found"
            }))
            await self.close()