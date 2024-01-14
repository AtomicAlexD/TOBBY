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
from database.rate_my_db_calls import db_read, db_write

class rate_my(commands.Cog, name="rate_my"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db_write = db_write()
        self.db_read = db_read()

    @commands.hybrid_group(
            name="rate_my",
            description="A group of commands to rate things.",
            )
    async def rate_my(self, context: Context) -> None:
        """
        A group of commands to rate things.

        :param context: The application command context.
        """
        
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description='Please specify a subcommand.',
                color=0xE02B2B,
            )
            await context.send(embed=embed)

    @rate_my.command(
        name="new_category",
        description="adds a new category of things to rate.",
    )
    @app_commands.describe(
        name="The name of the new category.",
        description="brief description of the category.",
    )
    async def add_category_to_database(self, context: Context, name , description = 'none') -> None:
        """
        Adds a new category of things to rate to the database

        :param context: The application command context.
        """
        try:
            guild_id = context.guild.id
            run = self.db_write.add_category(guild_id, name, description)
        #db_write.add_category(self=self, guild_id = context.guild.id, category_name = name, category_description = description)
        
            embed = discord.Embed(description=f'Category {run} added', color=0x93C47D)
            await context.send(embed=embed)
        except Exception as e:
            print(e)
            embed = discord.Embed(description='Something went wrong', color=0xE02B2B)
            await context.send(embed=embed)

    @rate_my.command(
        name="see_categories",
        description="lists all categories.",
    )
    async def see_categories(self, context: Context) -> None:
        """
        Lists all categories

        :param context: The application command context.
        """
        guild_id = context.guild.id
        categories = self.db_read.get_categories(guild_id)
        
        embed = discord.Embed(
            title="Categories",
            description="",
            color=0x93C47D,
        )
        for category_name, category_description in categories:
            embed.add_field(
                name=f"{category_name}",
                value=f"{category_description}",
                inline=False,
            )
        await context.send(embed=embed)

    @rate_my.command(
        name="new_item",
        description="adds a new item to rate.",
    )
    async def add_item_to_database(self, context: Context) -> None:
        """
        Adds a new item to rate to the database

        :param context: The application command context.
        """
        
        db_write.add_item_to_rate(context.guild.id, context.args)
        
        await context.send("Item added!")
    
    @rate_my.command(
        name="thing",
        description="rates an item.",
    )
    async def rate_item(self, context: Context) -> None:
        """
        Rates an item

        :param context: The application command context.
        """
        
        db_write.rate_item(context.guild.id, context.author.id, context.args)
        
        await context.send("Item rated!")

    
# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(rate_my(bot))
