:: Create virtual environment
python -m venv venv

:: Activate virtual environment
cd venv
cd Scripts
activate

:: Back to root dir, install dependencies
cd ..
cd ..
pip install -r requirements.txt

:: Create and setup db
flask db init
flask db migrate
flask db upgrade


:: FLASK APP ENV VARIABLES REQUIRED FOR EMAIL SUPPORT
set MAIL_SERVER=smtp.googlemail.com
set MAIL_PORT=587
set MAIL_USE_TLS=1
set MAIL_USERNAME=poop.time.app@gmail.com
set MAIL_PASSWORD=FlaskAppPassword

:: Start app
flask run 