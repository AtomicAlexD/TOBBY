""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class poll(commands.Cog, name="poll"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="poll",
        description="adds a new poll",
    )
    @app_commands.describe(
        question="The name of the new poll.",
        options="all options for the new poll separated by commas.",
    )
    async def poll(self, context: Context, question, options: str):
        options = options.split(',')
        if len(options) <= 1:
            embed = discord.Embed(title='Error!', description='You need more than one option to make a poll!', color=0xE02B2B)
            await context.send(embed=embed)
            return
        if len(options) > 10:
            embed = discord.Embed(title='Error!', description='You cannot make a poll for more than 10 things!', color=0xE02B2B)
            await context.send(embed=embed)
            return
        
        if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
            reactions = ['✅', '❌']
        else:
            reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

        description = []
        for x, option in enumerate(options):
            description += '\n {} {}'.format(reactions[x], option)
        embed = discord.Embed(title=question, description=''.join(description))
        react_message = await context.send(embed=embed)
        for reaction in reactions[:len(options)]:
            await react_message.add_reaction(reaction)
        embed.set_footer(text='Poll ID: {}'.format(react_message.id))
        await react_message.edit(embed=embed)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(poll(bot))
