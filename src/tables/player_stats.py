from sqlalchemy import Table, Column, String, Integer, ForeignKey


class PlayerStats():
    def __init__(self, metadata):
        self._table_name = "player_stats"
        self.table = \
            Table(self._table_name, metadata,
                Column("resource_id", Integer, 
                    ForeignKey("player_info.resource_id", 
                        onupdate="Cascade", 
                        ondelete="Cascade"), 
                    primary_key=True, nullable=False),
                Column('ppace', Integer),
                Column('pshooting', Integer),
                Column('ppassing', Integer),
                Column('pdribbling', Integer),
                Column('pdefending', Integer),
                Column('pphysical', Integer),
                Column('acceleration', Integer),
                Column('sprintspeed', Integer),
                Column('agility', Integer),
                Column('balance', Integer),
                Column('reactions', Integer),
                Column('ballcontrol', Integer),
                Column('dribbling', Integer),
                Column('positioning', Integer),
                Column('finishing', Integer),
                Column('shotpower', Integer),
                Column('longshotsaccuracy', Integer),
                Column('volleys', Integer),
                Column('penalties', Integer),
                Column('interceptions', Integer),
                Column('headingaccuracy', Integer),
                Column('marking', Integer),
                Column('standingtackle', Integer),
                Column('slidingtackle', Integer),
                Column('vision', Integer),
                Column('crossing', Integer),
                Column('freekickaccuracy', Integer),
                Column('shortpassing', Integer),
                Column('longpassing', Integer),
                Column('curve', Integer),
                Column('jumping', Integer),
                Column('stamina', Integer),
                Column('strength', Integer),
                Column('aggression', Integer),
                Column('composure', Integer))
    
    def get_table_name(self):
        return self._table_name
