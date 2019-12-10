import os
import discord
from dotenv import load_dotenv

from discord.ext import commands

import market

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
COMMAND_PREFIX = '-'

bot= commands.Bot(command_prefix=COMMAND_PREFIX, description='Discord bot intended for use with the PSS Express fleet Discord')

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user.name} is connected to the following guild: \n'
        f'{guild.name}(id: {guild.id})')

@bot.command(name='test', help='Used for bot testing purposes.')
async def tester_command(ctx):
    response = 'Master, I am functioning as you intended.'
    await ctx.send(response)

@bot.command(name='minswaps', help='Pulls all mineral crates worth 497k off market')
async def swap_finder(ctx):
    data = market.pull_min_swaps()
    await ctx.send(data)


bot.run(TOKEN)

