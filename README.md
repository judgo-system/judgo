# judgo

https://judgo.herokuapp.com


## Install Application with Docker

Step 0- Before install this project make sure your sysytem has `docker` and `docker-compose` installed.

Step 1- Clone project and run the following command inorder to ingest corpus to dataset.

```
docker-compose up --build -d 

# find the name of web container it should be something like judgo_web_xx
docker ps
# to enter web container
docker exec -i -t judgo_web_xx /bin/bash
cd src
# ingest data to dataset with the following command
python manage.py shell < fixtures/ingest_data.py 

# Press CTRL+D to exit from container
```

Step 2- Open http://0.0.0.0:8000/




## Install Application without Docker

Step 0- After clone project, create an activate a new virtual environment and run:

```
pip install -r requirements/base.txt
```

Step 1- Go to `web` folder create a new foloder named 'logs' and create a file named 'logs.log'

Step 2- Go to `web/web` create `.env` file and fill the following information:

```
SECRET_KEY='xxxxxx'
ENGINE="django.db.backends.sqlite3"
NAME="db.sqlite3"
USER="user"
PASSWORD="password"
HOST="localhost"
PORT=5432
```
You can change them if you want to use anyother databases

Step 3- Run the following commands:

```
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py createsuperuser

# if you want to ingest msmarco sample data to database
python manage.py shell < fixtures/ingest_msmarco_data.py

python manage.py runserver
```

Step 4- Open http://0.0.0.0:8000/




