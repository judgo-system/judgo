set -o errexit
set -o nounset

sleep 20
python3 src/manage.py makemigrations &&
python3 src/manage.py migrate auth && 
python3 src/manage.py migrate --run-syncdb && 
python3 src/manage.py runserver 0.0.0.0:8000

exec "$@"