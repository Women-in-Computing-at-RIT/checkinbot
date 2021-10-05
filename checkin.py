import discord
import requests

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)  # Client initialization

# Alex
AuthorizedUsers = [352641008040804352]

event_code = "xxxxx"
event_name = "We-re done"
# Past Events:


def verify_admin(message):
    if message.author.id in AuthorizedUsers:
        return True
    return False


async def help_manager(message):
    divided = message.content.strip().split()
    if len(divided) == 1:
        help_embed = discord.Embed()
        help_embed.title = "Help"
        help_embed.type = "rich"
        help_embed.colour = discord.colour.Color.blue()
        if verify_admin(message):
            help_embed.add_field(name="\"$getwinner (event_name)\"", value="generate winner from event",
                                     inline=False)
        help_embed.add_field(name="\"$checkin (code)\"", value="Check-in to event",
                             inline=False)
        await message.channel.send(embed=help_embed)
    else:
        message.channel.send("Usage: `-help`")
        return


async def checkin(message):
    divided = message.content.strip().split()
    if len(divided) != 2:
        await message.channel.send("Usage: `$checkin (code)`")
        return
    code = divided[1]
    if code != event_code:
        await message.channel.send("Checkin Failed: Incorrect Code")
        return
    r = requests.post(f"http://localhost:8880/api/hackers/{message.author.id}/{message.author.name}/event/{event_name}")
    if r.status_code == 500:
        print("checkin failure")
        print(r.json())
        await message.channel.send("CheckinBot Failure: Please contact Alex - Logistics for help")
        return
    elif r.status_code != 200:
        await message.channel.send("Checkin Failed")
        print("error with code " + str(r.status_code))
        return

    await message.channel.send(f"Checkin Successful: Thank you for joining {event_name}")
    return


async def getwinner(message):
    if not verify_admin(message):
        print("non admin tried to get winner")
        return
    divided = message.content.strip().split()
    if len(divided) != 2:
        await message.channel.send("Usage: `getwinner (event_name)`")
        return
    name = divided[1]
    r = requests.get(f"http://localhost:8880/api/events/{name}/get-winner")
    if r.status_code != 200:
        print(r.json())
        await message.channel.send("Something went wrong, please check the logs")
        return

    await message.channel.send(r.json())
    return


def test_go_connection():
    r = requests.get('http://localhost:8880/api/ping')
    if r.status_code != 200:
        print("Couldn't Connect to Web Server")
        exit(2)
    return

@client.event
async def on_ready():
    test_go_connection()


@client.event
async def on_message(message):
    if not message.content.startswith("$"):
        return
    if not ( isinstance(message.channel, discord.channel.DMChannel) and message.author != client.user ):
        await message.channel.send("Please communicate with me through direct message. You can do this"
                                   " by right-clicking on my name and selecting message")
        await message.delete()
        return

    command = message.content.strip().split()[0].lower()
    if command == "$help":
        await help_manager(message)
    if command == "$checkin":
        await checkin(message)
    if command == "$getwinner":
        await getwinner(message)

def main():
    # who needs security...hardcode all the things
    client.run('')


if __name__ == '__main__':
    main()
