from datetime import datetime

import sqlite3

from models import DeviceReadings, DeviceReadingsClientView, DeviceData


class DatabaseClient:
    conn = sqlite3.connect('temperature.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    DEV_READINGS_TABLE = DeviceReadings.Meta.table_name
    DEV_DATA_TABLE = DeviceData.Meta.table_name

    dtypes = " TEXT, ".join(DeviceReadings.__annotations__.keys())
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS '
        f'{DEV_READINGS_TABLE} ({dtypes} TEXT);'
    )

    dtypes = " TEXT, ".join(DeviceData.__annotations__.keys())
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS '
        f'{DEV_DATA_TABLE} ({dtypes} TEXT);'
    )

    def fetch_records_for_appliance(
            self,
            appliance_id: str,
            from_date: str = '1900-01-01',
            to_date: str = datetime.now().date().isoformat()
    ):
        sql_query = (
            f"SELECT * FROM {self.DEV_READINGS_TABLE} "
            f"WHERE dev_eui = '{appliance_id}' AND "
            f"date >= DATE('{from_date}') AND "
            f"date <= DATE('{to_date}') "
            "ORDER BY date DESC, time DESC;"
        )
        rows = self.cursor.execute(sql_query)
        return [DeviceReadings(**row) for row in rows]

    def fetch_records_last_24hours(
            self,
            appliance_id: str,
):
        sql_query = (
            f"SELECT {self.DEV_READINGS_TABLE}.date,"
                f"MAX({self.DEV_READINGS_TABLE}.time) as time, "
                "tempc_ds "
            f"FROM {self.DEV_READINGS_TABLE} "
            "WHERE "
                f"dev_eui = '{appliance_id}' AND "
                "DATE(date) >= DATE('now', '-1 day') "
            f"GROUP BY {self.DEV_READINGS_TABLE}.date, strftime('%H', TIME({self.DEV_READINGS_TABLE}.time)) "
            f"ORDER BY DATE({self.DEV_READINGS_TABLE}.date) DESC, TIME({self.DEV_READINGS_TABLE}.time) DESC "
            "LIMIT 24;"
        )
        rows = self.cursor.execute(sql_query)
        return [DeviceReadingsClientView(**row) for row in rows]

    def fetch_all_device_data(self):
        sql_query = (
            f"SELECT * FROM {self.DEV_DATA_TABLE} "
        )
        rows = self.cursor.execute(sql_query)
        return [DeviceData(**row) for row in rows]

    def fetch_all_owners(self):
        sql_query = (
            "SELECT "
                "DISTINCT(dev_owner) as dev_owner, dev_owner_email "
            f"FROM {self.DEV_DATA_TABLE}"
        )
        rows = self.cursor.execute(sql_query)
        return [
            (
                row['dev_owner'],
                row['dev_owner_email']
            )
            for row in rows
        ]

    def fetch_owner_devices(self, dev_owner_name: str):
        sql_query = (
            f"SELECT * FROM {self.DEV_DATA_TABLE} "
            f"WHERE dev_owner = '{dev_owner_name}'"
        )
        rows = self.cursor.execute(sql_query)
        return [DeviceData(**row) for row in rows]

    def remove_device(self, dev_eui: str):
        sql_query = (
            f"DELETE FROM {self.DEV_DATA_TABLE} "
            f"WHERE dev_eui = '{dev_eui}'"
        )
        self.cursor.execute(sql_query)

    def save(self, sensor_data: DeviceReadings or DeviceData):
        sensor_dict = sensor_data.__dict__
        insert_values = "', '".join(sensor_dict.values())
        sql_query = (
            f"INSERT INTO {sensor_data.Meta.table_name} {tuple(sensor_dict.keys())} "
            f"VALUES('{insert_values}');"
        )
        self.cursor.execute(sql_query)
        self.conn.commit()
