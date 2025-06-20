# IMPORT STANDARD LIBRARIES
import os
import json
from datetime import datetime

# IMPORT THIRD PARTY LIBRARIES
import pydantic
import requests


WEBHOOK_URL = os.getenv("WEBHOOK_URL")


# Dict of World Quests to track.
# keys = expansions (must match the url's from wowhead)
# values = set of quest IDs
WORLD_QUESTS: dict[str, list[int]] = {
    "legion": [
        # 42819, # Legion World Boss: Humongris
        # 45977, # Where There is a Whip...
    ],
    "bfa": [
        # 51976,  # Green Sabertron
        # 50873, # Test
        # 51173, # Sandfishing
        # 54689, # "Lights Out" for [Doomsoul Surprise]
        # 54415, # "Vulpera for a Day" for [Scavenge like a Vulpera]
        # 50717, # "Don't Stalk Me, Troll" for [Zandalari Spycatcher]
        # 50786, # "Revenge of Krag'wa" for [Revenge is Best Served Speedily]
        # 50665, # "Cancel the Blood Troll Apocalypse" for [A Most Efficient Apocalypse]
        # 51957, # "The Wrath of Vorrik" for [Vorrik's Champion] Part 1
        # 51983, # "Vorrik's Vengeance" for [Vorrik's Champion] Part 2
        # [Vorrik's Champion] Part 3
        # 52798, # "A Few More Charges" for [Hungry, Hungry Ranishu]
    ],
    "sl": [],
    "df": [
        # 78370,  # Claws for Concern
    ],
    "tww": [
        # 82120, # Pool Cleaner
        # 82580, # Courier Mission: Ore Recovery
    ],
}

################################################################################


class WorldQuest(pydantic.BaseModel):
    id: int
    ending: datetime
    worldquesttype: int | None = None
    factions: list = []

    # Rewards is a bit weird.. .its sometimes a dict sometimes an empty list.
    # since we don't need it right now.. we skip
    # rewards: WorldQuestRewards = WorldQuestRewards()

    zones: list[int] = []

    info: dict = {}
    # @property
    # def info(self):
    #      return world_quest_infos.get(self.id) or {}

    @property
    def name(self):
        return self.info.get("name_enus") or f"WQ({self.id})"

    @property
    def link(self):
        return f"https://www.wowhead.com/quest={self.id}"


################################################################################


def get_world_quests_info(html: str) -> dict:
    """
    Returns a list of dicts such as:
    >>> {
    >>>     72029: {
    >>>         "name_enus": "Fishing Frenzy!",
    >>>         "icon": "quest-start",
    >>>         "_side": 0,
    >>>         "reqclass": 0,
    >>>         "reqrace": 0
    >>>     },
    >>> }

    """
    # find the correct line
    for line in html.splitlines():
        if line.startswith("WH.Gatherer.addData(5, 1"):
            line = line.split("{", 1)[-1]
            line = "{" + line  # readd the { removed by the split above
            line = line.rstrip(");")

            infos = json.loads(line)
            infos = {int(k): v for k, v in infos.items()}  # convert the keys to integers
            return infos

    return {}


def get_world_quests_from_html(text: str) -> list[WorldQuest]:
    # find the correct line
    for line in text.splitlines():

        if "new Listview({" not in line:
            continue

        # expected line example:
        # >>> new Listview({"parent":"list","id":"lv-world-quests","template":"worldquests","data":[]});
        # we need the list of "data"
        line = line.split('"data":')[-1]
        line = line.split(";")[0]
        line = line.rstrip("});")

        world_quests = pydantic.TypeAdapter(list[WorldQuest]).validate_json(line)
        return world_quests

    return []


################################################################################


def load_website(expansion: str, region="eu") -> str:
    url = f"https://www.wowhead.com/world-quests/{expansion}/{region}"
    html = requests.get(url).text
    # df_list = pd.read_html(html)
    return html


################################################################################
#                   Discord


def fields_from_world_quest(world_quest: WorldQuest) -> list[dict]:
    return [
        {
            "name": "Name",
            "value": f"[{world_quest.name}](<{world_quest.link}>)",
            "inline": True,
        },
        {
            "name": "Zones",
            "value": ", ".join(str(zone) for zone in world_quest.zones),
            "inline": True,
        },
        {
            "name": "Until",
            "value": f"<t:{int(world_quest.ending.timestamp())}:R>",
            "inline": True,
        },
    ]


def send_discord_message(message: str, world_quests: list[WorldQuest] = []):
    # build the message
    discord_message = {}
    # discord_message["embeds"] = [embed]
    discord_message["content"] = message

    if world_quests:
        fields = []
        for world_quest in world_quests:
            fields += fields_from_world_quest(world_quest)
        embed = {"title": "World Quests", "fields": fields}
        discord_message["embeds"] = [embed]

    # print("discord_message", discord_message)
    response = requests.post(WEBHOOK_URL, json=discord_message)
    return response


################################################################################
#                   Main
#


def get_active_world_quests(expansion: str) -> list[WorldQuest]:
    html = load_website(expansion)

    info = get_world_quests_info(html)
    world_quests = get_world_quests_from_html(html)
    for world_quest in world_quests:
        world_quest.info = info.get(world_quest.id, {})

    return world_quests


def main() -> None:
    world_quests: list[WorldQuest] = []

    for expansion, qids in WORLD_QUESTS.items():
        active_world_quests = get_active_world_quests(expansion)
        active_world_quests = [wq for wq in active_world_quests if wq.id in qids]
        world_quests.extend(active_world_quests)

    if world_quests:
        send_discord_message("<@392483139991240714> !!!", world_quests)
    else:
        send_discord_message("No Interessting World Quests found.")


if __name__ == "__main__":
    main()
