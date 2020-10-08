# Import Modules
import discord
import envariables
import logging
from xml.etree import ElementTree
import aiohttp
import asyncio
from random import choice

# TODO: Create File to Store Previously Asked Questions and Pull from them Instead of Constantly Accessing Wolfram API (and taking up all my fuckin queries)

# Logs Discord DEBUG Logs to discord.log
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Accesses Discord Client
client = discord.Client()

# Initializes Tokens and API Keys from envariables
discordToken = envariables.discordToken
wolframToken = envariables.wolframToken

# Regular Variables
adminCommands = ['admin', 'admin help', 'admin servers']


# Informs of Bot Connection Information on Ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name='Q? help'))
    await client.get_channel(762093041116381198).send('Bot Enabled.')


# Detects Message Send Events
# TODO: Make Bot Only Search Messages with Prefix "Q? " Instead of all Messages
@client.event
async def on_message(message):
    # Ignores all Messages Sent by Bot
    if message.author == client.user:
        return

    # Only Parses Message If Proceeded with Prefix
    if message.content.startswith('Q? '):
        messageContent = message.content[3:]

        # Regular Commands
        title = f'{str(message.author)} asked, "{messageContent}"'
        answer = await message.channel.send(
            embed=discord.Embed(title=title,
                                description="Answering...",
                                color=0xffff00))  # Yellow
        color = 0x00ff00  # Green

        # Admin Commands
        # All Admin Commands Require You to Define a "command" and "description" Variable for Embed
        if messageContent in adminCommands:
            if message.author.id == 330116875755323393:
                if messageContent in ['admin', 'admin help']:
                    command = 'Help'
                    description = "Q? admin servers - Lists Servers Bot is In\nQ? admin change_presence <input> - Changes Rich Presence of Bot"

                elif messageContent == 'admin servers':
                    command = 'Servers'
                    description = f'In {len(client.guilds)} servers:'
                    for server in client.guilds:
                        description += f'\n{server.name}'
                        
                elif messageContent == 'admin change_presence':
                    command = 'Change Presence'
                    description = f'Changing Presence to "{messageContent[22:]}"...'
                    await client.change_presence(activity=discord.Game(name=messageContent[22:]))

            title = f'Admin Command "**{command}**" Triggered'
            color = 0xb500b5  # Purple

        # Predefined Question Responses
        elif messageContent.lower().startswith('help'):
            description = 'Ask me any question and I\'ll do my best to answer it!'

        # Sends Message to Wolfram API and Returns Result as Embed
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://api.wolframalpha.com/v2/query?input={messageContent.replace("+", "plus")}&appid={wolframToken}') as response:
                        # TODO: Change WolframAlpha Output Data Type from XML to JSON
                        tree = ElementTree.fromstring(await response.content.read())
                        # ? Should I Keep the Special Orange Empty Message Embed or Defaut to the Red One?
                        if tree[1][0].find('plaintext').text not in [None, '']:
                            # Predefined Answer Responses
                            if tree[1][0].find('plaintext').text == 'My name is Wolfram|Alpha.':
                                description = f'My name is {client.user}'
                            else:
                                description = tree[1][0].find('plaintext').text

                        else:
                            # Empty or Missing Answer
                            description = '¯\_(ツ)_/¯'
                            color = 0xff8000  # Orange

            # Returns if Answer Cannot be Found
            except IndexError:
                description = '¯\_(ツ)_/¯'
                color = 0xff0000  # Red

        # Applies title, description, and color Changes
        await answer.edit(
            embed=discord.Embed(title=title,
                                description=description,
                                color=color))


# Runs Bot... Obviously
client.run(envariables.discordToken)
