#!/usr/bin/python3

import os
import discord
import typing
from dotenv import load_dotenv

from discord.ext import commands

import market
import utility

# =========== SETUP ===========================================================

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
COMMAND_PREFIX = '-'

bot= commands.Bot(command_prefix=COMMAND_PREFIX, description='Discord bot intended for use with the PSS Express fleet Discord')

# =========== END SETUP =======================================================

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

@bot.command(name = 'xmas_role', help='Add role to let you write christmas story')
async def add_xmas_role(ctx):
    user = ctx.message.author
    role = discord.utils.get(user.guild.roles, name="Christmas Story Writer")
    await user.add_roles(role)
    await ctx.send(f'{user} may now write in the xmas story channel.')


class PSS(commands.Cog, name = 'PSS Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='minswaps', help='Pulls all crates worth 497k off market')
    @commands.has_any_role('Planet·Express', 'Awesome·Express')
    async def swap_finder(self, ctx):
        data = market.pull_min_swaps()
        await ctx.send(f'```{data}```')

    @commands.command(name='engine', help='Calculates engine dodge rate. ')
    async def eng_dodge(self, ctx, e_lvl : int = 10, e_stat : float = 0.0):
        await ctx.send(f'Engine Lv{e_lvl} with {e_stat} ENG stat: {utility.dodge_rate(e_lvl, e_stat)}% dodge rate')

    @commands.command(name='allwpns', help='Lists all weapon strings for use with dps function')
    async def list_all_wpnstrings(self, ctx):
        await ctx.send(f'```{utility.allwpns()}```')

    @commands.command(name='dps', help='Gets DPS for a weapon, see -help dps for wpn lvl, room stat & power options.')
    async def dps_calculator(self, ctx, wpn_string, stat : float = 0.0, power : int = 'MAX'): # TODO: Add a way to allow arguments to be passed via command in any order(*args?)
        await ctx.send(utility.dps(wpn_string = wpn_string, wpn_stat=stat , power=power))

    @commands.command(name='tax', help='Determines the amount of tax when you sell an item for a certain price. ')
    async def tax_calculator(self, ctx, sell_price : int):
        if sell_price == 1:
            amount = 1
        else:
            amount = utility.truncate(sell_price*0.8)

        await ctx.send(f'After tax: {amount}')


class Fun(commands.Cog, name = 'Fun Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll', help=f'Roll a 6-sided dice. To customise: {COMMAND_PREFIX}roll 3d8')
    async def roller(self, ctx, dice_arg: typing.Optional[str] = '1d6'):
        dice_arg = dice_arg.lower()
        dice_values = dice_arg.split('d')
        n = int(dice_values[0])
        d = int(dice_values[1])
        if n > 100000 or d > 100000:
            await ctx.send('I would rather die than roll that many dice for you.')
        rolls = utility.roll(n, d)
        await ctx.send(f'__You rolled {n} {d}-sided dice.__ Results:\n' + f'`{str(rolls)[1:-1]}`')

    @commands.command(name='binary', help='Convert an integer into its binary representation')
    async def int_to_bin(self, ctx, n: int):
        await ctx.send(f'{n} in binary is __{bin(n)[2:]}__.')


if __name__ == "__main__":
    bot.add_cog(PSS(bot))
    bot.add_cog(Fun(bot))
    bot.run(TOKEN)
