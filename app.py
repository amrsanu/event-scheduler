"""Gui for event scheduling.
"""
import sys
import threading
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLineEdit,
    QDateTimeEdit,
    QComboBox,
)

from events import (
    Event,
    EventScheduler,
    EventOccurence,
    DB_NAME,
)


class EventSchedulerApp(QMainWindow):
    """App for event scheduling."""

    def __init__(self, db_name):
        super().__init__()

        self.db_name = db_name
        self.event_scheduler = EventScheduler(db_name)
        self.scheduler_thread = threading.Thread(
            target=self.event_scheduler.run_scheduler
        )
        self.scheduler_thread.daemon = True

        self.setWindowTitle("Event Scheduler")
        self.setGeometry(100, 100, 400, 250)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.event_name_input = QLineEdit(self)
        self.event_name_input.setPlaceholderText("Event Name")
        self.layout.addWidget(self.event_name_input)

        self.event_datetime_input = QDateTimeEdit(self)
        self.event_datetime_input.setDateTime(datetime.now())
        self.layout.addWidget(self.event_datetime_input)

        self.repeat_options = QComboBox(self)
        self.repeat_options.addItem("Doesn't repeat")
        self.repeat_options.addItem(EventOccurence.DAILY)
        self.repeat_options.addItem(EventOccurence.WEEKLY)

        self.layout.addWidget(self.repeat_options)

        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.clicked.connect(self.add_event)
        self.layout.addWidget(self.add_event_button)

        self.central_widget.setLayout(self.layout)

    def add_event(self):
        """Add event using GUI widget"""
        event_name = self.event_name_input.text()
        event_time = self.event_datetime_input.dateTime().toString("hh:mm")
        repeat_option = self.repeat_options.currentText()

        event = Event(event_name, event_time, repeat_option)
        self.event_scheduler.add_event(event)

    def run(self):
        """Invoke the background thread to keep looking for events."""
        self.scheduler_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    event_scheduler_app = EventSchedulerApp(DB_NAME)
    event_scheduler_app.show()
    event_scheduler_app.run()
    print("Scheduler started...")
    sys.exit(app.exec_())
