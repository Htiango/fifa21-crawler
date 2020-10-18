import logging
import json
import requests

from bs4 import BeautifulSoup
from bs4.element import Tag


class Player:

    def __init__(self, url):
        """Form a complex number.

        url -- Futbin url link
        """
        self.soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        self.url = url
        self.__fetch_card_info()
        self.__fetch_usgae()
        self.__fetch_player_resource_id()
        self.__fetch_player_info()
        self.__fetch_player_stats()

    def __fetch_card_info(self):
        card_info_panel = self.soup.find_all(attrs={"id": "Player-card"})[0]
        self.display_name = card_info_panel.find("div", class_="pcdisplay-name").text
        self.rating = int(card_info_panel.find("div", class_="pcdisplay-rat").text)
        self.pos = card_info_panel.find("div", class_="pcdisplay-pos").text
        self.player_img = card_info_panel.find("div", class_="pcdisplay-picture").img["src"]
        self.nation_img = card_info_panel.find("div", class_="pcdisplay-country").img["src"]
        self.club_img = card_info_panel.find("div", class_="pcdisplay-club").img["src"]
        self.color = card_info_panel["data-level"]
        self.rare_type_int = card_info_panel["data-rare-type"]

    def __fetch_usgae(self):
        usage_panel = self.soup.find("div", class_="card s-bar").find("div", class_="right-s-nav")

        self.usage_ingame_stats = {}

        for child in usage_panel.children:
            if isinstance(child, Tag):
                try: 
                    usage_header = child.find("div", class_="mid-p-nav-t-header").text
                    if (usage_header == 'Games' or 
                        usage_header =='Goals' or 
                        usage_header =="Assists" or 
                        usage_header =='Yellow' or
                        usage_header =='Red'):
                        
                        value_str = child.find("div", class_="ps4-pgp-data").text.strip()
                        try: 
                            if usage_header == 'Games':
                                value_str = value_str.replace(",", "")
                                value = int(value_str)
                            else: 
                                value = float(value_str)
                        except Exception as e:
                            value = 0
                        self.usage_ingame_stats[usage_header] = value

                    elif usage_header == 'Top 3 Chem':
                        ps4_top_chem_ls = []
                        for val in child.find("div", class_="ps4-pgp-data").text.strip().split('\n'):
                            val = val.strip()
                            if len(val) > 0:
                                ps4_top_chem_ls.append(val)
                        for i in range(3):
                            if len(ps4_top_chem_ls) > i+1:
                                value = ps4_top_chem_ls[i+1]
                                key1 = "Top-" + str(i + 1) + "-chem"
                                key2 = "Top-" + str(i + 1) + "-usage"
                                value = value.split("(")
                                chem_type = value[0]
                                chem_percent = int(value[1].split("%")[0])
                                self.usage_ingame_stats[key1] = chem_type
                                self.usage_ingame_stats[key2] = chem_percent
                except Exception as e:
                    continue

    def __fetch_player_resource_id(self):
        page_info_panel = self.soup.find(attrs={"id": "page-info"})
        self.resource_id = int(page_info_panel["data-baseid"])
        self.resource_link = "https://www.futbin.com/21/playerPrices?player={}".format(str(self.resource_id))

    def __fetch_player_info(self):
        info_panel = self.soup.find(attrs={"id": "info_content"})
        self.skills = -1
        self.weak_foot = -1
        self.intl_rep = -1
        self.foot = ""
        self.height = 0
        self.weight = 0
        self.revision = "" 
        self.origin = ""

        for info in info_panel.find_all("tr"):
            title = info.th.text.strip()
            value = info.td.text.strip()

            try:
                if title == "Name":
                    self.full_name = value
                if title == "Club":
                    self.club = value
                if title == "Nation":
                    self.nation = value
                if title == "League":
                    self.league = value
                if title == "Skills":
                    self.skills = int(value)
                if title == "Weak Foot":
                    self.weak_foot = int(value)
                if title == "Intl. Rep":
                    self.intl_rep = int(value)
                if title == "Foot":
                    self.foot = value
                if title == "Height":
                    self.height = int(value[:3])
                if title == "Weight":
                    self.weight = int(value)
                if title == "Revision":
                    self.revision = value
                if title == "Origin":
                    self.origin = value
            except Exception:
                continue


    def __fetch_player_stats(self):
        player_stats_json_panel = self.soup.find_all(attrs={"id": "player_stats_json"})
        self.player_stats_json = json.loads(player_stats_json_panel[1].text.strip())
        self.player_stats_json.pop("test", None)
