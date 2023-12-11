# glowing-eureka

A Python Flask CMS made as a university programming project.

## Tech stack

For simplicity's sake the entire backend was written in Flask, with ORM mapping done in sqlAlchemy.
The database engine used is Sqlite3.
For frontend in true Flask style a combination of Bootstrap5 enhanced HTML.
In a few places where it was necessary JS was used.

## File structure

All static files served in the frontend are stored in the [static](./static/) folder.
Jinja2 templates are stored in the [templates](./templates/) folder.
Backend code is stored within [app.py](app.py), and ORM mapping is defined within [db.py](db.py).
addUser.py is a simple utility script for adding users to the database.

## How to run

For testing purposes just run app.py.
Within that file there is a Blueprint defined that may be used to setup the app on a production server.
