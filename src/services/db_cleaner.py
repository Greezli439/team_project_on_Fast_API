import schedule
import time
from _datetime import datetime, timedelta
from src.database.db_connection import SessionLocal
from src.database.models import Token
import sqlalchemy
from sqlalchemy.orm import Session
from src.database.db_connection import get_db



def clean_db():
    session = SessionLocal()

    tokens = session.query(Token).all()
    for token in tokens:
        if token.created_at + timedelta(hours=4) <= datetime.now():
            session.delete(token)
            session.commit()


    print('table token_black_list was cleaned')
    session.close()

def clean_engine():
    schedule.every().hour.do(clean_db)
    while True:
        schedule.run_pending()
        time.sleep(50)

if __name__ == '__main__':
    clean_engine()


