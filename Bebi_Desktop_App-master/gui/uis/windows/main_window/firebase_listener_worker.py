from PySide6.QtCore import QObject, QRunnable, Slot



class FirebaseListenerWorker(QRunnable):
    def __init__(self, firebase_listener, main_functions_instance, table_widget):
        super().__init__()
        self.firebase_listener = firebase_listener
        self.main_functions_instance = main_functions_instance
        self.table_widget = table_widget

    @Slot()
    def run(self):
        self.main_functions_instance.refresh_table.emit(self.table_widget)
