import discord as d
from discord.ext import commands
from discord.activity import CustomActivity
import asyncio
import sys
from gpiozero import Button
import discord.ext.tasks as tasks

from NouveauBotPortier.constants import DoorStatus

class BotPortier(commands.Bot):
    doorStatus : str
    doorStatus_isOverriden: bool
    button : Button
    configuration: dict
    status : d.Status

    def __init__(self, conf: dict) -> None:
        super().__init__(command_prefix=conf["prefix"], intents=conf["intents"])
        self.configuration = conf
        self.button = Button(4)
        self.checkButton.start()
        
    
    @tasks.loop(seconds=30)
    async def checkButton(self) -> None:
        """checks the door state and changes the presence if it is not currently overriden"""
        if not self.doorStatus_isOverriden:
            if self.button.is_active:
                self.doorStatus = DoorStatus.OPEN
                self.status = d.Status.online
            else:
                self.doorStatus = DoorStatus.CLOSED
                self.status = d.Status.do_not_disturb
        
        await self.change_presence(activity=CustomActivity(DoorStatus.OPEN), status=self.status)
        #send a notification inside the specified channel
        await self.get_channel(self.configuration["notification_channel"]).send(f"Local {self.doorStatus} !")
    

    @checkButton.before_loop
    async def before_checkDoorStatus(self) -> None:
        print("waiting for bot...")
        #TODO
    



