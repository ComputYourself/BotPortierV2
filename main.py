import BotPortier as BotPortier
import os
import yaml
import logging
from discord import Game, Status
from discord.ext.commands import Context, parameter
import discord

configuration_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(configuration_path, "conf.yaml.local"), "r") as stream:
    conf = yaml.safe_load(stream)

with open(conf["backup_filepath"], 'r') as file:
    backup = yaml.safe_load(file)

bot = BotPortier.BotPortier(configuration=conf, data=backup)



@bot.event
async def on_connect():
    print("connected")

@bot.command()
async def customDisplay(ctx : Context, activity: str = parameter(description="courte description de l'activité", default=None), status: str=parameter(description="status du bot", default=None)):
    """Change the bot's custom activity and status\nusage: customDisplay <activity> <[online|idle|dnd|offline]>"""
    #check if the user is allowed to use this command
    print(activity if activity else "None", status if status else "None")
    if activity and status in ["online", "idle", "dnd", "offline"]:
        if [role for role in [role.id for role in ctx.author.roles] if role in conf["allowed_roles"]]: #type:ignore
            print("yes")
            await bot.overrideDisplay(Game(activity), Status(status))
    else:
        await ctx.channel.send("usage: customDisplay <activity> <[online|idle|dnd|offline]>")

@bot.command()
async def stopCustomDisplay(ctx : Context, arg1=None):
    """stop the bot's custom activity"""
    if not arg1:
        if [role for role in [role.id for role in ctx.author.roles] if role in conf["allowed_roles"]]: #type:ignore
            bot.override = False
            await bot.updatePresence()
    else:
        await ctx.channel.send("usage : stopCustomDisplay")

async def isOpen(ctx : Context, arg1=None):
    """know if the button is on"""
    if not arg1:
        await ctx.channel.send(bot.doorStatus.name)

@bot.event
async def on_ready():
    print("ready")
    bot.checkButton.start()

bot.run(conf["bot_token"])