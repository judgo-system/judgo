# judgo

https://judgo.herokuapp.com


## Install

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





