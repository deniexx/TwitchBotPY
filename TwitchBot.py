import re
from twitchio.ext import commands
import asyncio
import random
import json

CHANNELS = ["#CHANNEL"]  # channels that the bot will connect [must be list or tuple]
NICK = "NICK"  # your bot channel username

bot = commands.Bot(
    irc_token="oauth:AUTH",  # your oauth code
    client_id="CLIENT_ID",  # your app id
    nick=NICK,
    prefix="!",  # command prefix
    initial_channels=CHANNELS
)

trustedUsersFile = "trustedUsers.txt"

trustedUsers = []

intervalMessages = ["You can grab your own MetcheBot source code from: https://github.com/deniexx/TwitchBotPY",
                    "These messages can be customized."]

# To add more messages to send add a comma and a on a a new line type your text in quotations


async def intervalmessage(ws):
    for channel in CHANNELS:
        for message in intervalMessages:
            await ws.send_privmsg(channel, message)

    await asyncio.sleep(300)
    await intervalmessage(ws)


def takeUsers():
    try:
        f = open(trustedUsersFile, "r")
        return json.load(f)
    except Exception as e:
        print(e)
        return []
    # Take all users from file and import them into list


@bot.event
async def event_ready():
    print("Bot is ready")
    ws = bot.ws
    for channel in CHANNELS:
        await ws.send_privmsg(channel, "/me is coming to save the day")
        # Message to send when the bot comes online

    trusted_users = takeUsers()
    await intervalmessage(ws)


@bot.event
async def event_message(ctx):
    if ctx.author.name.lower() == NICK:
        return

    await bot.handle_commands(ctx)

    # Check if there is a link in the message
    match = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]"
                      r"+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>"
                      r"]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<"
                      r">]+|(\([^\s()<>]+\)))*\)|[^\s`!()"
                      r"\[\]{};:'\".,<>?«»“”‘’]))", ctx.content)

    if match and ctx.author.name\
            not in f"@{trustedUsers}" and not ctx.author.is_mod:

        await ctx.channel.timeout(ctx.author.name, 60, "link post")
        await ctx.channel.send(f"Don't post links @{ctx.author.name}")
        # Times out people who post links


@bot.command(name="clear")
async def clear(ctx):
    if ctx.author.is_mod:
        await ctx.channel.clear()
        # Clears the entire chat if the command is used by a moderator


@bot.command(name="ban")
async def ban(ctx, user=None, *args):
    if ctx.author.is_mod:
        if user and args:
            await ctx.channel.ban(user, " ".join(args))
            await ctx.send(f"{user} has been banned for {' '.join(args)}")

        else:
            await ctx.send(f'@{ctx.author.name} -> !ban "user" "reason"')
            # Bans a user if command is used by mod


@bot.command(name="unban")
async def unban(ctx, user):
    if ctx.author.is_mod:
        await ctx.channel.unban(user)
        # Unbans user if command is used by mod


@bot.command(name="trust")
async def trust(ctx, user):
    if ctx.author.is_mod:
        trustedUsers.append(user)
        await ctx.send(f"{user} is permitted to post links")
        users = takeUsers()
        users.append(user)
        with open(trustedUsersFile, "w+") as f:
            json.dump(users, f)
        # You can permit a user to post links if command is used by mod


@bot.command(name="untrust")
async def untrust(ctx, user):
    if ctx.author.is_mod:
        trustedUsers.remove(user)

        users = takeUsers()
        users.remove(user)
        f = open(trustedUsersFile, "w+")
        json.dump(users, f)
        f.close()
        await ctx.send(f"{user} is no longer permitted to post links")
        # You can remove the permission from the user if command is used by mod


@bot.command(name="winner")
async def getwinner(ctx):
    if ctx.author.is_mod:
        users = await bot.get_chatters(str(ctx.channel))
        await ctx.send(f"@{random.choice(users[1])} is the winner")
        # Gets a list of all members and chooses 1 on random


@bot.command(name="help")
async def sendhelp(ctx):
    await ctx.send("Available commands: ")
    await ctx.send("""!clear - To clear messages 
    !ban/unban "user" "reason to ban" - ban/unban user
    !trust/untrust "user" - trust/untrust a user (allow to send links)
    !winner - choose a random veiwer to be the winner""")

bot.run()
