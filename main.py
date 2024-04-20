import csv
import mysql.connector

# Fancy database stuff
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="testdatabase"
)

def create_table():
    cursor = db.cursor()

    # create the table
    cursor.execute("CREATE TABLE Cars (id INT PRIMARY KEY AUTO_INCREMENT, "
                   "mpg FLOAT, "
                   "cylinders FLOAT, "
                   "engine FLOAT, "
                   "horsepower FLOAT, "
                   "weight FLOAT, "
                   "acceleration FLOAT, "
                   "year FLOAT, "
                   "origin VARCHAR(50), "
                   "name VARCHAR(50))")

    # Reading the file, skip the header, use csv.reader to read through it.
    # For each element in each row, if the element is nan, turn it to zero.
    # Try to convert the element to float, otherwise keep it as a string
    with open("Car performance data.csv", "r") as file:
        next(file)
        f = csv.reader(file)
        for x in f:
            for y in range(len(x)):
                if x[y] == 'nan':
                    x[y] = 0
                try:
                    x[y] = float(x[y])
                except:
                    continue
            cursor.execute("INSERT INTO Cars (mpg, cylinders, engine, horsepower, weight, acceleration, year, origin, name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8]))

    print("Table created!\n")
    db.commit()
    cursor.close()


def drop_table():
    cursor = db.cursor()
    cursor.execute("DROP TABLE Cars")
    print("\nTable destroyed!\n")
    db.commit()
    cursor.close()

def check_exit(term):
    if term == "x":
        print("Going back to menu...")
        return True
    return False


def print_table(mode, rows = None):
    #Case for print full table
    if not rows:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Cars")
        rows = cursor.fetchall()
        cursor.close()

    match mode:
        case 1:
            i = 0
            for x in rows:
                for y in x:
                    print(headers[i].title() + ":", y, end="   ")
                    i += 1
                i = 0
                print()
        case 2:
            i = 0
            print("We found these cars in the table.")
            for x in rows:
                for y in x:
                    print(headers[i].title() + ":", y, end="   ")
                    i += 1
                i = 0
                print()
        case 3:
            i = 0
            for x in rows:
                for y in x:
                    print(headers[i].title() + ":", y, end="   ")
                    i += 1


#Create list of headers for printing
def get_headers():
    cursor = db.cursor()
    cursor.execute("SHOW COLUMNS FROM Cars")
    headers = []

    for x in cursor:
        headers.append(x[0])
    cursor.close()
    return headers


def get_choice():
    choice = 1
    while choice in {1, 2, 3}:
        choice = input("\nInput 1 to view the full table, 2 to search for a term, 3 to change a term, or anything else to quit.\n")

        if choice.isnumeric():
            choice = int(choice)
        else:
            print("Please choose from a given value")
            choice = 1
            continue

        match choice:
            case 1:
                print_table(1)
            case 2:
                while True:
                    if find_value(headers) != 1:
                        break
            case 3:
                change_value()


def find_value(headers):
    cursor = db.cursor()

    print("Choose a parameter from the following list to search under: [OR X TO GO BACK TO MENU]")
    for x in headers:
        print(x, end=" ")

    para = (input("\n")).lower()
    if check_exit(para):
        cursor.close()
        return -1

    while para not in headers:
        para = (input("Please choose one of the listed choices\n")).lower()

    term = input("What value would you like to search for? [OR X TO GO BACK TO MENU]\n")
    if check_exit(term):
        cursor.close()
        return -1

    if term.isnumeric():
        float(term)
    elif para != ("origin" or "name"):
        print("We couldn't find any cars that match this description.")
        retry = input("Enter 1 to retry or any other character to quit.")
        cursor.close()
        return int(retry)

    query = "SELECT * FROM Cars WHERE {} = %s".format(para)
    values = (term,)
    cursor.execute(query, values)

    rows = cursor.fetchall()
    if not rows:
        print("We couldn't find any cars that match this description.")
        retry = input("Enter 1 to retry or any other character to quit.\n")
        cursor.close()
        return int(retry)
    else:
        print_table(2, rows)
    cursor.close()


def change_value():
    while True:
        row = input("Which item would you like to change (by ID)? [OR X TO GO BACK TO MENU]\n")
        if check_exit(row):
            return
        if row.isnumeric():
            int(row)

            cursor = db.cursor()
            query = "SELECT * FROM Cars WHERE id = %s"
            term = (row,)
            cursor.execute(query, term)
            line = cursor.fetchall()
            cursor.close()

            print_table(3, line)

            choice = input("\nIs this the right item? Enter 1 for yes, 2 for no and try again, or anything else to exit.\n")
            try:
                choice = int(choice)
            except:
                continue

            if choice == 1:
                break
            elif choice != 2:
                return
        else:
            print("We couldn't find an item with that ID. Please try again")

    while True:
        print("Choose a parameter from the following list to change: [OR X TO GO BACK TO MENU]")
        for x in headers[1:]:
            print(x, end=" ")

        col = (input("\n")).lower()
        if check_exit(col):
            return

        while col not in headers[1:]:
            col = input("Please choose one of the listed choices [OR X TO GO BACK TO MENU]\n")
            if check_exit(col):
                return

        value = (input("What would you like to change " + col + " to? [OR X TO GO BACK TO MENU]\n")).lower()
        if check_exit(value):
            return

        if col != ("name" or "origin"):
            try:
                value = float(value)
            except:
                print("This is not a valid entry. Please input a numeric value for this parameter.")
                continue
        break

    cursor = db.cursor()
    query = "UPDATE Cars SET {} = %s WHERE id = %s".format(col)
    values = (value, row)
    cursor.execute(query, values)
    query = "SELECT * FROM Cars WHERE id = %s"
    values = (row,)
    cursor.execute(query, values)
    line = cursor.fetchall()
    cursor.close()

    print("The entry has been modified:")
    print_table(3, line)
    print()


###########################################
            # Main Function
###########################################

create_table()
headers = get_headers()
get_choice()
drop_table()