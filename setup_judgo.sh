set -o errexit
set -o nounset

echo "Load Environment Variable"
export $(grep -v '^#' judgo.env | xargs)

rm -rf logs
mkdir logs
touch logs/logs.log
python3 web/manage.py makemigrations &&
python3 web/manage.py migrate auth && 
python3 web/manage.py migrate --run-syncdb && 

echo "Clone Sample File"
rm -rf sample-data
git clone https://github.com/judgo-system/sample-data.git
cp -rf sample-data web

echo "Ingest Data in Database"
python3 web/manage.py shell < web/fixtures/msmarco/ingest_msmarco_data.py

echo "Create superuser"

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python3 web/manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

echo "Run Django webapp"
python3 web/manage.py runserver 

exec "$@"