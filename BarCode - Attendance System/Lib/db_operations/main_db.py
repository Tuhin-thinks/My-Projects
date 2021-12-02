import sqlite3
from datetime import datetime
from sqlite3 import Error

from . import decide_check_type
evening, night = datetime.strptime("18:00", "%H:%M"), datetime.strptime("00:00", "%H:%M")


# -----------------uncomment below function for testing ---------
#
# def decide_check_type(l_checkin: str, l_checkout: str):
#     """
#     compares last check in and check-out times and decides whether to check-in or check-out at present time
#     :param l_checkin:
#     :param l_checkout:
#     :return:
#     """
#     if l_checkout and l_checkin:  # none of them are blanks or none
#         checkin_obj = datetime.strptime(l_checkin, "%H:%M")
#         checkout_obj = datetime.strptime(l_checkout, "%H:%M")
#
#         if checkin_obj > checkout_obj:
#             return "checked in"
#         else:
#             return "checked out"
#     else:
#         if not l_checkout:
#             return "checked in"
#         elif not l_checkin:
#             return "checked out"


# -------------------------------------------


def create_connection(db_path):
    try:
        con = sqlite3.connect(db_path)
        return con
    except Error:
        pass


def CreateTable(conn, query):
    try:
        cursor_obj = conn.cursor()
        cursor_obj.execute(query)
        conn.commit()
        return True
    except Error:
        return False


def deleterow(db_path, tablename, item_id):  # delete a row in a table
    conn = create_connection(db_path)
    delete_query = f"DELETE FROM {tablename} WHERE id={item_id}"
    cursor_obj = conn.cursor()
    cursor_obj.execute(delete_query)
    conn.commit()
    conn.close()


def insertintotable(conn, query, value):
    cursor = conn.cursor()
    cursor.execute(query, tuple(value))
    conn.commit()
    print('Data Inserted successfully!')


def fetchfromdb(conn, tablename, compare=False, query=None):
    """
    If compare is True then, it'll fetch all rows and all columns
    """
    if not compare:
        query = f"SELECT * FROM {tablename}"
    curson_obj = conn.cursor()
    curson_obj.execute(query)
    rows = curson_obj.fetchall()

    entry_list = []
    for row in rows:
        entry_list.append(row)
    return entry_list


def check_night_shift(cursor, emp_code):
    if emp_code:
        query = "SELECT shift from Employees where code=?"
        cursor.execute(query, emp_code)
        shift_data = cursor.fetchone()
        if shift_data:
            return shift_data[0]
    return None


def initialization(db_name):
    """
    Call this function and database and table will be created
    """
    conn = create_connection(db_name)
    query_create_table_check = "CREATE TABLE IF NOT EXISTS (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, " \
                               "employee_code " \
                               "TEXT, check_in TEXT, check_out TEXT, last_checkin TEXT, last_checkout TEXT)"

    query_create_table_emp = "CREATE TABLE IF NOT EXISTS Employees(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, " \
                             "code TEXT); "

    CreateTable(conn, query_create_table_emp)
    CreateTable(conn, query_create_table_check)
    conn.close()


def do_new_checkin(cursor, today, emp_code, time_text):
    """
    Need to call conn.commit() after this function call to finalize changes
    """
    update_query = f"INSERT INTO Attendance(date, employee_code, check_in, last_checkin) VALUES(?,?,?,?)"
    cursor.execute(update_query, (today, emp_code, time_text, time_text))


def update_attendance(conn, emp_code, check_type, time_text, today=None):
    """
    parameter today is only to be used to override the normal datetime getting process
    for testing purpose.
    """
    cursor = conn.cursor()
    today = datetime.today().strftime("%d-%m-%Y") if not today else today
    fetch_query = f"SELECT * FROM Attendance WHERE date=\"{today}\" AND employee_code=\"{emp_code}\""
    res = fetchfromdb(conn, 'Attendance', True, fetch_query)

    if res:  # if attendance exists
        res = res[0]
        print("attendance for the day found:", res)
        checkin = res[3]
        checkout = res[4]
        l_checkin = res[5]
        l_checkout = res[6]

        if check_type == 'checkin':
            # update last checkin
            update_query = f"UPDATE Attendance SET last_checkin=\"{time_text}\" WHERE id={res[0]}"
            cursor.execute(update_query)
            conn.commit()
            print(f"Last Checkin time updated for empcode: {emp_code}")
        else:  # checkout
            print("Doing checkout...\nres=", res)
            # update final checkout and last checkout

            # update last checkout (lcheckout)
            update_query = f"UPDATE Attendance SET last_checkout=\"{time_text}\" WHERE id={res[0]}"
            cursor.execute(update_query)
            conn.commit()
            # update check out with the difference

            # find (last-checkout - last check-in)
            time_gap_timedelta = datetime.strptime(time_text, "%H:%M") - datetime.strptime(l_checkin, "%H:%M")
            print(f"time gap delta={time_gap_timedelta}")
            # update checkout
            if checkout:
                checkout = (datetime.strptime(checkout, "%H:%M") + time_gap_timedelta).strftime("%H:%M")
            else:
                checkout = time_text
            update_query = f"UPDATE Attendance SET check_out=\"{checkout}\" WHERE id={res[0]}"
            cursor.execute(update_query)
            conn.commit()
    else:  # if first attendance of the day for the employee

        # check if employee has night shifts
        shift = check_night_shift(cursor, (emp_code,))
        print("employee shift:", shift)
        if shift == 'night':
            # get last attendance date for the employee
            fetch_query = "SELECT * FROM Attendance WHERE employee_code=? ORDER BY id DESC"
            cursor.execute(fetch_query, (emp_code,))
            previous_records = cursor.fetchall()
            if previous_records:  # if employee has previous attendances in the database
                check_time = datetime.strptime(time_text, "%H:%M")
                last_record = previous_records[0]
                last_date = last_record[1]
                print(f"last date: {last_date}")
                last_checkin, last_checkout = last_record[5], last_record[6]
                check_type = decide_check_type(last_checkin, last_checkout)
                if check_type == 'checked in':  # means employee has checked in previous night before 12 (now doing check out)
                    if evening < check_time < night:  # check out same day
                        print("Cannot check out, hasn't checked in for current day yet")
                        return
                    else:  # checking out after 12am (night shift start at 12am)
                        print("night shift: updating check out status for previous day.")
                        time_gap_timedelta = check_time - datetime.strptime(last_checkin, "%H:%M")
                        print(f"time gap:{time_gap_timedelta.seconds / 60:.03f} minutes (or"
                              f" {time_gap_timedelta.seconds / 3600:.03f} hrs)")
                        if last_checkout:
                            checkout = (datetime.strptime(last_checkout, "%H:%M") + time_gap_timedelta).strftime(
                                "%H:%M")
                        else:
                            checkout = time_text
                        update_query = "UPDATE Attendance SET check_out=?, last_checkout=? where id=?"
                        print(
                            f"\tupdating to checkout={checkout}, last_checkout={time_text}, where id={last_record[0]}")
                        params = (checkout, time_text, last_record[0])
                        cursor.execute(update_query, params)
                        conn.commit()  # finalize changes
                        print("\tupdated...")
                else:  # check in for first time of the day
                    do_new_checkin(cursor, today, emp_code, time_text)
                    conn.commit()
                    print("night shift: first check-in")
            else:
                do_new_checkin(cursor, today, emp_code, time_text)
                conn.commit()
                print("night shift: first check-in")
        else:
            # update the checkin, l_checkin
            update_query = f"INSERT INTO Attendance(date, employee_code, check_in, last_checkin) VALUES(?,?,?,?)"
            cursor.execute(update_query, (today, emp_code, time_text, time_text))
            conn.commit()
            print("dayshift: updated checkin and last checkin")
    conn.close()


def insert_operation(db_name, query, values: tuple):
    conn = create_connection(db_name)
    insertintotable(conn, query, values)
    conn.close()


def count_entries(db_name, table_name):
    conn = create_connection(db_name)
    query = f"SELECT count(*) from {table_name}"
    cursor = conn.cursor()
    cursor.execute(query)
    count = cursor.fetchone()
    return count[0] if type(count) == tuple else "0"


def check_if_employee(db_name, emp_code, table_name='Employees', check=True, check_type='checkin', time_text=None):
    conn = create_connection(db_name)
    fetch_query = f"SELECT * FROM \"Employees\" WHERE \"code\" like \"{emp_code}\""
    flag = 0
    res = fetchfromdb(conn, table_name, compare=True, query=fetch_query)
    if res:
        for row in res:
            update_id = row[0]
            name = row[1]
            emp_code_mod = row[2]
            break
        if emp_code_mod == emp_code:  # employee exists
            if check:
                update_attendance(conn, emp_code, check_type, time_text)
                flag = 1
                conn.close()
                return 1, f"Updated Attendance for Employee: <h5>{name}</h5>"
    conn.close()
    return 0, ""


def fetch_employee_row(db_path: str, code: str, mode="Attendance"):
    """
    If mode is Attendance, it fetch any existing column for the employee from the attendance table,
    else fetches from the Employees tables
    :param db_path: path to data base file
    :param code: str [Employee code]
    :param mode: str [options: Attendance or Employees]
    :return:
    """
    date_string = datetime.today().strftime("%d-%m-%Y")
    fetch_query = f"SELECT last_checkin, last_checkout FROM Attendance WHERE date=\"{date_string}\" AND employee_code=\"{code}\""
    conn = create_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(fetch_query)
    data_list = cursor.fetchall()
    conn.close()  # close existing db connection
    if data_list:
        return data_list[0]
    else:
        return None


if __name__ == '__main__':
    pass
    # conn = create_connection('../../mydatabase.sqlite')
    # update_attendance(conn, "87843515646", 'checkin', "07:30", "13-03-2021")
    # update_attendance(conn, "87843515646", 'checkout', "01:10", "14-03-2021")
    """
    After running above two lines the database at the main directory will have it's "checkout" time updated for
    employee "87843515646" for the date 13-03-2021
    """
