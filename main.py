import BotPortier as BotPortier
import os
import yaml
import logging
from discord import Game, Status
from discord.ext.commands import Context

configuration_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(configuration_path, "conf.yaml.local"), "r") as stream:
    conf = yaml.safe_load(stream)

bot = BotPortier.BotPortier(configuration=conf)

@bot.event
async def on_ready():
    print("ready")
    bot.checkButton.start()

@bot.event
async def on_connect():
    print("connected")

@bot.command()
async def changeDisplay(ctx : Context, arg1 : str, arg2 : str):
    #TODO check roles
    await bot.overrideDisplay(Game(arg1), Status(arg2))

async def stopDisplay(ctx : Context):
    bot.override = False

@bot.command()
async def changeDoorValue(ctx : Context, arg1 : str):
    bot.door = True if arg1 == "true" else False

bot.run(conf["bot_token"])