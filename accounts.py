
#/usr/bin/python3
import random
import csv
import sqlite3

class Account:
    def init_db(self):
        conn = sqlite3.connect("accounts.raw")
        curr = conn.cursor()
        try:
            curr.execute('create table test (test_column INTEGER);')
            curr.execute('DROP TABLE test;')
            try:
                curr.execute('create table card (id INTEGER, name TEXT, pin TEXT, balance INTEGER default 0);')
            except sqlite3.OperationalError:
                pass
        except sqlite3.OperationalError:
            curr.execute('DROP TABLE card;')
            curr.execute('create table card (id INTEGER, name TEXT, pin TEXT, balance INTEGER default 0);')
        finally:
            conn.commit()

    def is_match(self,input):
        converting_to_int_list = []
        for item in list(input):
            converting_to_int_list.append(int(item))
        current_card_name = converting_to_int_list[:-1]
        tmp_list = current_card_name.copy()
        for i in range(0, len(tmp_list), 2):
            tmp_list[i] *= 2
            if tmp_list[i] > 9:
                tmp_list[i] -= 9
        checksum = list(str(10 - sum(tmp_list) % 10))
        if len(checksum) != 1:
            checksum = [0]
        current_card_name.extend(checksum)
        del tmp_list
        card_name_for_db = ''.join(map(str, current_card_name))
        if card_name_for_db == input:
            return True
        else:
            return False

    def create_card(self):
        def get_pin():
            pin = ""
            for each in random.sample(range(9), k=4):
                pin += str(each)
            return pin

        conn = sqlite3.connect("accounts.raw")
        curr = conn.cursor()
        iin = [4, 0, 0, 0, 0, 0]
        print("\nEnter the card name you wanna create:\n")
        current_card_name = input()
        card_name_for_db = ''.join(map(str, current_card_name))
        card_pin_for_db = get_pin()
        print("\nYour card has been created")
        print("Your card name:\n{}\nYour card PIN:\n{}\n".format(card_name_for_db, card_pin_for_db))
        curr.execute('SELECT id from card;')
        db_return = curr.fetchall()
        try:
            listofrows = (lambda l: [item for sublist in l for item in sublist])(db_return)
            myid = max(listofrows)
        except ValueError:
            myid = 0
        dontsqlinjectme = (myid, card_name_for_db, card_pin_for_db)
        curr.execute('INSERT INTO card (id, name, pin) VALUES (?, ?, ?);', dontsqlinjectme)
        conn.commit()

    def retrieve_from_db(self,user_enters_card_no, user_enters_pin):
        conn = sqlite3.connect("accounts.raw")
        curr = conn.cursor()
        card_name = user_enters_card_no
        pin = user_enters_pin
        dontsqlinjectme = (card_name, pin)
        curr.execute('SELECT name, pin FROM card WHERE name = ? and pin = ?;', dontsqlinjectme)
        db_return = curr.fetchone()
        match = False
        try:
            if card_name in db_return and pin in db_return:
                match = True
                print("You have successfully logged in!")
        except sqlite3.OperationalError:
            print("\nWrong card name or PIN!\n")
        except TypeError:
            print("\nWrong card name or PIN!\n")
        while match:
            print("1. Balance\n2. Deposit\n3. Withdraw\n4. Transfer money\n5.Log out\n0.Exit")
            second_menu_choice = int(input())
            if second_menu_choice == 1:
                curr.execute('SELECT balance FROM card WHERE name = ? and pin = ?;', (card_name, pin))
                db_return = curr.fetchone()
                print("\nBalance: {}\n".format(db_return[0]))
            elif second_menu_choice == 2:
                print("\nEnter deposit:")
                dontsqlinjectme = (int(input()), card_name, pin)
                curr.execute('UPDATE card SET balance = balance + ? WHERE name = ? and pin = ?;', dontsqlinjectme)
                conn.commit()
                print("Income was added!")
            elif second_menu_choice == 3:
                global user_enters_withdraw
                print("\nEnter how much money you want to withdraw:\n")
                user_enters_withdraw = int(input())
                curr.execute('SELECT balance FROM card WHERE name = ? and pin = ?', (card_name, pin))
                db_return = curr.fetchone()
                if user_enters_withdraw > db_return[0]:
                    print("\nNot enough money!\n")
                    continue
                else:
                    curr.execute('UPDATE card SET balance = balance - ? WHERE name = ?;', (
                            user_enters_withdraw, card_name))
                    conn.commit()
                    print("\nSuccess!\n")
                    continue
            elif second_menu_choice == 4:
                global transfer_destination
                transfer_destination = []
                print("Enter card name:")
                user_enters_transferdest = input()
                if len(user_enters_transferdest) != 16:
                    print("\nProbably you made a mistake in the card name.\nPlease try again!\n")
                    continue
                elif len(user_enters_transferdest) == 16:
                    if user_enters_transferdest == card_name:
                        print("\nYou can't transfer money to the same account!\n")
                        continue
                    elif not self.is_match(user_enters_transferdest):
                        '# IF CHECK INFO RETURNS FALSE. NOT FALSE = TRUE AND THEN WE CONTINUE'
                        print("\nINFO CHECK:Probably you made a mistake in the card name.\nPlease try again!\n")
                        continue
                    else:
                        transfer_destination = (int(user_enters_transferdest),)
                curr.execute('SELECT name FROM card WHERE name = ?;', transfer_destination)
                db_return = curr.fetchone()
                try:
                    len(db_return)
                    print("\nEnter how much money you want to transfer:\n")
                    user_enters_transfermoney = int(input())
                    curr.execute('SELECT balance FROM card WHERE name = ? and pin = ?', (card_name, pin))
                    db_return = curr.fetchone()
                    if user_enters_transfermoney > db_return[0]:
                        print("\nNot enough money!\n")
                        continue
                    else:
                        curr.execute('UPDATE card SET balance = balance + ? WHERE name = ?;', (
                            user_enters_transfermoney, int(user_enters_transferdest)))
                        curr.execute('UPDATE card SET balance = balance - ? WHERE name = ?;', (
                            user_enters_transfermoney, card_name))
                        conn.commit()
                        print("\nSuccess!\n")
                        continue
                except TypeError:
                    print("\nSuch a card does not exist.\n")
                    continue
            elif second_menu_choice == 5:
                print("You have successfully logged out!")
                match = False
            elif second_menu_choice == 0:
                print("Bye!")
                conn.close()
                exit()

    def save_to_csv(self):
        conn = sqlite3.connect("accounts.raw")
        curr = conn.cursor()

        curr.execute('select * from card;')
        columns = [column[0] for column in curr.description]

        with open(f'data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            writer.writerows(curr.fetchall())
        conn.close()


account_current = Account()
status = True
account_current.init_db()
while status:
    print("1. Create an account\n2. Log into account\n3. Exit")
    first_menu_choice = int(input())
    if first_menu_choice == 1:
        account_current.create_card()
    elif first_menu_choice == 2:
        print("Enter your card name:")
        user_enters_card_no = input()
        print("Enter your PIN:")
        user_enters_pin = input()
        account_current.retrieve_from_db(user_enters_card_no, user_enters_pin)
    elif first_menu_choice == 3:
        print("Bye!")
        status = False
        account_current.save_to_csv()
