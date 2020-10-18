from sqlalchemy import Table, Column, String, Integer, Float, ForeignKey


class PlayerUsage():
    def __init__(self, metadata):
        self._table_name = "player_usage"
        self.table = \
            Table(self._table_name, metadata,
                Column("resource_id", Integer, 
                    ForeignKey("player_info.resource_id", 
                        onupdate="Cascade", 
                        ondelete="Cascade"), 
                    primary_key=True, nullable=False),
                Column('Games', Integer),
                Column('Goals', Float),
                Column('Assists', Float),
                Column('Yellow', Float),
                Column('Red', Float),
                Column('Top-1-chem', String(32)),
                Column('Top-1-usage', Integer),
                Column('Top-2-chem', String(32)),
                Column('Top-2-usage', Integer),
                Column('Top-3-chem', String(32)),
                Column('Top-3-usage', Integer))
    
    def get_table_name(self):
        return self._table_name
