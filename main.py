import discord
from discord.ext import commands, tasks
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import json

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# SERVER_ID = 351901521283252234  # SUH DUDE
SERVER_ID = 961311552907149365  # Bot Test
COPY_PASTA_ID = 1267527871677730906 # copy-pasta

with open('message_counts.json', 'r') as file:
    message_counts = json.load(file)

print("Message Counts Loaded Successfully")
print("Connecting to Discord...")

@bot.event
async def on_ready():
    global message_counts

    print(f'Bot is connected to Discord')
    if not update_message_counts.is_running():
        update_message_counts.start(message_counts)


@bot.event
async def on_disconnect():
    global message_counts

    await update_message_counts(message_counts)
    print("Bot has disconnected from Discord.")


@bot.event
async def on_message(message):
    # Ignore messages sent by the bot
    if message.author == bot.user:
        return

    # if message.guild.id != SERVER_ID:
    #     return

    if len(message.content) < 3:
        return

    # Increment dictionary value for user (ignoring reports)
    if not message.content.startswith('!wrongchat'):
        message_counts[str(message.author)] = message_counts.get(str(message.author), 0) + 1

    await bot.process_commands(message)


@tasks.loop(hours=.0166)
async def update_message_counts(counts):
    with open('message_counts.json', 'w') as f:
        json.dump(counts, f)

    # print("Message Counts Updated")

@bot.command()
async def copypasta(ctx):
    global COPY_PASTA_ID

    # if the message is a reply
    if ctx.message.reference:
        message = ctx.message
        # Capture message metadata
        reply_id = message.reference.message_id
        author_id = message.reference.resolved.author.id
        orig_msg = await ctx.fetch_message(reply_id)
        copy_pasta = orig_msg.content

        channel = bot.get_channel(COPY_PASTA_ID)
        author_message = await channel.send(f'Originally from <@{author_id}>\n')
        await channel.send(copy_pasta, reference=author_message)

        print(f'Copy Pasta Recorded: \n {copy_pasta}')

    else:
        await ctx.send('Please reply to a message')

@bot.command()
async def wrongchat(ctx):
    message = ctx.message
    now = datetime.now()

    # if the message is a reply
    if ctx.message.reference:
        # Capture message metadata
        reply_id = message.reference.message_id
        perp = message.reference.resolved.author
        print(
            f'.\n'
            f'New Report\n'
            f'Reporter: {message.author}\n'
            f'Perpetrator: {perp}\n'
            f'Channel: {message.channel}\n'
            f'Message ID: {reply_id}\n'
            f'DateTime: {now}\n'
        )

        # DataFrame has columns
        # 'Reporter','Perpetrator','Channel','MessageID','DateTime'
        dataframe = pd.read_csv('data.csv')

        # if message has already been reported
        if (dataframe['MessageID'] == reply_id).any():
            await ctx.send('Message has already been reported')
            return

        new_row = pd.DataFrame([[message.author, perp, message.channel, reply_id, now]], columns=dataframe.columns)
        dataframe = pd.concat([dataframe, new_row], ignore_index=True)
        dataframe.to_csv('data.csv', index=False)

        await ctx.send(
            f'.\n'
            f'Report Captured\n'
            f'Reporter: {message.author}\n'
            f'Perpetrator: {perp}\n'
            f'Channel: {message.channel}\n'
            f'Message ID: {reply_id}\n'
            f'DateTime: {now}\n'
        )

    else:
        await ctx.send('Please reply to the message you want to report')


@bot.command()
async def tallycount(ctx):
    message = ctx.message
    dataframe = pd.read_csv('data.csv')
    account = message.mentions[0] if message.mentions else message.author

    reports = (dataframe['Reporter'] == str(account)).sum()
    offenses = (dataframe['Perpetrator'] == str(account)).sum()

    print(f'\n'
          f'Data Request for {account}\n'
          f'Total Reports: {reports}\n'
          f'Total Offenses: {offenses}\n'
          )

    plt.clf()
    plt.figure()
    plt.bar(['Reports', 'Offenses'], [reports, offenses], color=['green', 'red'])
    plt.title(f'Records for {account}')
    plt.ylabel('Count')
    plt.savefig('tally_chart_user.png')

    await ctx.send(content=f'.\n'
                   f'Records for {account}\n'
                   f'---------------\n'
                   f'Total Reports: {reports}\n'
                   f'Total Offenses: {offenses}',
                   file=discord.File('tally_chart_user.png'))


@bot.command()
async def ratiocount(ctx):
    global message_counts

    message = ctx.message
    dataframe = pd.read_csv('data.csv')
    user = message.mentions[0] if message.mentions else message.author

    reports = round((dataframe['Reporter'] == str(user)).sum() / message_counts.get(str(user), 1), 2)
    offenses = round((dataframe['Perpetrator'] == str(user)).sum() / message_counts.get(str(user), 1), 2)

    print(f'\n'
          f'Data Request for {user}\n'
          f'Reports / Messages: {reports}\n'
          f'Offenses / Messages: {offenses}\n'
          )

    plt.clf()
    plt.figure()
    plt.bar(['Reports/Messages', 'Offenses/Messages'], [reports, offenses], color=['green', 'red'])
    plt.title(f'Records for {user}')
    plt.ylabel('Count')
    plt.savefig('tally_chart_user.png')

    await ctx.send(content=f'.\n'
                   f'Records for {user}\n'
                   f'---------------\n'
                   f'Reports/Messages: {reports}\n'
                   f'Offenses/Messages: {offenses}',
                   file=discord.File('tally_chart_user.png'))


@bot.command()
async def tallycounts(ctx):
    dataframe = pd.read_csv('data.csv')

    # get the counts for every user and sort them in descending order
    all_offenses = dataframe['Perpetrator'].value_counts().sort_values()

    # build the image chart
    plt.clf()
    plt.figure()
    all_offenses.plot.barh(color='red')
    plt.xticks(rotation='horizontal')
    plt.xlabel('Count')
    plt.tight_layout()
    plt.savefig('tally_chart_all.png')

    # build the text chart
    chart = '\n'
    for key, value in all_offenses[::-1].items():
        chart += f'{value}  - {key}\n'

    await ctx.send(content=f'.\n'
                   f'All Records\n'
                   f'---------------'
                   f'{chart}',
                   file=discord.File('tally_chart_all.png'))


@bot.command()
async def ratiocounts(ctx):
    global message_counts

    dataframe = pd.read_csv('data.csv')

    # get the counts for every user and sort them in descending order
    all_offenses = dataframe['Perpetrator'].value_counts().sort_values()
    all_offenses_ratio = pd.Series(
        {user: count / message_counts.get(user, 1) for user, count in all_offenses.items()}
    )

    # build the image chart
    plt.clf()
    plt.figure()
    all_offenses_ratio.plot.barh(color='red')
    plt.xticks(rotation='horizontal')
    plt.xlabel('Ratio')
    plt.tight_layout()
    plt.savefig('ratio_chart_all.png')

    # build the text chart
    chart = '\n'
    for key, value in all_offenses_ratio[::-1].items():
        chart += f'{round(value, 2)}  - {key}\n'

    await ctx.send(content=f'.\n'
                   f'All Records (Offenses/Messages)\n'
                   f'---------------'
                   f'{chart}',
                   file=discord.File('ratio_chart_all.png'))


bot.run('')
