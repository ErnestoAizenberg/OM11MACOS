import logging
from typing import Optional

from app.models import User

class UserRepo:
    def __init__(self, db_session, logger: Optional[logging.Logger] = None):
        self.db_session = db_session
        self.logger = logger or logging.getLogger(__name__)

    def get(self, user_id: str):
        self.logger.debug("Fetching user by id: %s", user_id)
        user = self.db_session.query(User).filter(User.id == user_id).one_or_none()
        self.logger.debug("Found user: %s", user)
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        self.logger.debug("Fetching user by email: %s", email)
        user = self.db_session.query(User).filter(User.email == email).one_or_none()
        self.logger.debug("Found user: %s", user)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        self.logger.debug("Fetching user by username: %s", username)
        user = self.db_session.query(User).filter(User.username == username).one_or_none()
        self.logger.debug("Found user: %s", user)
        return user

    def create_user(self, username: str, email: str, password: str) -> User:
        self.logger.debug("Creating user with username: %s, email: %s", username, email)
        new_user = User(username=username, email=email, password=password)
        self.db_session.add(new_user)
        self.db_session.commit()
        self.logger.debug("Created new user: %s", new_user)
        return new_user

