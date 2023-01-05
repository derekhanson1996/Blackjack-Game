import PySimpleGUI as sg
from Classes import Player_Class as pc
from Classes import BlackJack_Class as bj
from Database import Database_Functions as dbf
from datetime import datetime
from PIL import Image as im
import io
import re


def validate_account_creation(vals):
    valid_password = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$")
    try:
        if not re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", str(vals[2])):
            sg.popup("Please enter a valid email address\nExample: john_smith@gmail.com", title="Invalid Information")
            return False
        elif not re.search(valid_password, str(vals[3])):
            sg.popup("Please enter a valid password\n\nMust contain 8-20 characters\nMust contain at least 1 letter, number, and special character\nMust contain at least 1 uppercase and lowercase character\nMust not contain any spaces", title="Invalid Information")
            return False
        elif not str(vals[3]) == str(vals[4]):
            sg.popup("Please confirm your password", title="Invalid Information")
            return False
        elif float(vals[5]) < 0:
            sg.popup("Please enter a number greater than 0 for starting balance", title="Invalid Information")
            return False
        else:
            return True
    except ValueError:
        sg.popup("Please enter a number for the starting balance", title="Invalid Information")
        return False


def reset_window(player):
    dealer_cards = [[sg.Image(key="-DEALER CARD 1-"), sg.Image(key="-DEALER CARD 2-"), sg.Image(key="-DEALER CARD 3-"), sg.Image(key="-DEALER CARD 4-"), sg.Image(key="-DEALER CARD 5-"), sg.Image(key="-DEALER CARD 6-")]]
    player_cards = [[sg.Image(key="-PLAYER CARD 1-"), sg.Image(key="-PLAYER CARD 2-"), sg.Image(key="-PLAYER CARD 3-"), sg.Image(key="-PLAYER CARD 4-"), sg.Image(key="-PLAYER CARD 5-"), sg.Image(key="-PLAYER CARD 6-")]]
    game_layout = [
        [sg.Column(dealer_cards), sg.Push()],
        [sg.Text(key="-DEALER POINTS-", font=("Helvetica", 18), pad=(100, 0))],
        [sg.VPush()],
        [sg.Push(), sg.Column(player_cards)],
        [sg.Push(), sg.Text(key="-PLAYER POINTS-", font=("Helvetica", 18), pad=(150, 0))],
        [sg.Text(f"Balance: ${float(player.balance):.2f}", key="-BALANCE-", font=("Helvetica", 14))],
        [sg.Text(f"Bet Amount: $0.00", key="-BET AMOUNT-", font=("Helvetica", 14))],
        [sg.In(enable_events=True, key="-BET-", size=(18, 5))],
        [sg.Button("Place Bet", size=(15, 2)), sg.Button("Increase Balance", size=(15, 2)), sg.Push(), sg.Button("Hit", disabled=True, size=(15, 2), pad=(0, 20)), sg.Button("Stand", disabled=True, size=(15, 2)), sg.Push(), sg.Button("Exit", size=(15, 2))]
    ]
    return sg.Window("Hanson's Casino", game_layout, size=(1200, 700), enable_close_attempted_event=True)


def play_game(player):
    game = bj.BlackJack()
    game.shuffle_deck()
    has_blackjack = False
    game_started = False
    database = "hanson_casino.db"
    conn = dbf.create_connection(database)

    game_window = reset_window(player)

    while True:
        event, values = game_window.read()

        if event == "Exit" or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            if game_started:
                sg.popup("You cannot leave while a game has started!", title="Cannot Exit")
            else:
                break

        if event == "Increase Balance":
            deposit = sg.popup_get_text("How much would you like to deposit?", title="Deposit Funds")
            try:
                if float(deposit) > 0:
                    if deposit is not None:
                        deposit = "{:.2f}".format(float(deposit))
                        player.add_money(float(deposit))
                        game_window["-BALANCE-"].update(f"Balance: ${float(player.balance):.2f}")

                        if conn is not None:
                            dbf.update_player_data(conn, player)
                        else:
                            sg.popup("Can't connect to database!", title="Can't Connect")
                else:
                    sg.popup("Please enter a number greater than 0", title="Invalid Bet Amount")
            except ValueError:
                sg.popup("Please enter a number for the deposit amount", title="Invalid Character Entered")

        if event == "Place Bet":
            try:
                if float(values["-BET-"]) > 0:
                    if float(values["-BET-"]) > player.balance:
                        sg.popup("Cannot bet more than your balance, please deposit more funds to continue playing.", title="Insufficient Balance")
                    else:
                        game_started = True
                        values["-BET-"] = "{:.2f}".format(float(values["-BET-"]))
                        game.place_bet(values["-BET-"])
                        player.remove_money(float(game.bet_amount))
                        game_window["-BET AMOUNT-"].update(f"Bet Amount: ${float(game.bet_amount):.2f}")
                        game_window["-BALANCE-"].update(f"Balance: ${float(player.balance):.2f}")
                        game_window["Hit"].update(disabled=False)
                        game_window["Stand"].update(disabled=False)
                        game_window["Place Bet"].update(disabled=True)
                        game_window["Increase Balance"].update(disabled=True)

                        game.player_hand.append(next(game.draw_card()))
                        game.dealer_hand.append(next(game.draw_card()))
                        game.player_hand.append(next(game.draw_card()))
                        player_points = game.calculate_points(game.player_hand)
                        dealer_points = game.calculate_points(game.dealer_hand)

                        has_ace = re.findall("/", player_points)
                        if has_ace:
                            if int(player_points.split("/")[1]) == 21:
                                has_blackjack = True
                                game_window.write_event_value("Stand", None)

                        player_card_1 = im.open(f"Images/{game.player_hand[0]}.png")
                        dealer_card_1 = im.open(f"Images/{game.dealer_hand[0]}.png")
                        player_card_2 = im.open(f"Images/{game.player_hand[1]}.png")
                        dealer_card_2 = im.open("Images/back_of_card.png")
                        player_card_1.thumbnail((200, 200))
                        dealer_card_1.thumbnail((200, 200))
                        player_card_2.thumbnail((200, 200))
                        dealer_card_2.thumbnail((200, 200))
                        bio1 = io.BytesIO()
                        bio2 = io.BytesIO()
                        bio3 = io.BytesIO()
                        bio4 = io.BytesIO()
                        player_card_1.save(bio1, format="PNG")
                        dealer_card_1.save(bio2, format="PNG")
                        player_card_2.save(bio3, format="PNG")
                        dealer_card_2.save(bio4, format="PNG")
                        game_window["-PLAYER CARD 1-"].update(data=bio1.getvalue())
                        game_window["-DEALER CARD 1-"].update(data=bio2.getvalue())
                        game_window["-PLAYER CARD 2-"].update(data=bio3.getvalue())
                        game_window["-DEALER CARD 2-"].update(data=bio4.getvalue())
                        game_window["-PLAYER POINTS-"].update(f"{str(player.first_name)}: {player_points}")
                        game_window["-DEALER POINTS-"].update(f"Dealer: {dealer_points}")
                else:
                    sg.popup("Please enter a number greater than 0", title="Invalid Bet Entered")
            except ValueError:
                sg.popup("Please enter a number for the bet amount", title="Invalid Character Entered")

        if event == "Hit":
            game.player_hand.append(next(game.draw_card()))
            card = im.open(f"Images/{game.player_hand[len(game.player_hand) - 1]}.png")
            card.thumbnail((200, 200))
            bio1 = io.BytesIO()
            card.save(bio1, format="PNG")
            game_window[f"-PLAYER CARD {len(game.player_hand)}-"].update(data=bio1.getvalue())
            player_points = game.calculate_points(game.player_hand)
            game_window["-PLAYER POINTS-"].update(f"{str(player.first_name)}: {player_points}")

            has_ace = re.findall("/", player_points)
            if not has_ace:
                if int(player_points) > 21:
                    game.game_result = game.GAME_RESULTS[1]
                    player.update_total_losses()
                    player.update_games_played()

                    game.dealer_hand.append(next(game.draw_card()))
                    card = im.open(f"Images/{game.dealer_hand[len(game.dealer_hand) - 1]}.png")
                    card.thumbnail((200, 200))
                    bio1 = io.BytesIO()
                    card.save(bio1, format="PNG")
                    game_window[f"-DEALER CARD {len(game.dealer_hand)}-"].update(data=bio1.getvalue())
                    dealer_points = game.calculate_points(game.dealer_hand)
                    game_window["-DEALER POINTS-"].update(f"Dealer: {dealer_points}")
                    sg.popup(f"You lost.\nYou Won ${float(game.calculate_winnings()):.2f}", title="Winnings")

                    if conn is not None:
                        dbf.update_player_data(conn, player)
                    else:
                        sg.popup("Can't connect to database!", title="Can't Connect")

                    game_window.close()
                    game.new_game()
                    game_started = False
                    game_window = reset_window(player)

        if event == "Stand":
            game_window["Hit"].update(disabled=True)
            game_window["Stand"].update(disabled=True)
            dealer_points = game.calculate_points(game.dealer_hand)
            player_points = game.calculate_points(game.player_hand)

            has_ace = re.findall("/", player_points)
            if has_ace:
                player_points = player_points.split("/")[1]
                game_window["-PLAYER POINTS-"].update(f"{str(player.first_name)}: {player_points}")

            has_ace = re.findall("/", dealer_points)
            if has_ace:
                dealer_points = dealer_points.split("/")[0]

            while int(dealer_points) < 17:
                game.dealer_hand.append(next(game.draw_card()))
                card = im.open(f"Images/{game.dealer_hand[len(game.dealer_hand) - 1]}.png")
                card.thumbnail((200, 200))
                bio1 = io.BytesIO()
                card.save(bio1, format="PNG")
                game_window[f"-DEALER CARD {len(game.dealer_hand)}-"].update(data=bio1.getvalue())
                dealer_points = game.calculate_points(game.dealer_hand)

                has_ace = re.findall("/", dealer_points)
                if has_ace:
                    if int(dealer_points.split("/")[1]) >= 17:
                        dealer_points = dealer_points.split("/")[1]
                    else:
                        dealer_points = dealer_points.split("/")[0]

                game_window["-DEALER POINTS-"].update(f"Dealer: {dealer_points}")

            if int(player_points) < int(dealer_points) <= 21:
                game.game_result = game.GAME_RESULTS[1]
                player.update_total_losses()
                result_string = "You Lost.\nYou Won $"
            elif int(dealer_points) == int(player_points):
                game.game_result = game.GAME_RESULTS[2]
                player.update_total_draws()
                result_string = "Draw.\nYou Won $"
            elif has_blackjack:
                if int(dealer_points) == int(player_points):
                    game.game_result = game.GAME_RESULTS[2]
                    player.update_total_draws()
                    result_string = "Draw.\nYou Won $"
                else:
                    game.game_result = game.GAME_RESULTS[3]
                    player.update_total_wins()
                    result_string = "BlackJack!\nYou Won $"
            else:
                game.game_result = game.GAME_RESULTS[0]
                player.update_total_wins()
                result_string = "You Won!\nYou Won $"

            winnings = game.calculate_winnings()
            winnings = "{:.2f}".format(float(winnings))
            sg.popup(result_string + str(winnings), title="Winnings")
            player.update_games_played()
            player.add_money(float(winnings))

            if conn is not None:
                dbf.update_player_data(conn, player)
            else:
                sg.popup("Can't connect to database!", title="Can't Connect")

            game_window.close()
            game.new_game()
            has_blackjack = False
            game_started = False
            game_window = reset_window(player)

    conn.close()
    game_window.close()


def returning_account():
    database = "hanson_casino.db"
    conn = dbf.create_connection(database)

    login = [
        [sg.Text("Email", size=(15, 1)), sg.In(enable_events=True)],
        [sg.Text("Password", size=(15, 1)), sg.In(password_char="*", enable_events=True)]
    ]

    returning_account_layout = [
        [sg.VPush()],
        [sg.Push(), sg.Column(login, element_justification='c'), sg.Push()],
        [sg.VPush()],
        [sg.Push(), sg.Button("Login", size=(15, 2), bind_return_key=True), sg.Push(),  sg.Button("Back to Main Menu", size=(15, 2)), sg.Push()],
        [sg.VPush()]
    ]

    returning_account_window = sg.Window("Login", returning_account_layout, size=(400, 200))

    while True:
        event, values = returning_account_window.read()

        if event == "Back to Main Menu" or event == sg.WIN_CLOSED:
            break

        if event == "Login":
            player_info = [(values[0], values[1])]

            if conn is not None:
                valid_player = dbf.verify_credentials(conn, player_info)
                if valid_player:
                    player_data = dbf.get_player_data(conn, player_info)
                    player = pc.Player(player_data[0][0], player_data[0][1], player_data[0][2], player_data[0][3], player_data[0][4], player_data[0][5], player_data[0][6], player_data[0][7], player_data[0][8])
                    dbf.update_last_login(conn, player)
                    returning_account_window.close()
                    play_game(player)
                else:
                    sg.popup("Invalid Credentials, please try again!", title="Invalid Credentials")
            else:
                sg.popup("Can't connect to database!", title="Can't Connect")

    conn.close()
    returning_account_window.close()


def create_account():
    database = "hanson_casino.db"
    conn = dbf.create_connection(database)

    account_creation = [
        [sg.Text("First Name", size=(15, 1)), sg.In(enable_events=True)],
        [sg.Text("Last Name", size=(15, 1)), sg.In(enable_events=True)],
        [sg.Text("Email", size=(15, 1)), sg.In(enable_events=True)],
        [sg.Text("Password", size=(15, 1)), sg.In(enable_events=True, password_char="*")],
        [sg.Text("Confirm Password", size=(15, 1)), sg.In(enable_events=True, password_char="*")],
        [sg.Text("Starting Balance    $", size=(15, 1)), sg.In(enable_events=True)]
    ]

    account_creation_layout = [
        [sg.VPush()],
        [sg.Push(), sg.Column(account_creation, element_justification='c'), sg.Push()],
        [sg.VPush()],
        [sg.Push(), sg.Button("Create", size=(15, 2), bind_return_key=True), sg.Push(), sg.Button("Back to Main Menu", size=(15, 2)), sg.Push()],
        [sg.VPush()]
    ]

    account_creation_window = sg.Window("Create Account", account_creation_layout, size=(400, 300), finalize=True)

    while True:
        event, values = account_creation_window.read()

        if event == "Back to Main Menu" or event == sg.WIN_CLOSED:
            break

        if event == "Create":
            if validate_account_creation(values):
                values[5] = "{:.2f}".format(float(values[5]))
                player_data = [(values[0], values[1], values[2], values[3], values[5], "0", "0", "0", "0", "0.0", str(datetime.now()), "N/A")]

                if conn is not None:
                    dbf.create_tables(conn)
                    dbf.insert_new_player(conn, player_data)
                else:
                    sg.popup("Can't connect to database!", title="Can't Connect")

                sg.popup("Account Created Successfully!", title="Account Created")
                account_creation_window.close()
                returning_account()

    conn.close()
    account_creation_window.close()


sg.theme("DarkAmber")

main_menu = [
    [sg.Text("Welcome to Hanson's Casino!", font=("Helvetica", 16), pad=(0, 10))],
    [sg.Button("Returning User"), sg.Button("New User")],
    [sg.Button("Exit", size=(21, 2), pad=(0, 30))]
]

layout = [
    [sg.VPush()],
    [sg.Push(), sg.Column(main_menu, element_justification='c'), sg.Push()],
    [sg.VPush()]
]

window = sg.Window("Welcome", layout, size=(400, 200))

while True:
    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "New User":
        window.hide()
        create_account()
        window.un_hide()

    elif event == "Returning User":
        window.hide()
        returning_account()
        window.un_hide()

window.close()
