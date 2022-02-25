import discord
import requests
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
intents.messages = True
client = discord.Client(intents=intents)  # Client initialization

# Alex
AuthorizedUsers = [352641008040804352, 195687412956004352, 134870132538212353]

# api domain
API_DOMAIN = "localhost:8880"

CEREMONY_POINTS = 3
TECH_TALK_POINTS = 1

# Event date in "YYYY-MM-DD" format
day1 = "2022-02-26"
day2 = "2022-02-27"
# event format - "event-code-here": {start-time: "YYYY-MM-DD HH:MM", end-time: "HH:MM:SS", "name": "__"}
# Note: on startup times will be parsed and turned into datetime objects with keys datetime-start and datetime-end
events = {
    "PJ823": {"start-time": f"{day1} 10:00", "end-time": f"{day1} 11:00", "name": "OpeningCeremony", "points": CEREMONY_POINTS},
    "8ADHE": {"start-time": f"{day1} 13:00", "end-time": f"{day1} 13:35", "name": "M&TTech", "points": TECH_TALK_POINTS},
    "P0M31": {"start-time": f"{day1} 13:40", "end-time": f"{day1} 14:00", "name": "Brite", "points": TECH_TALK_POINTS},
    "L9RXA": {"start-time": f"{day1} 14:05", "end-time": f"{day1} 14:55", "name": "ConstellationBrands", "points": TECH_TALK_POINTS},
    "13DA1": {"start-time": f"{day1} 15:00", "end-time": f"{day1} 15:20", "name": "Wayfair", "points": TECH_TALK_POINTS},
    "AFQG9": {"start-time": f"{day1} 15:50", "end-time": f"{day1} 16:10", "name": "L3Harris", "points": TECH_TALK_POINTS},
    "G674H": {"start-time": f"{day1} 16:15", "end-time": f"{day1} 17:05", "name": "Foundry", "points": TECH_TALK_POINTS},
    "10BHE": {"start-time": f"{day1} 17:10", "end-time": f"{day1} 17:30", "name": "VisualDx", "points": TECH_TALK_POINTS},
    "LAD9H": {"start-time": f"{day1} 17:35", "end-time": f"{day1} 18:25", "name": "CloudBlue", "points": TECH_TALK_POINTS},
    "8T6RE": {"start-time": f"{day1} 18:30", "end-time": f"{day1} 19:05", "name": "STR", "points": TECH_TALK_POINTS},
    "Z7GXN": {"start-time": f"{day2} 15:00", "end-time": f"{day2} 16:05", "name": "ClosingCeremony", "points": CEREMONY_POINTS},
}

"""
    Check if a user is a listed authorized user
    :param message: Discord message
    :return: true if authorized, false otherwise
    """
def verify_admin(message) -> bool:
    if message.author.id in AuthorizedUsers:
        return True
    return False


async def help_manager(message):
    """
    Help command for understanding bot usage
    :param message: Discord message
    """
    divided = message.content.strip().split()
    # $help
    if len(divided) == 1:
        help_embed = discord.Embed()
        help_embed.title = "Help"
        help_embed.type = "rich"
        help_embed.colour = discord.colour.Color.blue()
        if verify_admin(message):
            help_embed.add_field(name="\"$getwinner (event_name)\"", value="Generate winner from event",
                                 inline=False)
            help_embed.add_field(name="\"$getgrandwinner\"", value="Generate grand prize winner",
                                 inline=False)
        help_embed.add_field(name="\"$checkin (code)\"", value="Check-in to event",
                             inline=False)
        await message.channel.send(embed=help_embed)
    # Incorrect arguments
    else:
        message.channel.send("Usage: `$help`")
        return


def check_code(code) -> (bool, str, int):
    """
    Takes code and determines whether code is valid for current time

    :param code:
    :param now:
    :return: bool indicating if code is valid, str representing name of event
    """
    if code not in events:
        return False, ""
    time = datetime.now()
    if events[code]["datetime-start"] < time < events[code]["datetime-end"]:
        # user is within valid checkin time
        return True, events[code]["name"], events[code]["points"]
    return False, ""


async def checkin(message):
    """
    Check in logic on message sent to bot
    :param message: Discord message
    """
    divided = message.content.strip().split()
    # Incorrect arguments
    if len(divided) != 2:
        await message.channel.send("Usage: `$checkin (code)`")
        return
    code = divided[1]
    valid_code, event_name, event_points = check_code(code)
    if not valid_code:
        await message.channel.send("Checkin Failed: Incorrect Code")
        return
    r = requests.post(f"http://{API_DOMAIN}/api/hackers/{message.author.id}/{message.author.name}/event/{event_name}/{event_points}")
    if r.status_code == 500:
        print("Check-in failure")
        print(r.json())
        # TODO: change to future logistics heads
        await message.channel.send("CheckinBot Failure: Please contact Aby Tiet or Annie Tiet for help")
        return
    # Unable to check in due to unsuccessful connection to Web Server
    elif r.status_code != 200:
        await message.channel.send("Check-in Failed")
        print("Error with code " + str(r.status_code))
        return
    # Successful check-in!
    await message.channel.send(f"Checkin Successful: Thank you for joining {event_name}")
    return


async def getwinner(message):
    """
    Gets the event winner
    # TODO: rename to get_winner
    :param message: Discord message
    :return:
    """
    # Authorized users only
    if not verify_admin(message):
        print("Unauthorized user tried to get winner")
        return
    divided = message.content.strip().split()
    # Incorrect arguments
    if len(divided) != 2:
        await message.channel.send("Usage: `getwinner (event_name)`")
        return
    # Get winner from Web Server
    name = divided[1]
    r = requests.get(f"http://{API_DOMAIN}/api/events/{name}/get-winner")
    # Unsuccessful request to Web Server
    if r.status_code != 200:
        print(r.json())
        await message.channel.send("Something went wrong, please check the logs")
        return
    await message.channel.send(r.json())
    return


async def getgrandwinner(message):
    """
    Gets the grand prize winner
    :param message: Discord message
    :return:
    """
    # Authorized users only
    if not verify_admin(message):
        print("Unauthorized user tried to get winner")
        return
    divided = message.content.strip().split()
    # Incorrect arguments
    if len(divided) != 1:
        await message.channel.send("Usage: `getgrandwinner`")
        return
    # Get winner from Web Server
    r = requests.get(f"http://{API_DOMAIN}/api/events/get-winner/grand-prize")
    # Unsuccessful request to Web Server
    if r.status_code != 200:
        print(r.json())
        await message.channel.send("Something went wrong, please check the logs")
        return
    await message.channel.send(r.json())
    return


def test_go_connection():
    """
    Checks status to Go Web Server (WiCHacksBotAPI)
    """
    r = requests.get(f"http://{API_DOMAIN}/api/ping")
    if r.status_code != 200:
        print("Couldn't Connect to Web Server")
        exit(2)
    return


def parse_date(time) -> datetime:
    return datetime.strptime(time, "%Y-%m-%d %H:%M")


def parse_times():
    for value in events.values():
        value["datetime-start"] = parse_date(value["start-time"])
        value["datetime-end"] = parse_date(value["end-time"])
        if value["datetime-start"] > value["datetime-end"]:
            print("Start time after End time")
            raise Exception


@client.event
async def on_ready():
    """
    Method called on successful bot startup
    """
    test_go_connection()
    parse_times()
    print("Ready to Handle Requests")


@client.event
async def on_message(message):
    """
    Method called to process user messages
    :param message: Discord message
    """
    if not message.content.startswith("$"):
        return
    if not (isinstance(message.channel, discord.channel.DMChannel) and message.author != client.user):
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
    if command == "$getgrandwinner":
        await getgrandwinner(message)


def main():
    # who needs security...hardcode all the things
    # discord bot key
    # TODO: add the bot key / add to GitHub secrets
    client.run('')


if __name__ == '__main__':
    main()
