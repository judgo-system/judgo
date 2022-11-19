set -o errexit
set -o nounset

mkdir logs
touch logs/logs.log
python3 web/manage.py makemigrations &&
python3 web/manage.py migrate auth && 
python3 web/manage.py migrate --run-syncdb && 

echo "Clone Sample File"
git clone https://github.com/judgo-system/sample-data.git
cp -rf sample-data web

echo "Ingest Data in Database"
python3 web/manage.py shell < web/fixtures/msmarco/ingest_msmarco_data.py

echo "Create superuser"
python3 web/manage.py createsuperuser

python3 web/manage.py runserver 0.0.0.0:8000

exec "$@"