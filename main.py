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
        return message.author == user and message.content[0] != '!'
    return inner_check

async def check_in(user):
    date, tasks = get_from_notion()

    standup_questions[0] = standup_questions[0].format(user.name)

    if date: # previous entry exists
        # turn date (ex. 2021-08-18) into human friendly form
        time_passed = (datetime.datetime.today() - datetime.datetime.strptime(date, '%Y-%m-%d')).days
        if time_passed == 1:
            date = 'yesterday'
        elif time_passed <= 7:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('last %A')
        else:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%b %d')

        tasks_string = "".join("- " + task + "\n" for task in tasks).strip()
        standup_questions[1] = standup_questions[1].format(date, tasks_string)
    else:
        standup_questions[1] = standup_questions[1].split(" Y")[0]
    
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
            if member.id == god and not member.bot:
                await check_in(member)

@bot.command()
async def members(ctx):
    channel = bot.get_channel(test_channel)
    async for member in ctx.guild.fetch_members(limit=None):
        await channel.send(f"{member} --- {member.id}")


bot.run(TOKEN)