# import os
# from dotenv import load_dotenv
# from mongoengine import connect
# from mongoengine import *

# load_dotenv()

# DB_USERNAME = os.getenv('DB_USERNAME')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_HOST = os.getenv('DB_HOST')
# DB_PORT = os.getenv('DB_PORT')
# DB_NAME = os.getenv('DB_NAME')

# connect(DB_NAME, 
#         username=DB_USERNAME,
#         password=DB_PASSWORD,
#         authentication_source='admin')

# class User(Document):
#     name = StringField()

# class Page(Document):
#     content = StringField()
#     author = ReferenceField(User)

# # john = User(name="John Smith")
# # john.save()

# # post = Page(content="Test Page")
# # post.author = john
# # post.save()

# for user in User.objects:
#     print(user.name)


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

app = Flask(__name__)

connect(DB_NAME, host=f'mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?authSource=admin')

app.register_blueprint(api)

@app.route('/')
def index():
    return "ETL Camara"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8004)