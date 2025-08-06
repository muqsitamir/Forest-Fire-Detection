
### What Does the Script Do?

This script is designed to intelligently **clean up your database** by deleting "false" events associated with a specific camera. It helps you manage data storage and focus on important events by removing unnecessary entries, but it does so with a specific logic to protect recent data.

Specifically, it targets events that are:

* **Not categorized as a "fire" or "smoke"** event.
* **Not marked as "FEATURED"**.

The script then applies one of two different deletion strategies:

1.  **If there are more than 100 qualifying events in the last 30 days**, the script will delete all qualifying events that are **older than 30 days**.
2.  **If there are 100 or fewer qualifying events in the last 30 days**, the script will delete the **oldest events, keeping the 100 most recent ones**.

---

### How to Use It

The script is run from the command line. You only need to provide the camera's ID to run the script.

#### Required Information

You must provide this one piece of information every time you run the script:

1.  **`camera_id`**: The unique ID number of the camera you want to clean up.

#### The `--delete` Option

By default, the script will **only count** the number of events that meet the deletion criteria. This is a safety feature that allows you to see what will be deleted before actually doing it.

To permanently delete the events, you must add the `--delete` flag to your command.

#### Example Commands

* **To see how many events will be deleted:**
    ```bash
    python manage.py delete_false_events 123
    ```
    *(This command will count the deletable events for camera `123` without deleting them.)*

* **To actually delete the events:**
    ```bash
    python manage.py delete_false_events 123 --delete
    ```
    *(This command will permanently delete the events for camera `123` based on the script's logic.)*