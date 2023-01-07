import discord as d
from discord.ext import commands
from discord.activity import Game
from gpiozero import Button, Device
from gpiozero.pins.mock import MockFactory
import discord.ext.tasks as tasks
import logging
import asyncio


from constants import DoorStatus

class BotPortier(commands.Bot):
    button : Button
    configuration: dict

    doorStatus : d.activity.Game
    overridenDoorStatus: d.activity.Game

    status : d.Status
    overridenStatus : d.Status

    override: bool

    door: bool
    def __init__(self, configuration: dict) -> None:
        super().__init__(command_prefix=configuration["prefix"], intents=d.Intents.all())
        #simulate the pi
        Device.pin_factory = MockFactory()
        self.configuration = configuration
        self.button = Button(4)
        self.doorStatus = Game(self.configuration["ACTIVITY_STRING"]["CLOSED"])
        self.status = d.Status.do_not_disturb
        self.override = False
        self.door = True
        logging.basicConfig(filename=configuration["logfile"])
        
    
    @tasks.loop(seconds=10)
    async def checkButton(self) -> None:
        """checks the door state every x seconds and changes the presence if it is not currently overriden"""
        logging.info("checkedButton")
        print("test")
        #remember the precedent status to act later if it changed
        oldDoorStatus = self.doorStatus


        if self.door:#self.button.is_active:
            self.doorStatus = Game(self.configuration["ACTIVITY_STRING"]["OPEN"])
            self.status = d.Status.online
        else:
            self.doorStatus = Game(self.configuration["ACTIVITY_STRING"]["CLOSED"])
            self.status = d.Status.do_not_disturb

        #change the bot's presence if it's not currently overriden
        if self.override :
            await self.updatePresenceOverride()
        else:
            await self.updatePresence()
            if oldDoorStatus != self.doorStatus:
                channel = self.get_channel(self.configuration["notification_channel"])
                await channel.send(self.doorStatus.name) #type:ignore

    


    async def overrideDisplay(self, activity: d.Game, status:d.Status):
        """override the door state and display custom activity (usually for events)"""
        self.override = True
        self.overridenDoorStatus = activity
        self.overridenStatus = status
        await self.updatePresenceOverride()

    async def updatePresence(self):
        logging.info(f"changed bot presence to: [{self.doorStatus.name}] | [{self.status}]")
        await self.change_presence(activity=self.doorStatus, status=self.status)
    
    async def updatePresenceOverride(self):
        logging.info(f"changed bot presence to: [{self.overridenDoorStatus.name}] | [{self.overridenStatus}]")
        await self.change_presence(activity=self.overridenDoorStatus, status=self.overridenStatus)



