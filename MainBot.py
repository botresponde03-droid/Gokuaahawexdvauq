import discord
import os
import json
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', description="Oh baby...", intents=intents)

discord_token = os.getenv('DISCORD_TOKEN')

configFile = "config.json"
if os.path.isfile("config.json"):
    file = open("config.json")
    conf = json.load(file)
    discord_token = discord_token or conf.get("discord_token")
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
async def play(ctx, word: str = None):
    if word:
        await bot.change_presence(activity=discord.Game(name=word))
    else:
        await ctx.send("Usage: .play <game_name>")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

async def setup_hook():
    try:
        await bot.load_extension("PornHub")
    except Exception as e:
        print(f"Failed to load PornHub extension: {e}")

bot.setup_hook = setup_hook

if discord_token:
    bot.run(discord_token)
else:
    print("ERROR: DISCORD_TOKEN environment variable not set!")

