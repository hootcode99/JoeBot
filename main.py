import discord
import os

# Create new discord client agent
joebot = discord.Client()
# store API token
my_secret = os.environ['token']


def remove_punctuation(message):
    punctuation = ".?!,;"  # punctuation dictionary
    cleared = message  # copy message to working variable
    for char in cleared:
        if char in punctuation:
            # replace punctuation with spaces
            cleared = cleared.replace(char, '')
    return cleared


# Verify Bot is connected and ready
@joebot.event
async def on_ready():
    print("JoeBot is beeping and booping\n")
    print("--------------------------------------")


# When a message is posted in any channel
@joebot.event
async def on_message(message):
    # remove punctuation, capital letter, and trailing whitespace
    clear_post = remove_punctuation(message.content).strip().lower()

    # ignore messages from itself
    if message.author == joebot.user:
        return
    elif "" in clear_post:
        await message.channel.send()


# token confirmation to communicate with Discord API
joebot.run(my_secret)
