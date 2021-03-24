import os
from flask import Flask
from mongoengine import connect
from dotenv import load_dotenv
from api.api import api

load_dotenv()

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
PORT = os.getenv('PORT')

app = Flask(__name__)

connect(DB_NAME, host=f'mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?authSource=admin')

app.register_blueprint(api)

@app.route('/')
def index():
    return "ETL Camara"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)
