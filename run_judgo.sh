set -o errexit
set -o nounset

echo "Load Environment Variable"
export $(grep -v '^#' judgo.env | xargs)

echo "Run Django webapp"
python3 web/manage.py runserver 

exec "$@"