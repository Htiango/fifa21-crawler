from sqlalchemy import Table, Column, String, Integer


class PlayerInfo():
    def __init__(self, metadata):
        self._table_name = "player_info"
        self.table = \
            Table(self._table_name, metadata,
                Column("resource_id", Integer, primary_key=True, nullable=False),
                Column("rating", Integer, nullable=False),
                Column("pos", String(16), nullable=False),
                Column('full_name', String(128), nullable=False),
                Column("display_name", String(64), nullable=False),
                Column("player_img", String(255), nullable=False),
                Column("nation", String(64), nullable=False),
                Column("club", String(64), nullable=False),
                Column("league", String(64), nullable=False),
                Column("url", String(255), nullable=False),
                Column("skills", Integer),
                Column("weak_foot", Integer),
                Column("intl_rep",Integer),
                Column("foot", String(16)),
                Column("height", Integer),
                Column("weight", Integer),
                Column("color", String(32)),
                Column("rare_type_int", Integer),
                Column("revision", String(32)),
                Column("origin", String(32)))
    
    def get_table_name(self):
        return self._table_name
