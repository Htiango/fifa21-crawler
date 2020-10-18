from sqlalchemy import Table, Column, String, Integer


class Club():
    def __init__(self, metadata):
        self._table_name = "club"
        self.table = \
            Table(self._table_name, metadata,
                Column("club", String(64), primary_key=True, unique=True),
                Column("club_img", String(255), nullable=False),
                Column("league", String(64), nullable=False))
    
    def get_table_name(self):
        return self._table_name
