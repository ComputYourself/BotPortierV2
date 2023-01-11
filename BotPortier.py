import discord as d
from discord.ext import commands
from discord.activity import Game
from gpiozero import Button, Device
import discord.ext.tasks as tasks
import logging
import asyncio
import yaml
import datetime as dt

class BotPortier(commands.Bot):
    button : Button
    configuration: dict

    doorStatus : d.activity.Game
    overridenDoorStatus: d.activity.Game
    eventStatus: d.activity.Game

    status : d.Status
    overridenStatus : d.Status

    override: bool
    event_occuring: bool
    logger : logging.Logger


    def __init__(self, configuration: dict, data: dict) -> None:
        super().__init__(command_prefix=configuration["prefix"], intents=d.Intents.all())
        

        self.configuration = configuration
        #self.button = Button(4)


        self.doorStatus = Game(self.configuration["ACTIVITY_STRING"]["OPEN"]) if data["status"] else Game(self.configuration["ACTIVITY_STRING"]["CLOSED"])
        self.status = d.Status(data["status"])
        self.override = False
        self.event_occuring = False

        logging.basicConfig(filename=configuration["logfile"], level=logging.INFO)
        self.logger = logging.getLogger("botPortier")
        
    
    @tasks.loop(seconds=10.0)
    async def checkButton(self) -> None:
        """checks the door state every x seconds and changes the presence if it is not currently overriden. Also checks for events."""
        print("checkButton")
        #print(dt.datetime.now())
        #remember the precedent status to act later if it changed
        oldDoorStatus = self.doorStatus
        
        announceDoor = False
        announceEvent = False

        if self.button.is_active:
            self.doorStatus = Game(self.configuration["ACTIVITY_STRING"]["OPEN"])
            self.status = d.Status.online
        else:
            self.doorStatus = Game(self.configuration["ACTIVITY_STRING"]["CLOSED"])
            self.status = d.Status.dnd

        if self.doorStatus != oldDoorStatus:
            print("announce")
            announceDoor = True


        #check for events
        guild = self.guilds[0]
        events = guild.scheduled_events
        current_time = dt.datetime.now(dt.timezone.utc)

        if events:
            print(events)
            for event in events:
                if event.end_time:
                    if event.start_time < current_time and event.end_time > current_time:
                        if not self.event_occuring:
                            announceEvent = True
                        self.event_occuring = True
                        self.eventStatus = Game(event.name)
                        await self.change_presence(activity=self.eventStatus, status=d.Status.online)
        else:
            self.event_occuring = False


        
        await self.updatePresence(announceDoor=announceDoor, announceEvent=announceEvent)

        print(dt.datetime.now())
            



    async def overrideDisplay(self, activity: d.Game, status:d.Status):
        """override the door state and display custom activity (usually for events)"""
        self.override = True
        self.overridenDoorStatus = activity
        self.overridenStatus = status
        self.logger.info(f"changed bot presence to: [{self.overridenDoorStatus.name}] | [{self.overridenStatus}]")
        await self.change_presence(activity=self.overridenDoorStatus, status=self.overridenStatus)
        await self.get_channel(self.configuration["notification_channel"]).send(f"nouveau statut: [{self.overridenDoorStatus}]") #type:ignore
        self.updateStatusFile()


    async def updatePresence(self, ctx=None, announceDoor=None, announceEvent=None):
        """update bot presence"""
        if self.event_occuring:
            await self.change_presence(activity=self.eventStatus, status=d.Status.online)
            if announceEvent:
                await self.get_channel(self.configuration["notification_channel"]).send(f"début de l'événement: {self.eventStatus.name}") #type:ignore
        else:
            await self.change_presence(activity=self.doorStatus, status=self.status)
            if announceDoor:
                self.logger.info(f"announced : {self.doorStatus.name}")
                await self.get_channel(self.configuration["notification_channel"]).send(self.doorStatus.name) #type:ignore


        self.logger.info(f"changed bot presence to: [{self.doorStatus.name}] | [{self.status}]")
        self.updateStatusFile()

    def updateStatusFile(self):
        with open(self.configuration["backup_filepath"], "w") as file:
            dict = {"doorStatus" : self.button.is_active, "status": self.status.name}
            yaml.safe_dump(dict, file)


