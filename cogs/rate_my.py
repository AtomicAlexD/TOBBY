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
from datetime import datetime

class rate_my(commands.Cog, name="rate_my"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db_write = db_write()
        self.db_read = db_read()

    @commands.hybrid_group(
            name="rate",
            description="A group of commands to rate things.",
            )
    async def rate_my(self, context: Context) -> None:
        """
        A group of commands to rate things.

        :param context: The application command context.
        """
        # if no sub command, default to rate_item
        if context.sub_command_passed is None:
            await self.rate_item(context)
        else:
            await context.send_help(context.command)

    @rate_my.command(
        name="new_category",
        description="adds a new category of things to rate.",
    )
    @app_commands.describe(
        name="The name of the new category.",
        description="description of the category.",
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
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
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
    @app_commands.describe(
        name = 'the name of the thing to rate.',
        category_name="The name of the category the thing belongs to.",
        description="description of the thing.",
        available_to_rate_date="date the thing is available to rate.",
    )
    async def add_item_to_database(self, context: Context, name, category_name, description = 'None Given',available_to_rate_date = None) -> None:
        """
        Adds a new item to rate to the database
        :param context: The application command context.
        """
        if available_to_rate_date == None:
            now = datetime.now()
            available_to_rate_date = now.strftime("%Y-%m-%d %H:%M:%S")
        guild_id = str(context.guild.id)
        confirmation = self.db_write.add_item_to_rate(guild_id, name, category_name, description, available_to_rate_date)
        if confirmation == 'no category found':
            embed = discord.Embed(description='Error in finding the category', color=0xE02B2B)
            await context.send(embed=embed)
        elif confirmation == 'could not add item to rate':
            embed = discord.Embed(description='Error in adding item to rate', color=0xE02B2B)
            await context.send(embed=embed)
        elif confirmation == 'item added to rate':
            embed = discord.Embed(description=f'Item {name} added to {category_name}', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(description='Im not sure what just happened... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
    
    @rate_my.command(
        name="what_can_i_rate",
        description="lists all items available to rate.",
    )
    async def what_can_i_rate(self, context: Context) -> None:
        user_id = context.author.id
        guild_id = context.guild.id
        items = self.db_read.get_items_to_rate(user_id, guild_id)
        if items == 'error':
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
        elif items == []:
            embed = discord.Embed(description='No items available to rate, if you want to update a rating use update_rating', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Items available to rate",
                description="",
                color=0x93C47D,
            )
            for item_name, category_name, description, item_id in items:
                embed.add_field(
                    name=f"{item_name}",
                    value=f"""Category: {category_name}
Description: {description}
If you want to rate this item, use the command /rate rate_item {item_name} with your rating (0-10)""",
                    inline=False,
                )
            await context.send(embed=embed)

    @rate_my.command(
        name="rate_item",
        description="rates an item.",
    )
    @app_commands.describe(
        rating = 'the rating to give the item (0-10), decimals will be rounded down',
        item_name = 'the name of the item to rate.(use /rate what_can_i_rate to see available items)',
    )
    async def rate_item(self, context: Context, rating, item_name=None) -> None:
        """
        Rates an item

        :param context: The application command context.
        """
        user_id = context.author.id
        guild_id = context.guild.id
        rating = int(rating)
        if item_name == None:
            #grab most recently available item in the guild 
            item_name = self.db_read.get_most_recent_item(guild_id)
        # check user hasnt already rated this item 
        if self.db_read.check_user_has_rated_item(guild_id, user_id, item_name) == True:
            embed = discord.Embed(description='You have already rated this item, use update instead', color=0xE02B2B)
            await context.send(embed=embed)
            return
        if rating < 0 or rating > 10:
            embed = discord.Embed(description='Rating must be between 0 and 10', color=0xE02B2B)
            await context.send(embed=embed)
            return
        confirmation = self.db_write.rate_item(guild_id, user_id, item_name, rating)
        if confirmation == 'could not add rating':
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
        elif confirmation == 'rating added':
            embed = discord.Embed(description=f'Item {item_name} rated {rating}', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(description='Im not sure what just happened... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)

    @rate_my.command(
        name="view_my_ratings",
        description="lists all items you have rated.",
    )
    async def view_my_ratings(self, context: Context) -> None:
        user_id = context.author.id
        guild_id = context.guild.id
        items = self.db_read.view_my_ratings(user_id, guild_id)
        if items == 'error':
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
        elif items == []:
            embed = discord.Embed(description='No items rated', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Items you have rated",
                description="",
                color=0x93C47D,
            )
            for item_name, category_name, description, rating in items:
                embed.add_field(
                    name=f"{item_name}",
                    value=f"""Category: {category_name}
Description: {description}
Rating: {rating}""",
                    inline=False,
                )
            await context.send(embed=embed)

    @rate_my.command(
        name="update_rating",
        description="updates a rating.",
    )
    @app_commands.describe(
        item_name = 'the id of the item to update.(use /rate view_my_ratings to see available items)',
        rating = 'the rating to give the item (0-10), decimals will be rounded down',
    )
    async def update_rating(self, context: Context, item_name, rating) -> None:
        """
        Updates a rating

        :param context: The application command context.
        """
        user_id = context.author.id
        guild_id = context.guild.id
        rating = int(rating)
        if rating < 0 or rating > 10:
            await context.send("Rating must be between 0 and 10")
            return
        confirmation = self.db_write.update_rating(guild_id, user_id, item_name, rating)
        if confirmation == 'could not update rating':
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
        elif confirmation == 'rating updated':
            embed = discord.Embed(description=f'Item {item_name} updated to {rating}', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(description='Im not sure what just happened... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)

    @rate_my.command(
        name="view_ratings",
        description="lists all ratings for an item.",
    )
    @app_commands.describe(
        item_name = 'the name of the item to view.(use /rate view_my_ratings to see available items)',
    )
    async def view_ratings(self, context: Context, item_name) -> None:
        guild_id = context.guild.id
        items = self.db_read.view_ratings(guild_id, item_name)
        if items == 'could not get ratings':
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
        elif items == []:
            embed = discord.Embed(description='No items rated', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Ratings for {items[0][0]}",
                description="",
                color=0x93C47D,
            )
            for w,rating, user_id in items:
                user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(
                int(user_id)
            )
                #change this to user / rating
                embed.add_field(name=f'{user}:',
                                value=rating,
                                inline=False
                                )
            await context.send(embed=embed)

    @rate_my.command(
        name="view_items_by_category",
        description="lists all items in a category.",
    )
    @app_commands.describe(
        category_name = 'the name of the category to view.(use /rate see_categories to see available categories)',
    )
    async def view_items_by_category(self, context: Context, category_name) -> None:
        guild_id = context.guild.id
        items = self.db_read.view_items_by_category(guild_id, category_name)
        if items == 'could not get items':
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
        elif items == []:
            embed = discord.Embed(description='No items found', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Items in {category_name}",
                description="",
                color=0x93C47D,
            )
            for item_name, description,available_date , rating in items:
                embed.add_field(
                    name=f"{item_name}",
                    value=f"""Description: {description}
Available to rate: {available_date}
Average Rating: {rating}""",
                    inline=False,
                )
            await context.send(embed=embed)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(rate_my(bot))


# name="view_ratings_by_user",