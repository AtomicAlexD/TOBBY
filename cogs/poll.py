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
from database.poll_db_calls import db_read, db_write
from datetime import datetime, timedelta


class poll(commands.Cog, name="poll"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db_write = db_write()
        self.db_read = db_read()

    @commands.hybrid_group(
        name="poll",
        description="A group of commands to set up and vote on things.",
    )
    async def poll(self, context: Context) -> None:
        """
        A group of commands to rate things.

        :param context: The application command context.
        """

        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Please specify a subcommand.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)

    @poll.command(
        name="new_poll",
        description="adds a new poll, can specify start and end times for voting.",
    )
    @app_commands.describe(
        name="The name of the new poll.",
        options="all options for the new poll separated by commas.",
        start_time="The time the poll should start.(defaults to now)",
        end_time="The time the poll should end.(defaults to 24 hours from now)",
    )
    async def add_new_poll_with_options(
        self,
        context: Context,
        name,
        options=["none"],
        start_time=datetime.now,
        end_time=datetime.now + timedelta(hours=24),
    ) -> None:
        """ """
        try:
            guild_id = context.guild.id
            add_poll = self.db_write.add_poll(guild_id, name,start_time,end_time)  # returns poll_id
            if add_poll is None:
                embed = discord.Embed(
                    description="Could'nt create Poll... Blame Alex", color=0xE02B2B
                )
                await context.send(embed=embed)
            else:
                try:
                    poll_id = add_poll
                    for option in options:
                        self.db_write.add_option_to_poll(poll_id, option)
                except Exception as e:
                    print(e)
                    embed = discord.Embed(
                        description="Couldn't add options to poll... Blame Alex", color=0xE02B2B
                    )
                    await context.send(embed=embed)
                embed = discord.Embed(description=f"Poll {name} added", color=0x93C47D)
                await context.send(embed=embed)
        except Exception as e:
            print(e)
            embed = discord.Embed(
                description="Something went wrong... Blame Alex", color=0xE02B2B
            )
            await context.send(embed=embed)



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(poll(bot))


# name="view_ratings_by_user",
