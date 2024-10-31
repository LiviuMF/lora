from datetime import datetime

import sqlite3

from models import LHT65, LHTClientView


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
            from_date: str,
            to_date: str
    ):
        from_date = from_date or '1900-01-01'
        to_date = to_date or datetime.now().date().isoformat()
        sql_query = (
            "SELECT * FROM temperature "
            f"WHERE dev_eui = '{appliance_id}' AND "
            f"date >= DATE('{from_date}') AND "
            f"date <= DATE('{to_date}') "
            "ORDER BY date DESC, time DESC;"
        )

        rows = self.cursor.execute(sql_query)
        return [LHT65(**row) for row in rows]

    def fetch_records_last_24hours(
            self,
            appliance_id: str,
):
        sql_query = (
            "SELECT temperature.date, MAX(temperature.time) as time, tempc_ds "
            "FROM temperature "
            "WHERE "
                f"dev_eui = '{appliance_id}' AND "
                "DATE(date) >= DATE('now', '-1 day') "
            "GROUP BY temperature.date, strftime('%H', TIME(temperature.time)) "
            "ORDER BY DATE(temperature.date) DESC, TIME(temperature.time) DESC "
            "LIMIT 24;"
        )
        rows = self.cursor.execute(sql_query)
        return [LHTClientView(**row) for row in rows]

    def save(self, sensor_data: LHT65):
        sensor_dict = sensor_data.__dict__
        insert_values = "', '".join(sensor_dict.values())
        sql_query = (
                    f"INSERT INTO temperature {tuple(sensor_dict.keys())} "
                    f"VALUES('{insert_values}');"
        )
        self.cursor.execute(sql_query)
        self.conn.commit()
