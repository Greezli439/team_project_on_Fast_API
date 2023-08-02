import schedule
import time
from _datetime import datetime, timedelta
from src.database.db_connection import SessionLocal
from src.database.models import Token
import sqlalchemy
from sqlalchemy.orm import Session
from src.database.db_connection import get_db



def clean_db():
    """
        Clean the token_black_list table by removing tokens older than 2 hours.

    This function queries the token_black_list table, checks each token's creation time,
    and deletes the tokens that are older than 2 hours from the current time.

    Note:
    - This function assumes that the `Token` and `SessionLocal` classes are defined and imported from the appropriate module.

    """
    session = SessionLocal()

    tokens = session.query(Token).all()
    for token in tokens:
        if token.created_at + timedelta(hours=4) <= datetime.now():
            session.delete(token)
            session.commit()


    print('table token_black_list was cleaned')
    session.close()

def clean_engine():
    """
        Run a cleaning job using a scheduler to clean the database regularly.

    This function schedules the `clean_db()` function to be executed every hour.
    The `clean_db()` function is responsible for cleaning the token_black_list table,
    removing tokens that are older than 4 hours from the current time.

    Note:
    - This function assumes that the `clean_db()` function is defined and imported from the appropriate module.
    - The `schedule` library is used to create the scheduler.

    """
    schedule.every().hour.do(clean_db)
    while True:
        schedule.run_pending()
        time.sleep(50)

if __name__ == '__main__':
    clean_engine()


