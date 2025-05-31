import logging
import secrets
from typing import Optional

from flask import Flask, jsonify, redirect, request, session, url_for, abort
from werkzeug.security import check_password_hash, generate_password_hash

from app.email_service import EmailService
from app.repos import UserRepo


def configure_email_auth(
    app: Flask,
    user_repo: UserRepo,
    email_service: EmailService,
    logger: Optional[logging.Logger] = None,
):
    logger = logger or logging.getLogger(__name__)

    @app.route("/api/login", methods=["POST"])
    def login():
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return jsonify({"message": "Email and password are required"}), 400

            # 1. Find user by email
            user = user_repo.get_user_by_email(email=email)
            if not user:
                return jsonify({"message": "Invalid credentials"}), 401

            # 2. Verify password
            if not check_password_hash(user.password, password):
                return jsonify({"message": "Invalid credentials"}), 401

            if not user.is_verified:
                return (
                    jsonify({"message": "User is not verified, check email first"}),
                    401,
                )

            # 3. Create session
            session.clear()
            session["user_id"] = user.id
            session.permanent = True  # Makes the session last 31 days (Flask default)

            # 4. Return success
            return jsonify(
                {
                    "message": "Login successful",
                    "user": {"id": user.id, "name": user.username, "email": user.email},
                }
            )

        except Exception as e:
            logger.error(f"An error while login: {str(e)}")
            return jsonify({"message": "Server error"}), 500

    # Signup endpoint
    @app.route("/api/signup", methods=["POST"])
    def signup():
        try:
            data = request.get_json()
            name = data.get("name")
            email = data.get("email")
            password = data.get("password")

            if not name or not email or not password:
                return (
                    jsonify({"message": "Name, email and password are required"}),
                    400,
                )

            # 1. Check if user exists
            existing_user = user_repo.get_user_by_email(email=email)

            if existing_user:
                return jsonify({"message": "Email already in use"}), 400

            # 2. Hash password and create user
            hashed_password = generate_password_hash(password)
            user_data_dict = {
                "username": name,
                "email": email,
                "password": hashed_password,
                "verification_token": secrets.token_urlsafe(32),
            }
            new_user = user_repo.create_user(user_data_dict)

            # 3. Send verification email
            verification_token: str = new_user.verification_token
            verification_link: str = url_for(
                "verify", token=verification_token, _external=True
            )
            email_service.send_verification_email(
                verification_link=verification_link,
                username=new_user.username,
                email=new_user.email,
            )
            # 4. Return success
            return (
                jsonify(
                    {
                        "message": "Account created successfully",
                        "user": {
                            "id": new_user.id,
                            "name": new_user.username,
                            "email": new_user.email,
                        },
                    }
                ),
                201,
            )

        except Exception as e:
            logger.error(f"An error occured while sign up: {str(e)}")
            return jsonify({"message": "Server error"}), 500

    @app.route("/verify/<token>", methods=["GET"])
    def verify(token):
        user = user_repo.get_user_by_verification_token(token)
        if not user:
            logger.error("Not tge valid token provided")
            abort(403)

        true_verification_token = user.verification_token

        if token == true_verification_token:
            user.is_verified = True
            data_for_update = {
                "id": user.id,
                "verification_token": None,
                "is_verified": True,
            }
            verified_user = user_repo.update(data_for_update)

            # Automatically log in the user
            session.clear()
            session["user_id"] = verified_user.id
            session.permanent = True

            logger.info("User verified successfully.")
            return redirect("/")

        logger.warning("User auth token is nit correct")
        return redirect("/")

    # Logout endpoint
    # @app.route('/api/logout', methods=['POST'])
    # def logout():
    #    session.clear()
    #    return jsonify({'message': 'Logged out successfully'})

    # Check auth status
    @app.route("/api/check-auth", methods=["GET"])
    def check_auth():
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"authenticated": False}), 200

        user = user_repo.get(user_id)
        if not user:
            session.clear()
            return jsonify({"authenticated": False}), 200

        return jsonify(
            {
                "authenticated": True,
                "user": {"id": user.id, "name": user.username, "email": user.email},
            }
        )
