from typing import Any

import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from binance_bot.configs.main_config import DatabaseConfig
from binance_bot.constants import KlineProps


class DatabaseClient:

    def __init__(self, database_config: DatabaseConfig):
        self.conf = database_config

    def _execute_autocommit_statement(self, statement: str) -> None:
        _con = psycopg2.connect(
            host=self.conf.host,
            port=self.conf.port,
            user=self.conf.user,
            password=self.conf.password
        )
        _con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        _con.cursor().execute(statement)

    def _create_database(self) -> None:
        self._execute_autocommit_statement(f"CREATE database {self.conf.dbname}")

    def _drop_database(self) -> None:
        self._execute_autocommit_statement(f"DROP database {self.conf.dbname}")

    def recreate_database(self):
        try:
            self._drop_database()
        except psycopg2.errors.InvalidCatalogName:
            pass
        finally:
            self._create_database()

    def get_database_connection(self) -> Any:
        return psycopg2.connect(
            host=self.conf.host,
            port=self.conf.port,
            dbname=self.conf.dbname,
            user=self.conf.user,
            password=self.conf.password
        )

    @staticmethod
    def create_klines_table(db_con: Any, pair: str) -> None:
        _cur = db_con.cursor()
        _cur.execute(f"CREATE TABLE {pair} ("
                     f"{KlineProps.TIME_OPEN} BIGINT, "
                     f"{KlineProps.OPEN} NUMERIC, "
                     f"{KlineProps.HIGH} NUMERIC, "
                     f"{KlineProps.LOW} NUMERIC, "
                     f"{KlineProps.CLOSE} NUMERIC, "
                     f"{KlineProps.VOLUME} NUMERIC)")
        db_con.commit()
        _cur.close()

    @staticmethod
    def insert_klines_into_table(db_con: Any, pair: str, data: pd.DataFrame) -> None:
        _cur = db_con.cursor()
        for row in data.values:
            _cur.execute(f"INSERT INTO {pair} VALUES (%s, %s, %s, %s, %s, %s)", row)
        db_con.commit()
        _cur.close()

    @staticmethod
    def read_table(pair: str, db_con: Any) -> pd.DataFrame:
        return pd.read_sql_query(f"SELECT * from {pair}", db_con)
