from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.repos import UserRepo

def configure_email_auth(
    app: Flask,
    user_repo: UserRepo,
):
    @app.route('/api/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'message': 'Email and password are required'}), 400
            
            # 1. Find user by email
            user = user_repo.get_user_by_email(email=email)
            if not user:
                return jsonify({'message': 'Invalid credentials'}), 401
            
            # 2. Verify password
            if not check_password_hash(user.password, password):
                return jsonify({'message': 'Invalid credentials'}), 401
            
            # 3. Create session
            session.clear()
            session['user_id'] = user.id
            session.permanent = True  # Makes the session last 31 days (Flask default)
            
            # 4. Return success
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'name': user.username,
                    'email': user.email
                }
            })
            
        except Exception as e:
            raise Exception(f"An error: {str(e)}")
            return jsonify({'message': 'Server error'}), 500

    # Signup endpoint
    @app.route('/api/signup', methods=['POST'])
    def signup():
        try:
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            
            if not name or not email or not password:
                return jsonify({'message': 'Name, email and password are required'}), 400
            
            # 1. Check if user exists
            existing_user = user_repo.get_user_by_email(email=email)

            if existing_user:
                return jsonify({'message': 'Email already in use'}), 400
            
            # 2. Hash password and create user
            hashed_password = generate_password_hash(password)
            new_user = user_repo.create_user(
                username=name,
                email=email,
                password=hashed_password
            )
            
            # 3. Automatically log in the new user
            session.clear()
            session['user_id'] = new_user.id
            session.permanent = True
            
            # 4. Return success
            return jsonify({
                'message': 'Account created successfully',
                'user': {
                    'id': new_user.id,
                    'name': new_user.username,
                    'email': new_user.email
                }
            }), 201
            
        except Exception as e:
            raise Exception(f"An error occured: {str(e)}")
            return jsonify({'message': 'Server error'}), 500

    # Logout endpoint
    #@app.route('/api/logout', methods=['POST'])
    #def logout():
    #    session.clear()
    #    return jsonify({'message': 'Logged out successfully'})

    # Check auth status
    @app.route('/api/check-auth', methods=['GET'])
    def check_auth():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'authenticated': False}), 200
        
        user = user_repo.get(user_id)
        if not user:
            session.clear()
            return jsonify({'authenticated': False}), 200
        
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user.id,
                'name': user.username,
                'email': user.email
            }
        })
