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

    @rate_my.command(
        name="new_category",
        description="adds a new category of things to rate, with a default overall metric.",
    )
    @app_commands.describe(
        name="The name of the new category.",
        description="description of the category.",
        metrics="the metrics to rate the category with, seperated by a comma. (default is overall and will always be added)",
    )
    async def add_category_to_database(self, context: Context, name , description = None, metrics:str=None) -> None:
        """
        Adds a new category of things to rate to the database

        :param context: The application command context.
        """
        try:
            guild_id = context.guild.id
            category, metric, category_id = self.db_write.add_category(guild_id, name, description)
            embed = discord.Embed(description=f'Category: {category} added, with {metric} metric', color=0x93C47D)
            await context.send(embed=embed)
        except Exception as e:
            print(e)
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
        if metrics != None:
            metrics = metrics.split(',')
            for metric in metrics:
                try:
                    self.db_write.add_metric(category_id=category_id, metric_name=metric, metric_description=metric)
                    embed = discord.Embed(description=f'Metric: {metric} added to {category}', color=0x93C47D)
                except Exception as e:
                    print(e)
                    embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
                    await context.send(embed=embed)

    @rate_my.command(
        name="see_metrics",
        description="lists all metrics for a category.",
    )
    @app_commands.describe(
        category_name="The name of the category to see metrics for.",
    )
    async def see_metrics(self, context: Context, category_name) -> None:
        """
        Lists all metrics for a category

        :param context: The application command context.
        """
        guild_id = context.guild.id
        metrics = self.db_read.get_metrics(guild_id, category_name)
        if metrics == 'no category found':
            embed = discord.Embed(description='Error in finding the category', color=0xE02B2B)
            await context.send(embed=embed)
        elif metrics == 'no metrics found':
            embed = discord.Embed(description='No metrics found', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Metrics for {category_name}",
                description="",
                color=0x93C47D,
            )
            for metric_name, metric_description, id in metrics:
                embed.add_field(
                    name=f"{metric_name}",
                    value=f"{metric_description}",
                    inline=False,
                )
            await context.send(embed=embed)

    @rate_my.command(
        name="new_metric",
        description="adds a new metric to a category.",
    )
    @app_commands.describe(
        category_name="The name of the category to add a metric to.",
        metric_name="The name of the new metric.",
        metric_description="description of the metric.",
    )
    async def add_metric_to_database(self, context: Context, category_name, metric_name, metric_description = None) -> None:
        """
        Adds a new metric to a category

        :param context: The application command context.
        """
        guild_id = context.guild.id
        category_id = self.db_read.get_category_id(guild_id, category_name)
        if category_id == 'could not get category id':
            embed = discord.Embed(description='Error in finding the category', color=0xE02B2B)
            await context.send(embed=embed)
        confirmation = self.db_write.add_metric(category_id, metric_name, metric_description)
        if confirmation == 'could not add metric':
            embed = discord.Embed(description='Error in adding metric', color=0xE02B2B)
            await context.send(embed=embed)
        elif confirmation == metric_name:
            embed = discord.Embed(description=f'Metric: {metric_name} added to {category_name}', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(description='Im not sure what just happened... Blame Alex', color=0xE02B2B)
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
        if categories == None:
            embed = discord.Embed(description='Error in finding the categories', color=0xE02B2B)
            await context.send(embed=embed)
        elif categories == []:
            embed = discord.Embed(description='No categories have been added in this guild', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Categories",
                description="",
                color=0x93C47D,
            )
            for category_name, category_description, metric_count in categories:
                embed.add_field(
                    name=f"{category_name}",
                    value=f"""Description: {category_description}
Count of Metrics: {metric_count}""",
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
If you want to rate this item, use the command /rate item {item_name}""",
                    inline=False,
                )
            await context.send(embed=embed)

    @rate_my.command(
        name="item",
        description="rates an item.",
    )
    @app_commands.describe(
        item_name = 'the name of the item to rate.(use /rate what_can_i_rate to see available items)',
    )
    async def rate_item(self, context: Context, item_name=None) -> None:
        """
        Start a DM with the user to rate each metric for an item
        """
        user_id = context.author.id
        guild_id = context.guild.id
        if item_name == None:
            #grab most recently available item in the guild 
            item_name = self.db_read.get_most_recent_item(guild_id)
        category_id = self.db_read.get_category_id_of_item(guild_id, item_name)
        # check user hasnt already rated this item 
        metrics = self.db_read.get_metrics_for_item(guild_id, category_id)
        if metrics == 'could not get metrics':
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
            return
        user_ratings = self.db_read.get_user_ratings_for_item(guild_id, user_id, item_name)
        if len(metrics) == len(user_ratings):
            embed = discord.Embed(description='You have already rated this item, use update instead', color=0xE02B2B)
            await context.send(embed=embed)
            return
        embed = discord.Embed(description='Lets take this some place more private...', color=0x93C47D)
        await context.send(embed=embed)
        #start dm with user
        dm_channel = await context.author.create_dm()
        embed = discord.Embed(description=f'The following messages are for **{item_name}**', color=0x93C47D)
        await dm_channel.send(embed=embed)
        rated_metrics = set(rating[0] for rating in user_ratings) if user_ratings else set()
        for metric_name, metric_description, metric_id in metrics:
            while True:
                # send dm to user
                embed = discord.Embed(description=f'Please rate **{metric_name}** on a scale of 0 to 10', color=0x93C47D)
                embed.add_field(
                    name=f"Description:",
                    value=f"{metric_description}",
                    inline=False,
                )
                await dm_channel.send(embed=embed)
                # wait for user to respond
                def check(m):
                    return m.author == context.author and m.channel == dm_channel and m.content.isdigit() and 0 <= int(m.content) <= 10
                msg = await self.bot.wait_for('message', check=check)
                rating = int(msg.content)
                break
            confirmation = self.db_write.rate_item(guild_id, user_id, item_name, rating, metric_name)
            if confirmation == 'could not add rating':
                embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
                await dm_channel.send(embed=embed)
            elif confirmation == 'rating added':
                embed = discord.Embed(description=f'Item {item_name}: {metric_name} rated {rating}', color=0x93C47D)
                await dm_channel.send(embed=embed)
            else:
                embed = discord.Embed(description='Im not sure what just happened... Blame Alex', color=0xE02B2B)
                await dm_channel.send(embed=embed)
        embed = discord.Embed(description=f'All metrics for **{item_name}** rated', color=0x93C47D)
        await dm_channel.send(embed=embed)
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
AVG Rating across metrics: {rating}""",
                    inline=False,
                )
            await context.send(embed=embed)


    @rate_my.command(
        name="update",
        description="Starts a dm chat so you can update a rating of an item.",
    )
    @app_commands.describe(
        item_name = 'the name of the item to update.(use /rate view_my_ratings to see available items)',
    )
    async def update_rating(self, context: Context, item_name=None) -> None:
        """
        Start a DM with the user to rate each metric for an item
        """
        user_id = context.author.id
        guild_id = context.guild.id
        if item_name == None:
            #grab most recently available item in the guild 
            item_name = self.db_read.get_most_recent_item(guild_id)
        category_id = self.db_read.get_category_id_of_item(guild_id, item_name)
        metrics = self.db_read.get_metrics_for_item(guild_id, category_id)
        if metrics == 'could not get metrics':
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
            return
        user_ratings = self.db_read.get_user_ratings_for_item(guild_id, user_id, item_name)
        if len(user_ratings) == 0:
            embed = discord.Embed(description='You have not rated this item yet, use /rate item instead', color=0xE02B2B)
            await context.send(embed=embed)
            return
        embed = discord.Embed(description='Lets take this some place more private...', color=0x93C47D)
        await context.send(embed=embed)
        #start dm with user
        dm_channel = await context.author.create_dm()
        embed = discord.Embed(description=f'The following messages are for **{item_name}**', color=0x93C47D)
        await dm_channel.send(embed=embed)
        rated_metrics = set(rating[0] for rating in user_ratings) if user_ratings else set()
        for metric_name, metric_description, metric_id in metrics:
            while True:
                # send dm to user
                embed = discord.Embed(description=f'Please rate **{metric_name}** on a scale of 0 to 10', color=0x93C47D)
                embed.add_field(
                    name=f"Description:",
                    value=f"{metric_description}",
                    inline=False,
                )
                await dm_channel.send(embed=embed)
                # wait for user to respond
                def check(m):
                    return m.author == context.author and m.channel == dm_channel and m.content.isdigit() and 0 <= int(m.content) <= 10
                msg = await self.bot.wait_for('message', check=check)
                rating = int(msg.content)
                break
            confirmation = self.db_write.update_item_rating(guild_id, user_id, item_name, rating, metric_name) #TODO: make db call
            if confirmation == 'could not update rating':
                embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
                await dm_channel.send(embed=embed)
            elif confirmation == 'rating updated':
                embed = discord.Embed(description=f'Item {item_name}: {metric_name} rated {rating}', color=0x93C47D)
                await dm_channel.send(embed=embed)
            else:
                embed = discord.Embed(description='Im not sure what just happened... Blame Alex', color=0xE02B2B)
                await dm_channel.send(embed=embed)
        embed = discord.Embed(description=f'All metrics for **{item_name}** rated', color=0x93C47D)
        await dm_channel.send(embed=embed)
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
                title=f"Ratings for {item_name}",
                description="Average rating per metric",
                color=0x93C47D,
            )
            for metric, rating in items:
                embed.add_field(name=f'{metric}:',
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

    @rate_my.command(
        name="change_available_date",
        description="changes the date an item is available to rate.",
    )
    @app_commands.describe(
        item_name = 'the name of the item to change.(use /rate view_items_by_category see available items)',
        available_date = 'the date the item is available to rate, in the format YYYY-MM-DD',
    )
    async def change_available_date(self, context: Context, item_name, available_date) -> None:
        guild_id = context.guild.id
        confirmation = self.db_write.change_available_date(guild_id, item_name, available_date)
        if confirmation == 'could not change available date':
            embed = discord.Embed(description='Something went wrong... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)
        elif confirmation == 'available date changed':
            embed = discord.Embed(description=f'Item {item_name} available date changed to {available_date}', color=0x93C47D)
            await context.send(embed=embed)
        else:
            embed = discord.Embed(description='Im not sure what just happened... Blame Alex', color=0xE02B2B)
            await context.send(embed=embed)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(rate_my(bot))


# name="view_ratings_by_user",