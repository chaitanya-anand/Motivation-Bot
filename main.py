import discord
import os  # for the Bot authentication TOKEN from env(secret) file
import requests  # allows code to make HTTP requests
import json  # to manage data returned my api
import random  # to choose random message
from replit import db  # to use repl.it database
from keep_alive import keep_alive  # to run web-server in repl.it

client = discord.Client()

sad_words = [
    "unhappy", "depressed", "sad", "discouraged", "angry", "depressing",
    "miserable"
]

starter_encouragements = [
    "Cheer Up!", "You are doing great", "Hang in there",
    "You are an awesome person!"
]

if "responding" not in db.keys():
    db["responding"] = True


# function to get quote from API
def get_quotes():
    # get random quote from api
    response = requests.get("https://zenquotes.io/api/random")

    # read the json data
    json_data = json.loads(response.text)

    #store the quote and author
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return (quote)


# add a new encouraging message to database
def update_encouragements(encouraging_message):
    if "encouragements" in db.keys():
        encouragements = db["encouragements"]
        encouragements.append(encouraging_message)
        db["encouragements"] = encouragements
    else:
        db["encouragements"] = [encouraging_message]


# delete an existing message from database
def delete_encouragements(index):
    encouragements = db["encouragements"]

    if len(encouragements) > index:
        del encouragements[index]

    db["encouragements"] = encouragements


# function called when Bot starts
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# function called when message received in server
@client.event
async def on_message(message):
    # if message is from the bot, then don't do anything
    if message.author == client.user:
        return

    # get message content
    msg = message.content

    # respond to hello
    if msg.startswith('$hello'):
        await message.channel.send('Hello!')

    # send motivational quotes from www.zenquotes.io
    if msg.startswith('$motivate'):
        quote = get_quotes()
        await message.channel.send(quote)

    # get all encouragements from database and starter_encouragements
    options = starter_encouragements
    if "encouragements" in db.keys():
        options = options + db["encouragements"].value

    # if sad word detected in any message and responding is turned on
    # then send an encouraging message
    if db["responding"] and any(word in msg for word in sad_words):
        await message.channel.send(random.choice(options))

    # add new encouraging message to database
    if msg.startswith('$new'):
        # split the message so that the "$new " command is not added
        # check if command contains the message
        try:
            encouraging_message = msg.split("$new ", 1)[1]
        except:
            await message.channel.send(
                "No encouraging message found!\nPlease provide a message after the command."
            )
        else:
            # call function to update database
            update_encouragements(encouraging_message)
            await message.channel.send("New encouraging message added.")

    # delete existing encouraging message from database
    if msg.startswith('$del'):
        encouragements = []
        if "encouragements" in db.keys():
            try:
                index = int(msg.split("$del", 1)[1])
            except:
                await message.channel.send(
                    "No valid index found after message.")
            else:
                delete_encouragements(index)
                encouragements = db["encouragements"].value
                await message.channel.send(encouragements)

    # list all encouraging message in database
    if msg.startswith('$list'):
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = db["encouragements"].value
        await message.channel.send(encouragements)

    # turn responding to sad words on or off
    if msg.startswith('$responding'):
        try:
            value = msg.split('$responding ', 1)[1]
        except:
            if db['responding']:
                await message.channel.send("Responding is on.")
            else:
                await message.channel.send("Responding is off.")
        else:
            if value == 'false':
                db['responding'] = False
                await message.channel.send("Responding is off.")
            else:
                db['responding'] = True
                await message.channel.send("Responding is on.")

# start web-server
keep_alive()
# Bot TOKEN
client.run(os.environ['TOKEN'])
