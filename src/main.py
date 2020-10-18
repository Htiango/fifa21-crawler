import copy
import json
import sqlalchemy as db
import time

from player import Player
from tables.club import Club
from tables.nation import Nation
from tables.player_info import PlayerInfo
from tables.player_stats import PlayerStats
from tables.player_usage import PlayerUsage
from sqlalchemy.exc import IntegrityError



with open('credentials.json', 'r') as f:
    config = json.load(f)

user = config['user']
password = config["password"]
host = config["host"]
database = config["db"]

connect_str_template = "mysql+pymysql://{user}:{password}@{host}/{db}"
connect_str = connect_str_template.format(user=user, 
                                          password=password,
                                          host=host,
                                          db=database)

engine = db.create_engine(connect_str)
connection = engine.connect()
metadata = db.MetaData()


player_info_table = PlayerInfo(metadata).table
club_table = Club(metadata).table
nation_table = Nation(metadata).table
player_stats_table = PlayerStats(metadata).table
player_usage_table = PlayerUsage(metadata).table

metadata.create_all(engine)




def timeit(method):
    """
    decorator function to calculate the time
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        time_ms = "{:.2f}ms".format((te - ts) * 1000)
        print("Time: {}".format(time_ms))
        return result
    return timed

@timeit
def insert_one(url):
    player = Player(url)
    print(player.display_name)

    try:
        query = db.insert(player_info_table).values(full_name=player.full_name, 
            resource_id=player.resource_id,
            rating=player.rating,
            pos=player.pos,
            display_name=player.display_name,
            player_img=player.player_img,
            nation=player.nation,
            club=player.club,
            league=player.league,
            url=player.url,
            skills=player.skills,
            weak_foot=player.weak_foot,
            intl_rep=player.intl_rep,
            foot=player.foot,
            height=player.height,
            weight=player.weight,
            color=player.color,
            rare_type_int=player.rare_type_int,
            revision=player.revision, 
            origin=player.origin)

        connection.execute(query)
    except IntegrityError:
        print("dup key for resource_id")

    try:
        query = db.insert(nation_table).values(nation=player.nation, 
            nation_img=player.nation_img)
        connection.execute(query)
    except IntegrityError:
        print("dup key for nation")

    try:
        query = db.insert(club_table).values(club=player.club,
            club_img=player.club_img,
            league=player.league)
        connection.execute(query)
    except IntegrityError:
        print("dup key for club")


    try:
        query = db.insert(player_stats_table)
        values_dict = copy.deepcopy(player.player_stats_json)
        values_dict["resource_id"]=player.resource_id
        connection.execute(query,values_dict)
    except IntegrityError:
        print("dup key for stats")

    try:
        query = db.insert(player_usage_table)
        values_dict = copy.deepcopy(player.usage_ingame_stats)
        values_dict["resource_id"]=player.resource_id
        connection.execute(query,values_dict)
    except IntegrityError:
        print("dup key for usage")


    print("-----------Finish One------------------!")



url_template = "https://www.futbin.com/21/player/{}"

for i in range(800, 802):
    url = url_template.format(i)
    try:
        insert_one(url)
    except Exception:
        print("Skip " + url)
        print("-----------Skip One------------------!")

