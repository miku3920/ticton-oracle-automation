import os
from dotenv import load_dotenv
import asyncio

import mysql.connector as connector
import mysql.connector.errors as Error

load_dotenv()

MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


async def create_connection():
    try:
        connection = connector.connect(
            host=os.getenv("MYSQL_HOST"),  # Assuming MariaDB is running on localhost
            database=os.getenv("MYSQL_DATABASE"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Successfully connected to MariaDB server version ", db_info)
            return connection
        else:
            print("Failed to connect to MariaDB server")
            return None
    except Error as e:
        print("Error while connecting to MariaDB", e)
        return None


async def init():
    connection = await create_connection()
    if connection is not None and connection.is_connected():
        cursor = connection.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS your_table (
            id INT PRIMARY KEY,
            address VARCHAR(255),
            state VARCHAR(100),
            price DECIMAL(10, 2)
        )
        """
        cursor.execute(create_table_sql)
        connection.commit()
        connection.close()


async def get_alarm_from_db():
    try:
        connection = await create_connection()
        if connection is not None and connection.is_connected():
            cursor = connection.cursor()
            select_sql = "SELECT * FROM %s"
            cursor.execute(select_sql, [MYSQL_DATABASE])
            result = {}
            for id, address, state, price in cursor.fetchall():
                result[id] = {}
                result[id]["address"] = address
                result[id]["state"] = state
                result[id]["price"] = price

            cursor.close()
            connection.close()
            return result

    except Error as e:
        print("Error while getting alarm info", e)
        return None


async def update_alarm_to_db(alarm_dict):
    try:
        if alarm_dict is None:
            return None
        connection = await create_connection()
        if connection is not None and connection.is_connected():
            cursor = connection.cursor()
            update_sql = """
            INSERT INTO %s (id, address, state, price)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE address = VALUES(address), state = VALUES(state), price = VALUES(price)
            """
            insert_list = []
            for alarm_id, alarm_info in alarm_dict.items():
                insert_list.append(
                    (
                        MYSQL_DATABASE,
                        alarm_id,
                        alarm_info["address"],
                        alarm_info["state"],
                        alarm_info["price"],
                    )
                )
            cursor.executemany(update_sql, insert_list)
            connection.commit()
            cursor.close()
            connection.close()
            print("Successfully updated alarm info")

    except Error as e:
        print("Error while updating alarm info", e)


if __name__ == "__main__":
    asyncio.run(init())
