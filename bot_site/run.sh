python bot_site/manage.py makemigrations &&\
python bot_site/manage.py migrate &&\
# env DJANGO_SUPERUSER_PASSWORD=admin DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@mail.ru python bot_site/manage.py createsuperuser --noinput&&\
python bot_site/manage.py runserver 0.0.0.0:8000