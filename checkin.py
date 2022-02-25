import discord
import requests
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
intents.messages = True
client = discord.Client(intents=intents)  # Client initialization

# Alex
AuthorizedUsers = [352641008040804352, 195687412956004352, 134870132538212353]

# Event date in "YYYY-MM-DD" format
day1 = "2022-02-26"
day2 = "2022-02-27"

CEREMONY_POINTS = 3
TECH_TALK_POINTS = 1
# event format - "event-code-here": {start-time: "YYYY-MM-DD HH:MM", end-time: "HH:MM:SS", "name": "__"}
# Note: on startup times will be parsed and turned into datetime objects with keys datetime-start and datetime-end
events = {
    "7YPN2": {"start-time": f"{day1} 10:45", "end-time": f"{day1} 11:30", "name": "OpeningCeremony", "points": CEREMONY_POINTS},
    "BXBN1": {"start-time": f"{day1} 10:25", "end-time": f"{day1} 12:55", "name": "MTTechTalk", "points": TECH_TALK_POINTS},
    "8ECP7": {"start-time": f"{day1} 3:30", "end-time": f"{day1} 3:50", "name": "CbrandsTechTalk", "points": TECH_TALK_POINTS},
    "Y8XN4": {"start-time": f"{day2} 10:45", "end-time": f"{day2} 11:30", "name": "ClosingCeremony", "points": CEREMONY_POINTS},
}


def verify_admin(message) -> bool:
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
    divided = message.content.strip().split()
    if len(divided) != 2:
        await message.channel.send("Usage: `$checkin (code)`")
        return
    code = divided[1]
    valid_code, event_name, event_points = check_code(code)
    if not valid_code:
        await message.channel.send("Checkin Failed: Incorrect Code")
        return
    r = requests.post(f"http://localhost:8880/api/hackers/{message.author.id}/{message.author.name}/event/{event_name}/{event_points}")
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
    test_go_connection()
    parse_times()
    print("Ready to Handle Requests")


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
    # discord bot key
    client.run('OTQzMzE4MDQ1MTIyNzg1MzIw.YgxTYw.Q3wEGFCHmVCzOSEkId8zHLaSYgw')


if __name__ == '__main__':
    main()
