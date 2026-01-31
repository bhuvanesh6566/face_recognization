import os

class Config:
    # FORMAT: mysql+pymysql://<username>:<password>@<host>/<db_name>
    
    # ⚠️ REPLACE 'your_password' WITH YOUR ACTUAL MYSQL ROOT PASSWORD
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:bhuvan@10@localhost/face_attendance'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super-secret-key'