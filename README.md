### Hexlet tests and linter status:
[![Actions Status](https://github.com/Neyghyw/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Neyghyw/python-project-83/actions)

### Maintainability:
<a href="https://codeclimate.com/github/Neyghyw/python-project-83/maintainability"><img src="https://api.codeclimate.com/v1/badges/c29440c9ef45211143b6/maintainability" /></a>

# Description

Hello!

This web app analysis the web page for its SEO affordability.

The app is available by link:
    https://flask-secretkey.up.railway.app/
    
# Local usage
For personal usage you need to create a special .env file, that contains environment variables.

Creating:
```ch
touch .env
```

Example: 
```ch
SECRET_KEY=8c42c2ea363a9082740b523d1a302e6a3ad3387d3491b8ffb66da
DATABASE_URL=postgresql://user:password@connect_url/database
```

# Makefile
Into makefile you can see next commands:
* debug - start local wsgi-server, that use debug mode. Debug mode restart automatically when you edit a code.
* start - start command for production deploy.
* dev - start local wsgi-server.
* lint - this command will check project with flake8 linter.
* install - this command will install poetry into project.


# Tech stack

* Linux OS
* python = "^3.10"
* flask = "^2.2.2"
* gunicorn = "^20.1.0"
* psycopg2-binary = "^2.9.5"
* python-dotenv = "^0.21.1"
* validators = "^0.20.0"
* requests = "^2.28.2"
* bs4 = "^0.0.1"
