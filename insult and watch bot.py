import discord
import requests
import time
import asyncio
from discord.ext import commands
from collections import defaultdict

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
userMessages = defaultdict(list)
maxMessages = 10
timeInterval = 6
timeout_duration = 30  

def get_insult(who=None):
    params = {"lang": "en"}
    if who:
        params["who"] = who
    response = requests.get("https://insult.mattbas.org/api/insult", params=params)
    if response.status_code == 200:
        return response.text
    else:
        return "Couldn't fetch an insult at this time."

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    currentTime = time.time()
    if message.content.lower().startswith("insult"):
        parts = message.content.split()
        if len(parts) > 1:
            who = parts[1]
            insult = get_insult(who)
        else:
            insult = get_insult()
        await message.channel.send(insult)

    user_id = message.author.id
    userMessages[user_id].append((message.content, currentTime))
    userMessages[user_id] = [
        (msg, timeStamp) for msg, timeStamp in userMessages[user_id]
        if currentTime - timeStamp < timeInterval
    ]

    if len(userMessages[user_id]) >= maxMessages:
        # Timeout the user from sending messages
        member = message.guild.get_member(message.author.id)
        if member:
            try:
                await message.channel.set_permissions(member, send_messages=False)
                await asyncio.sleep(timeout_duration)
                await message.channel.set_permissions(member, send_messages=True)
            except discord.Forbidden:
                print(f"Bot doesn't have permission to manage roles or channels in {message.guild.name}.")
            except Exception as e:
                print(f"An error occurred: {type(e).__name__} - {e}")

client.run("your discord bot code")