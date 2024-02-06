python bot_site/manage.py makemigrations &&\
python bot_site/manage.py migrate &&\
# apt-get update && apt-get install -y gettext &&\
env DJANGO_SUPERUSER_PASSWORD=admin DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@mail.ru python bot_site/manage.py createsuperuser --noinput&&\
python bot_site/manage.py runserver 0.0.0.0:8000
# /bin/bash -c "while true; do echo 'admin alive'; sleep 60; done"