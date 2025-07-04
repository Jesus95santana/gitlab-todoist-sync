# GitLab Todoist Notification Sync

Automate your GitLab workflow by syncing activity notifications from all your GitLab repositories into Todoist as tasks.
Easily track code reviews, comments, merges, and more — right from your task manager.

---

## Features

- Polls all GitLab projects you have access to, using your Personal Access Token (PAT)
- Stores events in a local SQLite database for persistence and de-duplication
- Modular, maintainable structure: each feature is a helper in its own file
- Sends new GitLab activity as tasks to a Todoist project ("GitLab Notifications" or any project you choose)
- Flexible: Customize polling interval, task labels, priorities, and more

---

## Project Structure

```
gitlab-todoist-sync/
│
├── main.py                   # Main orchestrator (calls helpers in order)
├── .env                      # Configuration file (tokens, DB location, etc)
├── README.md
├── gitlab/
│   ├── __init__.py
│   ├── connection.py         # Handles GitLab connection/auth
│   ├── create_gitlab_notifications_db.py
│   ├── poll_gitlab_notifications_db.py
│
├── todoist/
│   ├── __init__.py
│   ├── connection.py         # Handles Todoist connection/auth
│   ├── create_todoist_task.py
│   ├── create_todoist_project.py
│   ├── poll_todoist_notification_db.py
```

---

## Requirements

- Python 3.8+
- [pip](https://pip.pypa.io/) (or pipenv, optional)
- Accounts/tokens for both [GitLab](https://gitlab.com/) and [Todoist](https://todoist.com/)

---

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/gitlab-todoist-sync.git
   cd gitlab-todoist-sync
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Copy and edit the `.env-sample` file:**

   ```env-sample
   # .env example
   GITLAB_URL=https://gitlab.com
   PRIVATE_TOKEN=your_gitlab_pat_token
   GITLAB_NOTIFICATIONS_DB_FILE=gitlab_notifications.db
   GITLAB_POLL_INTERVAL=60

   TODOIST_TOKEN=your_todoist_api_token
   TODOIST_NOTIFICATION_PROJECT_NAME=GitLab Notifications
   ```

---

## Usage

1. **Initialize the database (first time only):**

   ```bash
   python3 main.py
   ```
