import sqlite3

from models import LHT65


class DatabaseClient:
    conn = sqlite3.connect('temperature.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    dtypes = " TEXT, ".join(LHT65.__annotations__.keys())
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS '
        f'temperature ({dtypes} TEXT);'
    )

    def fetch_records_for_appliance(
            self,
            appliance_id: str,
            from_date: str
    ):
        sql_query = (
            "SELECT * FROM temperature "
            f"WHERE dev_eui = '{appliance_id}' AND "
            f"date >= DATE('{from_date}') "
            "ORDER BY date DESC, time DESC "
        )
        rows = self.cursor.execute(sql_query)
        return [LHT65(**row) for row in rows]

    def save(self, sensor_data: LHT65):
        sensor_dict = sensor_data.__dict__
        insert_values = "', '".join(sensor_dict.values())
        sql_query = (
                    f"INSERT INTO temperature {tuple(sensor_dict.keys())} "
                    f"VALUES('{insert_values}');"
        )
        self.cursor.execute(sql_query)
        self.conn.commit()
