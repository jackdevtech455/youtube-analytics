from sqlalchemy import select
from sqlalchemy.orm import Session
from yta_core.db.models import User

DEFAULT_USER_EMAIL_ADDRESS = "default@local"

def get_or_create_default_user(database_session: Session) -> User:
    existing_user = database_session.execute(
        select(User).where(User.email == DEFAULT_USER_EMAIL_ADDRESS)
    ).scalar_one_or_none()

    if existing_user is not None:
        return existing_user

    new_user = User(email=DEFAULT_USER_EMAIL_ADDRESS)
    database_session.add(new_user)
    database_session.commit()
    database_session.refresh(new_user)
    return new_user
