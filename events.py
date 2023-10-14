"""To create a GUI with following capabilities.
1. Create events with date and Time.
2. Get notifications for the events at scheduled time.
"""

import os
import time

import sqlite3
import schedule
from plyer import notification

DB_NAME = "events.db"
ICON = "clock.png"


class EventOccurence:
    DAILY = "daily"
    WEEKLY = "weekly"
    YEARLY = "Yearly"


class Event:
    """To have event date, time and details."""

    def __init__(self, event_name, event_time, event_occurence):
        self.event_name = event_name
        self.event_time = event_time
        self.event_occurence = event_occurence


class EventScheduler:
    """To schedule the events and have the notification."""

    def __init__(self, db_name):
        self.events = []
        self.db_name = db_name
        self.setup_database()
        self.load_events_from_database()

    def setup_database(self):
        """Setup database for the fist time"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_name TEXT,
                event_time TEXT,
                event_occurence  TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def add_event(self, event):
        """Add a new event
        Args:
            event (_type_): _description_
        """
        self.events.append(event)
        self.save_event_to_database(event)
        self.schedule_notifications(event)

    def remove_event(self, event):
        """Remove the event from the database

        Args:
            event (_type_): _description_
        """
        self.events.remove(event)
        self.delete_event_from_database(event)

    def schedule_notifications(self, event):
        """Schedule the event."""
        print("Schedule notification...")
        print(f"Event: {event.event_name} {event.event_time}")
        if event.event_occurence == EventOccurence.DAILY:
            schedule.every(1).day.at(event.event_time).do(
                self.display_notification, event
            )
        elif event.event_occurence == EventOccurence.WEEKLY:
            schedule.every(1).week.at(event.event_time).do(
                self.display_notification, event
            )
        else:
            schedule.every().day.at(event.event_time).do(
                self.display_notification, event
            )
        # TODO: Add check for the EventOccurence.

    def get_scheduled_notifications(self):
        """Get details of scheduled notifications."""
        scheduled_jobs = schedule.get_jobs()
        print(scheduled_jobs)
        return scheduled_jobs

    def display_notification(self, event):
        """Displat the event

        Args:
            event (Event): Event object with time and details.
        """
        notification.notify(
            title="Event Reminder",
            message=f"{event.event_name} is happening now!",
            app_name="EventScheduler",
            timeout=10,
            toast=True,
            # app_icon=ICON,
        )
        self.remove_event(event)

    def load_events_from_database(self):
        """To load the saved events from the DB"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT event_name, event_time, event_occurence FROM events")
            for row in cursor.fetchall():
                event = Event(row[0], row[1], row[2])
                self.add_event(event)
            conn.close()
        except sqlite3.Error as e:
            print(f"Error loading events from the database: {e}")

    def save_event_to_database(self, event):
        """Dave the event to the DB

        Args:
            event (Event): Event to save
        """

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (event_name, event_time, event_occurence) VALUES (?, ?, ?)",
                (event.event_name, event.event_time, event.event_occurence),
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error saving event to the database: {e}")

    def delete_event_from_database(self, event):
        """Delete the event from the database

        Args:
            event (_type_): Event to delete
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM events WHERE event_name = ? AND event_time = ? AND event_occurence =?",
                (event.event_name, event.event_time, event.event_occurence),
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error deleting event from the database: {e}")

    def run_scheduler(self):
        """Start the scheduler loop in a separate thread"""
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    scheduler = EventScheduler(DB_NAME)

    scheduler.load_events_from_database()
    scheduler.run_scheduler()
