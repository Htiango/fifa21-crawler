import argparse
import copy
import json
import logging
import logging.config
import requests
import sqlalchemy as db
import sys
import traceback
import time

from bs4 import BeautifulSoup
from player import Player
from tables.club import Club
from tables.nation import Nation
from tables.player_info import PlayerInfo
from tables.player_stats import PlayerStats
from tables.player_usage import PlayerUsage
from sqlalchemy.exc import IntegrityError


logging.config.fileConfig(fname='logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
CRAWL_PAGE = "https://www.futbin.com"


logger.info("START!")
logger.info("Reading credentials.......")
with open('credentials.json', 'r') as f:
    config = json.load(f)

user = config['user']
password = config["password"]
host = config["host"]
database = config["db"]
logger.info("Loaded credentials!")

connect_str_template = "mysql+pymysql://{user}:{password}@{host}/{db}"
connect_str = connect_str_template.format(user=user, 
                                          password=password,
                                          host=host,
                                          db=database)

logger.info("Connecting to MySQL database........")
engine = db.create_engine(connect_str)
connection = engine.connect()
metadata = db.MetaData()
logger.info("Connected to database!")

logger.info("Creating tables if not exist........")
player_info_table = PlayerInfo(metadata).table
club_table = Club(metadata).table
nation_table = Nation(metadata).table
player_stats_table = PlayerStats(metadata).table
player_usage_table = PlayerUsage(metadata).table

metadata.create_all(engine)
logger.info("Created tables!")


def timeit(method):
    """
    decorator function to calculate the time
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        time_ms = "{:.2f}ms".format((te - ts) * 1000)
        logger.info("Time finishing {}: {}".format(method, time_ms))
        return result
    return timed

@timeit
def fetch_one(url):
    logger.info("Crawling......")
    try:
        player = Player(url)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(repr(traceback.format_exception(exc_type, exc_value,
            exc_traceback)))
        logger.error(e)
        logger.error("Failed to crawl for page: {}".format(url))

    logger.info("Crawled Player: " + player.display_name)

    logger.info("Inserting data into player_info table.....")
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
        logger.info("Inserted successfully!")
    except IntegrityError:
        logger.warning("dup key for player_info table, skipped")
    

    logger.info("Inserting data into nation table.....")
    try:
        query = db.insert(nation_table).values(nation=player.nation, 
            nation_img=player.nation_img)
        connection.execute(query)
        logger.info("Inserted successfully!")
    except IntegrityError:
        logger.warning("dup key for nation table")

    logger.info("Inserting data into club table.....")
    try:
        query = db.insert(club_table).values(club=player.club,
            club_img=player.club_img,
            league=player.league)
        connection.execute(query)
        logger.info("Inserted successfully!")
    except IntegrityError:
        logger.warning("dup key for club table, skipped")

    logger.info("Inserting data into player_stats table.....")
    try:
        query = db.insert(player_stats_table)
        values_dict = copy.deepcopy(player.player_stats_json)
        values_dict["resource_id"]=player.resource_id
        connection.execute(query,values_dict)
        logger.info("Inserted successfully!")
    except IntegrityError:
        logger.warning("dup key for player_stats table, skipped")

    logger.info("Inserting data into player_usage table.....")
    try:
        query = db.insert(player_usage_table)
        values_dict = copy.deepcopy(player.usage_ingame_stats)
        values_dict["resource_id"]=player.resource_id
        connection.execute(query,values_dict)
        logger.info("Inserted successfully!")
    except IntegrityError:
        logger.warning("dup key for player_usage table")

    logger.info("Finish inserting data into all tables!")


@timeit
def fetch_page(page_num):
    page_url = "https://www.futbin.com/players?page={}".format(page_num)
    response = requests.get(page_url)
    if response.status_code == 403:
        logger.error("YOU ARE BANNED BY FUTBIN!!!!!!!")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    link_panels = soup.find_all("a", class_="player_name_players_table")
    for link_panel in link_panels:
        url_suffix = link_panel["href"]
        url = CRAWL_PAGE + url_suffix
        try:
            logger.info("Start crawling on: {}".format(url))
            fetch_one(url)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(repr(traceback.format_exception(exc_type, exc_value, 
                exc_traceback)))
            logger.error(e)
            logger.error("Encountering errors while fetching one for page {}".format(url))
            logger.warning("Skipped for page {}".format(url))


def fetch_save_player_links(page_start, page_end):
    url_ls = []
    for page_num in range(page_start, page_end + 1):
        page_url = "https://www.futbin.com/players?page={}".format(page_num)
        response = requests.get(page_url)
        if response.status_code == 403:
            logger.error("YOU ARE BANNED BY FUTBIN!!!!!!!")
            return
        soup = BeautifulSoup(response.content, 'html.parser')
        link_panels = soup.find_all("a", class_="player_name_players_table")
        for link_panel in link_panels:
            url_suffix = link_panel["href"]
            url = CRAWL_PAGE + url_suffix
            url_ls.append(url)
        logger.info("Finsh page {}".format(page_num))
        time.sleep(2)
    with open("player_links.json", "w") as f:
        json.dump(url_ls, f)
    return len(url_ls)


def fetch_stats():
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--crawel_version', type=str, required=True, 
        help='Crawl what?', choices=["links", "stats", "all"])
    parser.add_argument('-s', '--page_start', type=int, default=1, 
        help='Crawel page start')
    parser.add_argument('-e', '--page_end', type=int, default=2, 
        help='Crawel page end')

    args = parser.parse_args()

    if args.crawel_version == "links":
        fetch_save_player_links(args.page_start, args.page_end)
    elif args.crawel_version == "stats":
        fetch_stats()
    else:
        fetch_save_player_links(args.page_start, args.page_end)
        fetch_stats()


if __name__ == "__main__":
    main()

