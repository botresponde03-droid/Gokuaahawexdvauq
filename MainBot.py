import discord
import os
import json
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', description="Oh baby...", intents=intents)

configFile = "config.json"
if os.path.isfile("config.json"):
    file = open("config.json")
    conf = json.load(file)
    discord_token = conf["discord_token"]
else:
    print("RIP no config")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def stop(ctx):
    print('------')
    print('Logging out')
    await bot.close()

@bot.command()
async def play(ctx, word:str=None):
    await bot.change_presence(activity=discord.Game(name=word))

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.event
async def on_message(message):   
    await bot.process_commands(message)

# Load cogs here
async def setup_hook():
    await bot.load_extension("PornHub")

bot.setup_hook = setup_hook

bot.run(discord_token)