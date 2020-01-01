#!/usr/bin/python3

import os
import discord
import typing
from dotenv import load_dotenv

from discord.ext import commands

import bank
import market
import utility

# =========== SETUP ===========================================================

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
COMMAND_PREFIX = '-'
ADMIN_ROLE = 'Administrator'


cmd_rate = 20
cmd_per = 10

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
    response = f'Master {ctx.author}, I am functioning as you intended.'
    await ctx.send(response)


class PSS(commands.Cog, name = 'PSS Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='minswaps', help='Pulls all crates worth 497k off market', aliases=['ms'])
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


class Bank(commands.Cog, name = 'Bank Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='bank', invoke_without_command=True, help='Various commands involving the Express fleet rewards bank')
    async def bank(self, ctx):
        await ctx.send(f"Base bank command. Use {COMMAND_PREFIX}help bank to see subcommands.")

    @bank.command(name='new', help='Create new bank account with a set balance')
    @commands.has_role(ADMIN_ROLE)
    async def bankaccount_update(self, ctx, acc_name: str, acc_balance: int):
        result = bank.bank_update_account(acc_name, acc_balance)
        await ctx.send(result)

    @bank.command(name='add', help='Add/subtract an amount from a bank account')
    @commands.has_role(ADMIN_ROLE)
    async def bank_account_add(self, ctx, acc_name: str, amount: int):
        if bank.bank_inc_balance(acc_name, amount):
            if amount < 0:
                await ctx.send(f'{acc_name}\'s balance decreased by {-amount}.')
            else:
                await ctx.send(f'{acc_name}\'s balance increased by {amount}.')
        else:
            await ctx.send('Account modification failed.')
                

    @bank.command(name = 'wallet', help='Check your bank balance')
    async def bank_check(self, ctx):
        author = str(ctx.author)
        balance = bank.bank_check_balance(author)
        if balance:
            await ctx.send(f'{ctx.author}, your balance is {balance}.')
        else:
            await ctx.send('This account doesn\'t exist')

    @bank.command(name='all', help='Show all bank accounts')
    async def bank_showall(self, ctx):
        accounts = bank.bank_all_accounts()
        await ctx.send(accounts)

    @bank.command(name='delete', help='Deletes a bank account')
    @commands.has_role(ADMIN_ROLE)
    async def bank_delete(self, ctx, acc_name: str):
        if bank.bank_delete_account(acc_name):
            await ctx.send(f'{acc_name}\'s bank account deleted successfully.')
        else:
            await ctx.send('Could not delete that account.')

class Fun(commands.Cog, name = 'Fun Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Triggers on error within cog"""

        # Prevent local handled commands from being handled here
        if hasattr(ctx.command, 'on_error'):
            return
    
        ignored = (commands.CommandNotFound, commands.UserInputError) # Already handled
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(error)


    @commands.command(name='roll', help=f'Roll a 6-sided dice. To customise: {COMMAND_PREFIX}roll 3d8')
    @commands.cooldown(rate=cmd_rate, per=cmd_per, type=commands.BucketType.member)
    async def roller(self, ctx, dice_arg: typing.Optional[str] = '1d6'):
        dice_arg = dice_arg.lower()
        dice_values = dice_arg.split('d')
        n = int(dice_values[0])
        d = int(dice_values[1])
        if n < 1000 and d < 1000000:
            rolls = utility.roll(n, d)
            await ctx.send(f'__You rolled {n} {d}-sided dice.__ Results:\n' + f'`{str(rolls)[1:-1]}`')
        else:
            await ctx.send('I would rather die than roll that many dice for you.')
        

    @commands.command(name='binary', help='Convert an integer into its binary representation')
    async def int_to_bin(self, ctx, n: int):
        await ctx.send(f'{n} in binary is __{bin(n)[2:]}__.')

    @commands.command(name='define', help='Returns definition for a word')
    async def define_word(self, ctx, word):
        result = utility.dict_api(word)
        await ctx.send(result)

if __name__ == "__main__":
    bot.add_cog(PSS(bot))
    bot.add_cog(Fun(bot))
    bot.add_cog(Bank(bot))
    bot.run(TOKEN)
