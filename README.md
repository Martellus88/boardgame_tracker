# boardgame_tracker
Django application for keeping statistics of games played.

## Application launch order
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd boardgame_tracker
    python manage.py migrate
    python manage.py runserver

When creating a superuser, you must manually add yourself to the list of players, through the admin panel or on the "add player" page, with the **same username** that you specified when creating the superuser. Otherwise, when trying to view overall statistics for the game, there will be a 404 error.


### TODO
    Ajax requests when accessing the BGG API.
