# Checkpoint7 : Note Application

A simple but powerful note-taking web application built with Flask and PostgreSQL. This application allows users to create, manage, and organize notes with a flexible tagging system.

## Features

* **Full CRUD for Notes:**
    * **Create:** Add new notes with a title and description.
    * **Read:** View all notes on the main page.
    * **Update:** Edit existing notes to change their content or tags.
    * **Delete:** Remove notes you no longer need.

* **Dynamic Tag Management:**
    * Assign multiple tags to any note using a simple comma-separated list.
    * Tags are automatically created if they don't already exist.
    * View all notes associated with a specific tag.
    * A central "Manage Tags" page to view, edit, and delete all tags.

* **Automatic Tag Garbage Collection:**
    * To keep the tag list clean, the application automatically deletes any tag that is no longer associated with any notes. This happens when:
        * A note is deleted, and it was the only note using a particular tag.
        * A tag is removed from a note during an edit, and no other notes are using that tag.


## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

* Python 3.x
* PostgreSQL

### 2. Clone the Repository

```bash
git clone https://github.com/nimpy-wth/checkpoint7.git
cd psunote
```

### 3. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies

Create a `requirements.txt` file with the following content:

```
Flask
Flask-SQLAlchemy
Flask-WTF
psycopg2-binary
WTForms-SQLAlchemy
```

Then, install the dependencies using pip:

```bash
pip install -r requirements.txt
```

### 5. Database Setup with Docker

This project uses Docker Compose to simplify the database setup.

1.  **Start the Database:**
    Make sure you have the `docker-compose.yml` file in your project root. Run the following command to start the PostgreSQL database and pgAdmin in the background:
    ```bash
    docker-compose up -d
    ```
    This command automatically creates the database (`coedb`) and user (`coe`) specified in the file.

2.  **Initialize Tables:**
    Once the Docker containers are running, you need to create the application's tables in the database. Run the following commands in your terminal (with your virtual environment activated):
    ```bash
    # Open the Python shell
    python
    ```python
    # Inside the Python shell, run these commands
    from noteapp import app, models
    with app.app_context():
        models.db.create_all()
    exit()
    ```

3.  **(Optional) Access pgAdmin:**
    You can manage the database visually using the pgAdmin service.
    * **URL:** `http://localhost:7080`
    * **Email:** `coe@local.db`
    * **Password:** `CoEpasswd`


### 6. Run the Application

Now you can start the Flask development server.

```bash
python psunote/noteapp.py
```

The application will be available at `http://127.0.0.1:5000`.

## File Structure

* `noteapp.py`: The main application file. It contains all the Flask routes and business logic for handling requests.
* `models.py`: Defines the database schema using SQLAlchemy ORM. It includes the `Note` and `Tag` models and their relationship.
* `forms.py`: Contains the WTForms classes (`NoteForm`, `TagForm`) used for validating and processing user input from HTML forms.
* `templates/`: This directory contains all the HTML templates used for rendering the web pages.
    * `base.html`: The main layout template that other templates extend.
    * `index.html`: The home page, displaying all notes.
    * `notes-create.html`: The form for creating a new note.
    * `note-edit.html`: The form for editing an existing note.
    * `tags-list.html`: The page for managing all tags.
    * `tag-edit.html`: The form for editing a tag's name.
    * `tags-view.html`: The page that displays all notes for a specific tag.

## How to Use

* **Home Page:** View all your notes. Click "Create Note" to add a new one or "Manage Tags" to see all tags.
* **Creating a Note:** Fill in the title, description, and add tags as a comma-separated list (e.g., `python, flask, webdev`).
* **Editing a Note:** Click the "Edit" button on any note card. You can change any field. Removing a tag might delete it if no other note uses it.
* **Deleting a Note:** On the "Edit Note" page, click the "Delete Note" button. This will also trigger the tag garbage collection.
* **Managing Tags:** Go to the "Manage Tags" page to see a list of all tags. You can edit their names or delete them. Deleting a tag from here will remove it from all notes it was attached to.
