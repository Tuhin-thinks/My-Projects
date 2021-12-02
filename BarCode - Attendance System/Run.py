import re
from datetime import datetime
import sys
import os

from PyQt5.QtWidgets import (QMainWindow, QApplication, QMessageBox, QShortcut, QTableWidgetItem, QFileDialog,
                             QInputDialog)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QUrl

from UI import home_page
from Lib import image_capture, manage_settings
from Lib.db_operations import main_db

DB_NAME = "mydatabase.sqlite"  # default value
main_db.initialization(DB_NAME)
BASE = os.path.dirname(__file__)  # directory for the Run.py file [This script]
FRAME_CAPTURE_LIMIT = 20  # default value (effective when settings.json file is not present)
DISPLAY_DATE = "Current Date" # display preference for date [show all rows or current date rows, Ctrl + Shift + P]

# settings folder and file
json_folder_path = os.path.realpath(os.path.join(BASE, 'Lib/data'))
if not os.path.exists(json_folder_path):
    os.mkdir(json_folder_path)  # create the settings folder
json_file_path = os.path.join(os.path.join(json_folder_path, 'settings.json'))


def update_globals():
    """
    Update global variables (also updates json storage)
    :return:
    """
    global DB_NAME
    global FRAME_CAPTURE_LIMIT

    if os.path.exists(json_file_path):
        data = manage_settings.read_settings(json_file_path)
        FRAME_CAPTURE_LIMIT = data['FRAME_COUNT_LIMIT']
        db_path = data['db_path']
        if os.path.exists(db_path):
            DB_NAME = db_path
        else:
            data['db_path'] = DB_NAME
            manage_settings.update_json_file(json_file_path, data)
        print("settings restored:", data)


def decide_check_type(l_checkin: str, l_checkout: str):
    """
    compares last check in and check-out times and decides whether to check-in or check-out at present time
    :param l_checkin:
    :param l_checkout:
    :return:
    """
    if l_checkout and l_checkin:  # none of them are blanks or none
        checkin_obj = datetime.strptime(l_checkin, "%H:%M")
        checkout_obj = datetime.strptime(l_checkout, "%H:%M")

        if checkin_obj > checkout_obj:
            return "checked in"
        else:
            return "checked out"
    else:
        if not l_checkout:
            return "checked in"
        elif not l_checkin:
            return "checked out"


def OpenFile(parent, title, preferred_dir=None):
    """
    Opens File dialog, where you can set data base path
    :param parent:
    :param title:
    :param preferred_dir:
    :return:
    """
    options = QFileDialog.Options()
    if preferred_dir is None:
        preferred_dir = QUrl.fromLocalFile(os.getcwd())
    fileName, _ = QFileDialog.getOpenFileUrl(parent, caption=title, directory=preferred_dir, options=options)
    fileName: QUrl
    if fileName and _:
        file_name_string = QUrl.toLocalFile(fileName)
        if file_name_string:
            return file_name_string
        else:
            print(file_name_string, "returned None")
            return None
    else:
        return None


def showMessage(message_text, message_type):
    """
    Function to show message box pop-up, it can be 'information', 'error' or "warning"
    :param message_text:
    :param message_type:
    :return:
    """
    if message_type == 'info':
        message = QMessageBox(QMessageBox.Information, "Info", message_text, QMessageBox.Ok)
        res = message.exec_()
        if res == QMessageBox.Ok:
            message.close()
    elif message_type == 'warning':
        message = QMessageBox(QMessageBox.Warning, 'Warning', message_text, QMessageBox.Close)
        res = message.exec_()
        if res == QMessageBox.Close:
            message.close()

    elif message_type == 'error':
        message = QMessageBox(QMessageBox.Critical, 'Error', message_text, QMessageBox.Retry)
        res = message.exec_()
        if res == QMessageBox.Retry:
            message.close()


def check_date_eligibility(date_string):
    """
    Check if current date matches the given date string
    :param date_string:
    :return:
    """
    today_date_string = datetime.today().strftime("%d-%m-%Y")
    if today_date_string != date_string and DISPLAY_DATE != 'All':
        return 0
    else:
        if DISPLAY_DATE == 'All':
            return 1
        else:
            return 1


class AppHome(QMainWindow):
    def __init__(self):
        super(AppHome, self).__init__()
        self.ui = home_page.Ui_MainWindow()
        self.ui.setupUi(self)

        self.attendance_columns = [
            'id', 'date', 'employee_code', 'check_in', 'check_out',
            'last_checkin', 'last_checkout'
        ]

        self.employee_columns = [
            'id', 'name', 'code'
        ]
        # update_globals()
        # gui initializations
        self.ui.statusbar.showMessage("Settings Loaded")
        self.ui.tableWidget_db.verticalHeader().setVisible(False)
        self.ui.tableWidget_db.setColumnCount(len(self.attendance_columns))

        # shortcuts
        self.reload_action = QShortcut(QKeySequence("Ctrl+Shift+R"), self)
        self.reload_action.activated.connect(self.update_attendance_table)

        self.date_display_action = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        self.date_display_action.activated.connect(self.date_display_preference)

        # slots
        self.ui.pushButton_cam.clicked.connect(self.open_cam)
        self.ui.actionSet_Data_Base_Path.triggered.connect(self.update_path)
        self.ui.actionSet_Frame_Capture_count.triggered.connect(self.frame_capture)
        self.update_attendance_table()  # this will update date also

    def frame_capture(self):
        """
        updated the user preference for frame capture limit, effective immediately from next capture
        :return:
        """
        global FRAME_CAPTURE_LIMIT
        user_input, _ = QInputDialog().getInt(self, "Input Limit", "Set Frame Capture Limit", min=5, max=100)
        if user_input and _:
            self.update_path(user_input)
        FRAME_CAPTURE_LIMIT = user_input

    def update_path(self, frame_capture_limit=None):
        """
        Updates data base path [Date base preferably created by this scripts (was copied some where) or db file created by same schema
        effective immediately, updates attendance table]
        :param frame_capture_limit:
        :return:
        """
        global DB_NAME
        if not frame_capture_limit:
            file_url = OpenFile(self, "Save Data Base File")
            if file_url:
                setting_dict = {
                    'db_path': file_url,
                    'FRAME_COUNT_LIMIT': FRAME_CAPTURE_LIMIT
                }
                manage_settings.update_json_file(json_file_path, setting_dict)
                DB_NAME = file_url
                self.update_attendance_table()
        else:
            setting_dict = {
                'db_path': DB_NAME,
                'FRAME_COUNT_LIMIT': frame_capture_limit
            }
            manage_settings.update_json_file(json_file_path, setting_dict)

    def open_cam(self):
        """
        Open camera and capture barcode data from live streaming feed
        :return:
        """
        self.ui.pushButton_cam.setDisabled(True)  # disable open cam button
        self.ui.statusbar.showMessage("Scanning Barcode...", 2*1000)
        image_capture.main(FRAME_CAPTURE_LIMIT, self.capture_data)
        # self.capture_data(data)
        self.ui.pushButton_cam.setEnabled(True)  # enable open cam button

    def capture_data(self, data: bytes):
        """
        Press the camera button

        :description: decides, whether to check in the employee or check out and update the data base and display table
        :param data:
        :return:
        """
        if not data == b'':
            self.ui.statusbar.showMessage("Barcode Scanned Successfully...")
            # showMessage(f"Barcode scanned : code: <h5>{data.decode('utf-8')}</h5>", 'info')
            time_text = datetime.now().strftime("%H:%M")

            check_data = main_db.fetch_employee_row(DB_NAME, data.decode('utf-8'))
            if check_data:
                check_type_decision = decide_check_type(check_data[0], check_data[1])
                if check_type_decision == 'checked in':
                    check_type = 'checkout'  # this is the type for what employee is doing now [get decision based on
                    # previous entry, predict the opposite]
                else:
                    check_type = 'checkin'
                res, message = main_db.check_if_employee(DB_NAME, data.decode('utf-8'), check_type=check_type,
                                                         time_text=time_text)
                if res:
                    pattern = "\<h5\>(.*)<\/h5>"
                    name = re.findall(pattern, message)[0]
                    showMessage(message, 'info')
                    self.update_attendance_table()
                    self.ui.statusbar.showMessage(f"{name} has "
                                                  f"{'checked out' if check_type == 'checkout' else 'checked in'}")
                else:
                    showMessage(f"No Employee Found with code : <h5>{data.decode('utf-8')}<h5>", 'warning')
            else:
                check_type = 'checkin'  # if no records found for todays date, do checkin
                res, message = main_db.check_if_employee(DB_NAME, data.decode('utf-8'), check_type=check_type,
                                                         time_text=time_text)
                if res:
                    pattern = "\<h5\>(.*)<\/h5>"
                    name = re.findall(pattern, message)[0]
                    showMessage(message, 'info')
                    self.update_attendance_table()
                    self.ui.statusbar.showMessage(f"{name} has "
                                                  f"{'checked out' if check_type == 'checkout' else 'checked in'}")
                else:
                    showMessage(f"No Employee Found with code : <h5>{data.decode('utf-8')}<h5>", 'warning')

    def update_attendance_table(self):
        """
        Updates the attendance table and the date (Ctrl + Shift + R)
        :return:
        """
        self.ui.statusbar.showMessage("Updating Attendance Table View...")
        conn = main_db.create_connection(DB_NAME)
        self.ui.tableWidget_db.clear()
        self.ui.tableWidget_db.clearContents()
        row_count = self.ui.tableWidget_db.rowCount()
        while row_count >= 0:
            self.ui.tableWidget_db.removeRow(row_count)
            row_count -= 1
        res = main_db.fetchfromdb(conn, 'Attendance', False)

        header_write_flag = 1  # variable prevents header from being writen more than once
        checked_in = 0
        tot_employees = main_db.count_entries(DB_NAME, "Employees")
        if res:
            for row in res:
                table_rows = self.ui.tableWidget_db.rowCount()
                if table_rows == 0 and header_write_flag:  # set the header for the table
                    for column_index, column_name in enumerate(self.attendance_columns):
                        self.ui.tableWidget_db.setHorizontalHeaderItem(column_index, QTableWidgetItem(str(column_name)))
                        header_write_flag = 0
                    self.ui.tableWidget_db.horizontalHeader().setVisible(True)

                self.ui.tableWidget_db.insertRow(table_rows)
                check_type = decide_check_type(row[5], row[6])
                if check_type == 'checked in':
                    checked_in += 1
                for value_index, value in enumerate(row):
                    if value_index == 1:
                        eligibility = check_date_eligibility(str(value))
                        if eligibility:
                            pass
                        else:
                            self.ui.tableWidget_db.removeRow(table_rows)  # remove added row
                            checked_in -= (1 if checked_in else 0)
                            continue  # break the loop to skip adding more columns (go to next row)
                    try:
                        self.ui.tableWidget_db.setItem(table_rows, value_index, QTableWidgetItem(str(value)))
                        self.ui.tableWidget_db.item(table_rows, value_index). \
                            setToolTip(f"employee has:{check_type}")

                    except AttributeError:
                        pass

            self.ui.statusbar.showMessage("Attendance table view updated...")
        self.ui.label_date.setText(f'Date:<h5>{datetime.today().strftime("%d-%m-%Y")}<h5>')

        header_display = f"""\
<html><head/>
  <body>
  <p>
    <span style=" color:#327498;">Total Employees:</span>
    <span style=" color:#000000;">{tot_employees}</span>
  </p>
  <p>
    <span style=" color:#327498;">Checked in:</span>
    <span style=" color:#000000;">{checked_in}</span>
  </p>
  </body>
</html>
        """
        self.ui.label_info_header.setText(header_display)
        self.update()

    def date_display_preference(self):
        """
        Updates date display preference, whether you want to show all rows or rows matches the current date?
        (Ctrl + Shift + P)
        :return:
        """
        res, _ = QInputDialog().getItem(self, "Set the display preference for \"dates\"",
                                        "Set you date display, preference, All displays all rows, "
                                        "current date displays rows for only today", ["All",
                                                                                      "Current "
                                                                                      "Date"])
        if res and _:
            global DISPLAY_DATE
            if res != 'All':
                DISPLAY_DATE = "Current Date"
            else:
                DISPLAY_DATE = "All"
            self.ui.statusbar.showMessage(f"Date display Preference update to \"{DISPLAY_DATE}\"")
            self.update_attendance_table()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppHome()
    window.show()
    sys.exit(app.exec_())
#    res = decide_check_type("21:07", "21:09")
#    print(res)
