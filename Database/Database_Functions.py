import sqlite3
from sqlite3 import Error
from datetime import datetime


def create_connection(db):
    try:
        conn = sqlite3.connect(db)
        return conn
    except Error as err:
        print(err)
    return None


def create_tables(conn):
    sql_create_players_table = """ CREATE TABLE IF NOT EXISTS Players (
                                        first_name text, 
                                        last_name text,
                                        email text,
                                        password text, 
                                        balance float,
                                        total_games_played int,
                                        total_wins int,
                                        total_losses int,
                                        total_draws int,
                                        win_loss_ratio float,
                                        account_created timestamp,
                                        last_login timestamp
                                ); """

    try:
        c = conn.cursor()
        c.execute(sql_create_players_table)
    except Error as err:
        print(err)


def insert_new_player(conn, player_data):
    try:
        c = conn.cursor()
        c.executemany(f"INSERT INTO Players (first_name, last_name, email, password, balance, total_games_played, total_wins, total_losses, total_draws, win_loss_ratio, account_created, last_login) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", player_data)
        conn.commit()
    except Error as err:
        print(err)


def verify_credentials(conn, player_data):
    try:
        c = conn.cursor()
        all_player_data = c.execute('SELECT email, password FROM Players').fetchall()

        for email, password in all_player_data:
            if player_data[0][0] == email and player_data[0][1] == password:
                return True

        return False
    except Error as err:
        print(err)


def get_player_data(conn, player_data):
    try:
        c = conn.cursor()
        player = c.execute('SELECT * FROM Players WHERE email=? AND password=?', (player_data[0][0], player_data[0][1])).fetchall()
        return player
    except Error as err:
        print(err)


def update_last_login(conn, player):
    try:
        c = conn.cursor()
        player_data = [(str(datetime.now()), player.email, player.password)]
        conn.executemany("UPDATE Players SET last_login=? WHERE email=? AND password=?", player_data)
        conn.commit()
    except Error as err:
        print(err)


def update_player_data(conn, player):
    try:
        c = conn.cursor()
        player_data = [(player.balance, player.total_games_played, player.total_wins, player.total_losses, player.total_draws, player.get_win_loss_ratio(), player.email, player.password)]
        conn.executemany("UPDATE Players SET balance=?, total_games_played=?, total_wins=?, total_losses=?, total_draws=?, win_loss_ratio=? WHERE email=? AND password=?", player_data)
        conn.commit()
    except Error as err:
        print(err)
