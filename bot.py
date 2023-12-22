import os
import random 
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guild(s):')
    for guild in bot.guilds:
        print(
            f'{guild.name} - id: {guild.id}'
        )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@bot.command(name='parrot', help='make Tobby copy what you say')
async def parrot(context):
    message = context.message
    reply = message.content[8:]
    await context.send(reply)

@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(context):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        'Cool. Cool cool cool cool cool cool cool, no doubt no doubt no doubt no doubt.',
        'NINE NINE!'
    ]
    response = random.choice(brooklyn_99_quotes)
    await context.send(response)

@bot.command(name='happy_birthday', help='Send a happy birthday message')
async def happy_birthday(context):
    await context.send('Happy Birthday! 🎈🎉')

@bot.command(name='rate', help='Rate todays drink')
async def rate(context):
    await context.send('sending you a DM')
    dm_channel = await context.author.create_dm()
    await dm_channel.send('How do you rate {insert drink here}?')

@bot.command(name='beer_me', help='Get todays drink')
async def beer_me(context):
    await context.send('Todays Drink is {insert drink here}')

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(context, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await context.send(', '.join(dice))

@bot.event
async def on_command_error(context, error):
    if isinstance(error, commands.CommandNotFound):
        await context.send('I do not recognize that command. Please try again, or use !help for a list of commands')

bot.run(TOKEN)