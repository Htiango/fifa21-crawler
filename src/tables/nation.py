from sqlalchemy import Table, Column, String


class Nation():
    def __init__(self, metadata):
        self._table_name = "nation"
        self.table = \
            Table(self._table_name, metadata,
                Column("nation", String(64), primary_key=True, unique=True),
                Column("nation_img", String(255), nullable=False))
    
    def get_table_name(self):
        return self._table_name
