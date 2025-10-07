import os
import requests
from datetime import datetime

# --- Configuration ---
ASANA_PAT = os.getenv('ASANA_PAT')
PROJECT_GID = os.getenv('PROJECT_GID')

# --- Pre-flight Check ---
if not all([ASANA_PAT, PROJECT_GID]):
    print("Error: Ensure ASANA_PAT and PROJECT_GID are set.")
    exit(1)

# --- API Setup & Global Constants ---
HEADERS = {
    "Authorization": f"Bearer {ASANA_PAT}",
    "Accept": "application/json"
}
TASKS_URL = f"https://app.asana.com/api/1.0/projects/{PROJECT_GID}/tasks"
DATE_FORMAT = "%Y-%m-%d"

# --- Helper Functions ---
def get_subtasks(parent_task_gid):
    """Fetches all subtasks for a given parent task."""
    subtask_url = f"https://app.asana.com/api/1.0/tasks/{parent_task_gid}/subtasks"
    response = requests.get(subtask_url, headers=HEADERS, params=all)
    response.raise_for_status()
    print(response.json()['data'])
    return response.json()['data']

def update_parent_task_dates(task_gid, start_date, due_date):
    """Updates the start and due dates of the parent task."""
    update_url = f"https://app.asana.com/api/1.0/tasks/{task_gid}"
    
    payload_data = {}
    if start_date:
        payload_data['start_on'] = start_date.strftime(DATE_FORMAT)
    if due_date:
        payload_data['due_on'] = due_date.strftime(DATE_FORMAT)

    if not payload_data:
        return

    payload = {"data": payload_data}
    response = requests.put(update_url, headers=HEADERS, json=payload)
    response.raise_for_status()
    print(f"  - Synced dates for parent GID {task_gid} to Start: {payload_data.get('start_on')}, Due: {payload_data.get('due_on')}.")

# --- Main Logic ---
def main():
    """Fetches parent tasks and syncs their dates based on their subtasks."""
    print("Starting Asana parent task date sync...")
    
    params = {
        "completed_since": "now",
        "opt_fields": "name,start_on,due_on,num_subtasks"
    }
    
    try:
        response = requests.get(TASKS_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        tasks = response.json()['data']
        
        print(f"Found {len(tasks)} non-completed parent tasks to check.")
        
        for task in tasks:
            if task['num_subtasks'] > 0:
                task_gid = task['gid']
                task_name = task['name']
                print(f"-> Checking subtasks for '{task_name}'...")
                
                subtasks = get_subtasks(task_gid)
                
                earliest_start, latest_due = None, None
                
                for subtask in subtasks:
                    start_str, due_str = subtask.get('start_on'), subtask.get('due_on')
                    
                    if start_str:
                        current_start = datetime.strptime(start_str, DATE_FORMAT).date()
                        if earliest_start is None or current_start < earliest_start:
                            earliest_start = current_start
                            
                    if due_str:
                        current_due = datetime.strptime(due_str, DATE_FORMAT).date()
                        if latest_due is None or current_due > latest_due:
                            latest_due = current_due
                
                parent_start_str = task.get('start_on')
                parent_due_str = task.get('due_on')
                parent_start = datetime.strptime(parent_start_str, DATE_FORMAT).date() if parent_start_str else None
                parent_due = datetime.strptime(parent_due_str, DATE_FORMAT).date() if parent_due_str else None
                
                update_needed = False
                if (earliest_start and earliest_start != parent_start) or \
                   (latest_due and latest_due != parent_due):
                    update_needed = True
                
                if update_needed:
                    update_parent_task_dates(task_gid, earliest_start, latest_due)

    except requests.exceptions.RequestException as e:
        print(f"An API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    print("Asana date sync check complete.")

if __name__ == "__main__":
    main()
