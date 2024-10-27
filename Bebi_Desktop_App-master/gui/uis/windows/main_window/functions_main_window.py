# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

# IMPORT PACKAGES AND MODULES
# ///////////////////////////////////////////////////////////////
import sys

# IMPORT QT CORE
# ///////////////////////////////////////////////////////////////
from qt_core import *

# LOAD UI MAIN
# ///////////////////////////////////////////////////////////////
from . ui_main import *

from . setup_main_window import *

from firebase_admin import firestore, storage, db

from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from plyer import notification
from . firebase_listener import *


# FUNCTIONS
class MainFunctions(QObject):
    table_widget = None
    def __init__(self):
        super().__init__()
        # SETUP MAIN WINDOw
        # Load widgets from "gui\uis\main_window\ui_main.py"
        # ///////////////////////////////////////////////////////////////
        # self.ui = UI_MainWindow()
        # self.ui.setup_ui(self)
    
    def set_table_widget(self, table_widget):
        self.table_widget = table_widget
        
    
        
    def browse_image(self, edit_line):
        # Open a file dialog to select an image
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        file_dialog.setViewMode(QFileDialog.Detail)
        
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            edit_line.setText(selected_file)
            # self.show_selected_image(selected_file)


    def confirm_user(self, name, image_path):
        if name and image_path:
            try:
                # Add user data to Firebase Realtime Database
                dbs = firestore.client()
                users_ref = dbs.collection(u'Users')
                ref = db.reference('Users')
                id = 1
                while id < 30:
                    if ref.child(str(id)).get() is not None:
                        id += 1
                        print(id)
                    else: break
                
                
                # Create a new document with an auto-generated ID
                new_user_ref = users_ref.add({
                    u'name': name,
                    u'photo': f"https://storage.googleapis.com/systemsecuritybebi.appspot.com/UsersPhotos/{name.replace(' ', '_')}.png"
                })

                # Get the auto-generated document ID
                document_id = new_user_ref[1].id
                print(f"User added successfully with Document ID: {document_id}")

                # Upload user image to Cloud Storage
                bucket = storage.bucket()
                blob = bucket.blob(f"UsersPhotos/{document_id}.png")
                blob.upload_from_filename(image_path, content_type="image/png")
                print("Image uploaded successfully")
                download_url = blob.public_url
                print(f"Image uploaded successfully. Download URL: {download_url}")
                
                user_metadata = {
                    "photo": blob.public_url,  # The URL of the uploaded photo
                    "name": name
                }
                
                # Push the metadata to the database
                user_ref = ref.child(str(id))
                user_ref.set(user_metadata)
                MainFunctions.show_notification(self, "User Added Successfully!")

            except Exception as e:
                print(f"Error confirming user: {e}")

        else:
            print("Please enter a name and choose a picture.")

    def show_notification(self, msg):
        title = "Bebi - Security System"
        message = msg

        notification.notify(
            title=title,
            message=message,
            app_icon=None,  # e.g., 'C:\\icon_32x32.ico' (path to your custom icon)
            timeout=3,  # Notification timeout in seconds
            toast=False  # Set to True for Windows Toast Notifications (Windows 8 and 10)
        )

    # @Slot()
    # def updateTableInMainThread(self):
    #     MainFunctions.refresh_table(self, self.table_widget)
        
    def refresh_table(self):
        updated_data = []
        # Fetch updated data
        updated_data = MainFunctions.fetch_history_from_firebase(self, "")

        # Populate the table with updated data
        self.populate_table(updated_data, self.table_widget)
    
    def populate_table(self, new_data, table_widget):
        font = QFont()
        font.setPointSize(16)
        self.data = []
        # Append new data to the existing data list
        # self.data.extend(new_data)
        self.data = new_data
        # Populate the table with all data
        table_widget.setRowCount(len(self.data))
        print(len(self.data))
        for row_number, user in enumerate(self.data):
            # row_number = table_widget.rowCount()
            # table_widget.insertRow(row_number) # Insert row
            
            item = QTableWidgetItem(user["name"])
            table_widget.setItem(row_number, 0, item)
            
            item.setFont(font)
            
            # self.table_widget.setItem(row_number, 0, QTableWidgetItem(str(user["name"]))) # Add name
            # self.table_widget.setItem(row_number, 1, QTableWidgetItem(str(user["time"]))) # Add time
            
            item = QTableWidgetItem(user["time"])
            table_widget.setItem(row_number, 1, item)
            item.setFont(font)
            file_path = MainFunctions.convert_gcs_to_firebase_url(self, str(user["url"]))
            self.download_image(file_path, row_number, 2, self.table_widget)
            
            table_widget.verticalHeader().setSectionResizeMode(row_number, QHeaderView.Fixed)
            table_widget.verticalHeader().setDefaultSectionSize(200)
        
    def fetch_history_from_firebase(self, name):
        ref = db.reference("/history")
        bucket = storage.bucket()
        results = [item for item in ref.get() if item is not None]
        
        history_list = []
        for id in results:
            child_ref = ref.child(id)
            data = child_ref.get()
            
            history_list.append(data)
        # Read data from the child
            
        return history_list
    def download_image(self, url, row, col, table):
        
        self.manager = QNetworkAccessManager(self)
        request = QNetworkRequest(QUrl(url))
        reply = self.manager.get(request)
        
        reply.finished.connect(lambda: MainFunctions.add_image_to_cell(self, row, col, table, reply))
        
        
    def add_image_to_cell(self, row, col, table, reply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # self.image_label.setPixmap(pixmap)
            # pixmap = QPixmap(image_path).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Create a label and set the pixmap
            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            # item = QTableWidgetItem()
            table.setCellWidget(row, col, label)

    def convert_gcs_to_firebase_url(self, gcs_url):
        # Split the GCS URL to extract the bucket and object path
        parts = gcs_url.split("/")
        bucket = parts[3]
        object_path = "/".join(parts[4:])
        object_path = object_path.split("/")
        object_path = object_path[0] + "%2F" + object_path[1]
        # print(object_path)

        # Construct the Firebase Storage URL
        firebase_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o/{object_path}?alt=media"

        return firebase_url

    



    # SET MAIN WINDOW PAGES
    # ///////////////////////////////////////////////////////////////
    def set_page(self, page):
        self.ui.load_pages.pages.setCurrentWidget(page)

    # SET LEFT COLUMN PAGES
    # ///////////////////////////////////////////////////////////////
    def set_left_column_menu(
        self,
        menu,
        title,
        icon_path
    ):
        self.ui.left_column.menus.menus.setCurrentWidget(menu)
        self.ui.left_column.title_label.setText(title)
        self.ui.left_column.icon.set_icon(icon_path)

    # RETURN IF LEFT COLUMN IS VISIBLE
    # ///////////////////////////////////////////////////////////////
    def left_column_is_visible(self):
        width = self.ui.left_column_frame.width()
        if width == 0:
            return False
        else:
            return True

    # RETURN IF RIGHT COLUMN IS VISIBLE
    # ///////////////////////////////////////////////////////////////
    def right_column_is_visible(self):
        width = self.ui.right_column_frame.width()
        if width == 0:
            return False
        else:
            return True

    # SET RIGHT COLUMN PAGES
    # ///////////////////////////////////////////////////////////////
    def set_right_column_menu(self, menu):
        self.ui.right_column.menus.setCurrentWidget(menu)

    # GET TITLE BUTTON BY OBJECT NAME
    # ///////////////////////////////////////////////////////////////
    def get_title_bar_btn(self, object_name):
        return self.ui.title_bar_frame.findChild(QPushButton, object_name)

    # GET TITLE BUTTON BY OBJECT NAME
    # ///////////////////////////////////////////////////////////////
    def get_left_menu_btn(self, object_name):
        return self.ui.left_menu.findChild(QPushButton, object_name)
    
    # LEDT AND RIGHT COLUMNS / SHOW / HIDE
    # ///////////////////////////////////////////////////////////////
    def toggle_left_column(self):
        # GET ACTUAL CLUMNS SIZE
        width = self.ui.left_column_frame.width()
        right_column_width = self.ui.right_column_frame.width()

        MainFunctions.start_box_animation(self, width, right_column_width, "left")

    def toggle_right_column(self):
        # GET ACTUAL CLUMNS SIZE
        left_column_width = self.ui.left_column_frame.width()
        width = self.ui.right_column_frame.width()

        MainFunctions.start_box_animation(self, left_column_width, width, "right")

    def start_box_animation(self, left_box_width, right_box_width, direction):
        right_width = 0
        left_width = 0
        time_animation = self.ui.settings["time_animation"]
        minimum_left = self.ui.settings["left_column_size"]["minimum"]
        maximum_left = self.ui.settings["left_column_size"]["maximum"]
        minimum_right = self.ui.settings["right_column_size"]["minimum"]
        maximum_right = self.ui.settings["right_column_size"]["maximum"]

        # Check Left Values        
        if left_box_width == minimum_left and direction == "left":
            left_width = maximum_left
        else:
            left_width = minimum_left

        # Check Right values        
        if right_box_width == minimum_right and direction == "right":
            right_width = maximum_right
        else:
            right_width = minimum_right       

        # ANIMATION LEFT BOX        
        self.left_box = QPropertyAnimation(self.ui.left_column_frame, b"minimumWidth")
        self.left_box.setDuration(time_animation)
        self.left_box.setStartValue(left_box_width)
        self.left_box.setEndValue(left_width)
        self.left_box.setEasingCurve(QEasingCurve.InOutQuart)

        # ANIMATION RIGHT BOX        
        self.right_box = QPropertyAnimation(self.ui.right_column_frame, b"minimumWidth")
        self.right_box.setDuration(time_animation)
        self.right_box.setStartValue(right_box_width)
        self.right_box.setEndValue(right_width)
        self.right_box.setEasingCurve(QEasingCurve.InOutQuart)

        # GROUP ANIMATION
        self.group = QParallelAnimationGroup()
        self.group.stop()
        self.group.addAnimation(self.left_box)
        self.group.addAnimation(self.right_box)
        self.group.start()
        
    