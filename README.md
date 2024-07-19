# JWT Token Authentication

Using JWT authentication with Django Rest Framework.

## Virtual Environment

Create virtual environment

```
python -m venv env

```

Activate virtual environment - gitbash terminal

```
source env/Scripts/activate

```

## Install packages

pip install -r requirements.txt


## API endpoints:

* `/api/user/register/`
* `/api/user/login/`
* `/api/user/`
* `/api/user/logout/`

* `/api/user/tasks/add/`
* `/api/user/tasks/view/`

## Example usage

This repo can be used from the command line with the following steps:

```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

```

You can also use it with **httpie** as follows:

```
http GET http://127.0.0.1:8000/api/user/ "Cookie:access_token=<the access token>"
```
