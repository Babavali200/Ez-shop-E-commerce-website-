set -o errexit
gunicorn myshop.wsgi:application
