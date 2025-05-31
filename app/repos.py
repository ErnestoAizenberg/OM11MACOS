import logging
from typing import Dict, Optional

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

    def update(self, user_data_dict: Dict):
        self.logger.debug("Updating user with data: %s", user_data_dict)
        user_id = user_data_dict.get("id")
        if not user_id:
            raise ValueError("User ID is required for update")

        restricted_fields = [
            "id",
            "password_hash",
            "created_at",
        ]  # fields that shouldn't be updated
        update_data = {
            k: v for k, v in user_data_dict.items() if k not in restricted_fields
        }

        if not update_data:
            raise ValueError("No valid fields provided for update")

        rows_updated = (
            self.db_session.query(User).filter_by(id=user_id).update(update_data)
        )

        if rows_updated == 0:
            raise ValueError(f"User with ID {user_id} not found")

        updated_user = self.db_session.query(User).get(user_id)
        return updated_user

    def get_user_by_email(self, email: str) -> Optional[User]:
        self.logger.debug("Fetching user by email: %s", email)
        user = self.db_session.query(User).filter(User.email == email).one_or_none()
        self.logger.debug("Found user: %s", user)
        return user

    def get_user_by_verification_token(self, verification_token: str) -> Optional[User]:
        self.logger.debug("Fetching user by verification_token: %s", verification_token)
        try:
            user = (
                self.db_session.query(User)
                .filter(User.verification_token == verification_token)
                .one_or_none()
            )
            self.logger.debug("Found user: %s", user)
            return user
        except Exception as e:
            self.db_session.rollback()
            self.logger(
                "Exception in while geting_user_by_verification_token: %s", str(e)
            )
            raise

    def get_user_by_username(self, username: str) -> Optional[User]:
        self.logger.debug("Fetching user by username: %s", username)
        user = (
            self.db_session.query(User).filter(User.username == username).one_or_none()
        )
        self.logger.debug("Found user: %s", user)
        return user

    def create_user(self, user_data_dict) -> User:
        self.logger.debug("Creating user with data: %s", user_data_dict)
        try:
            new_user = User(**user_data_dict)
            self.db_session.add(new_user)
            self.db_session.commit()
            self.logger.debug("Created new user: %s", new_user)
            return new_user
        except Exception as e:
            self.db_session.rollback()
            self.logger.error("Failed to create a user: %s", str(e), exc_info=True)
            raise
