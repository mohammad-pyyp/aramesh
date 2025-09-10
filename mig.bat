@echo off

call C:\Users\Reza.asa\Documents\pro\env\Scripts\activate.bat

python manage.py makemigrations
python manage.py migrate

call django.bat

