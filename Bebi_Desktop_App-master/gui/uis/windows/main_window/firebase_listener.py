from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QThread, Signal, QObject, Slot
import firebase_admin
from firebase_admin import credentials, db

from . functions_main_window import *

from . setup_main_window import *
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

class FirebaseListener(QObject):
    new_user_added = Signal(dict)
    data_changed = Signal(dict, MainFunctions)
    
    application_started = False
    table_widget = None
    main_function = None
    def __init__(self, main_function):
        super().__init__()
        self.main_function = main_function

    def run(self):
        # Reference to the 'users' node in the Realtime Database
        users_ref = db.reference('history')
        # Start listening for changes in the 'users' node
        users_ref.listen(self.process_snapshot)

    
    def set_table_widget(self, table_widget):
        self.table_widget = table_widget
        
    def process_snapshot(self, event):
        print(event.event_type)
        if event.event_type == 'put':
            user_data = event.data
            # print(user_data)
            self.new_user_added.emit(user_data)
            # self.data_changed.emit()
            # MainFunctions.refresh_table(self, self.table_widget)
            self.data_changed.emit(user_data, self.main_function)
            # Check if the application has started before emitting the notification
            if hasattr(self, 'application_started') and self.application_started:
                MainFunctions.show_notification(self, "User Logged In Successfully!!")
                
            else:
                self.application_started = True
                

