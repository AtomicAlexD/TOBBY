import os
import random 
import discord

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = 'The Test Of Brewdog Boys Interactive'

intents = discord.Intents().all()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_message(message):
    # print(f'guild: {message.guild}')
    # print(f'channel: {message.channel}')
    # print(f'author: {message.author}')
    # print(f'content: {message.content}')

    if message.author == client.user:
        return

    if message.guild is None:  # This means it's a DM
        print(f'DM received: {message.content}')
        # Here you can add your code to handle the DM
        reply = 'I have received your DM message. im currently doing nothing with it'
        await message.author.send(reply)
        return

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    if message.content.startswith('!'):
        if message.content == '!99':
            response = random.choice(brooklyn_99_quotes)
            await message.channel.send(response)
        
        elif 'happy birthday' in message.content.lower():
            await message.channel.send('Happy Birthday! 🎈🎉')
        
        elif 'rate' in message.content.lower():
            await message.channel.send('Todays Drink is {insert drink here}')
            await message.channel.send('sending you a DM')
            dm_channel = await message.author.create_dm()  # Create a DM channel
            await dm_channel.send('How do you rate {inser drink here?}')  # Send a message

        elif 'help' in message.content.lower():
            await message.channel.send('I can do the following commands:')
            await message.channel.send('!99 - get a random quote from Brooklyn 99')
            await message.channel.send('Happy Birthday - wish someone a happy birthday')
            await message.channel.send('rate - rate todays drink')
        
        else:
            await message.channel.send('Sorry I don\'t understand that command, try !help')

client.run(TOKEN)