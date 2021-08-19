import datetime
import discord
from discord.ext import commands, tasks

import auth
from notion_io import get_from_notion, send_to_notion
from config import god, test_channel, standup_questions

# allow bot to access member list
intents = discord.Intents.default()
intents.members = True


# CONSTANTS
TOKEN = auth.disc_token
bot = commands.Bot(command_prefix='!', intents=intents)
team = [god]


def check(user):
    def inner_check(message):
        return message.author == user
    return inner_check

async def check_in(user):
    previous_response = get_from_notion()
    
    user_responses = []
    for question in standup_questions:
        await user.send(question)
        msg = await bot.wait_for('message', check=check(user))
        user_responses.append(msg.content)
    
    send_to_notion(user_responses)

    await user.send("Perfect! Good luck and have a great day :smile:")


@bot.event
async def on_ready():
    for guild in bot.guilds:
        for member in guild.members:
            if member.id == god and not member.user.bot:
                await check_in(member)

@bot.command()
async def members(ctx):
    channel = bot.get_channel(test_channel)
    async for member in ctx.guild.fetch_members(limit=None):
        await channel.send(f"{member} --- {member.id}")


bot.run(TOKEN)