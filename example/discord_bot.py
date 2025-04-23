import os

import discord
from dotenv import load_dotenv
from hangman import hangman_state_machine

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignore messages from the bot itself
    output = hangman_state_machine.run(message.content, message.channel.id)

    # add formatting for discord
    output = "```" + output + "```"

    await message.channel.send(output)


client.run(TOKEN)
