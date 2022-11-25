# judgo

A tool to rank documents for each query based on users' preference which has been used for TREC 2022 Health Misinformation Track!

## Install Application and Test with sample data

### 1. Without Docker

- Step 1: Create an activate a new virtual environment and run:

```
pip install -r requirements/local.txt
```

- Step 2:  Change `judgo.env` file according to your own settings

- Step 3: Execute the following file to setup and run application for the first time.

```
./setup_judgo.sh
```
If you previously run this file and you need to run the system with the previous setting, execute ```./run_judgo.sh```

- Step 4: Open http://0.0.0.0:8000/





### 2. with Docker

 - Step 0: Before install this project make sure your sysytem has `docker` and `docker-compose` installed.

 - Step 1:  Change `docker/.web` file according to your own settings

 - Step 2: Run the following command.

  ```
  docker-compose up --build -d 
  ```

  Step 3- Open http://0.0.0.0:8000/



