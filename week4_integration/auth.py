from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from functools import wraps
import bcrypt
from db_connect import get_connection

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    """
    User model for Flask-Login.
    Represents an authenticated operator from the database.
    """
    def __init__(self, operator_id, username, operator_name, role, is_active):
        self.id = operator_id
        self.operator_id = operator_id
        self.username = username
        self.operator_name = operator_name
        self.role = role
        self._is_active = is_active

    def get_id(self):
        """Required by Flask-Login - returns the unique identifier"""
        return str(self.operator_id)

    @property
    def is_active(self):
        """Required by Flask-Login - returns whether user is active"""
        return self._is_active

    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'

    def is_cashier(self):
        """Check if user has cashier role"""
        return self.role == 'cashier'


def load_user_from_db(operator_id):
    """
    Load user from database by operator_id.
    Called by Flask-Login's @login_manager.user_loader

    Args:
        operator_id (str): The operator's ID (converted to int)

    Returns:
        User object or None if not found
    """
    conn = get_connection()
    if not conn:
        return None

    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            SELECT operator_id, username, operator_name, role, is_active
            FROM Operator
            WHERE operator_id = %s
        """
        cursor.execute(query, (int(operator_id),))
        result = cursor.fetchone()

        if result:
            return User(
                operator_id=result[0],
                username=result[1],
                operator_name=result[2],
                role=result[3],
                is_active=result[4]
            )
        return None

    except Exception as e:
        print(f"Error loading user: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        conn.close()


def verify_password(plain_password, password_hash):
    """
    Verify a password against its bcrypt hash.

    Args:
        plain_password (str): The plain text password
        password_hash (str): The stored bcrypt hash

    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        # Convert string hash back to bytes for bcrypt
        hash_bytes = password_hash.encode('utf-8')
        password_bytes = plain_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def authenticate_user(username, password):
    """
    Authenticate a user by username and password.

    Args:
        username (str): The username
        password (str): The plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    conn = get_connection()
    if not conn:
        return None

    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            SELECT operator_id, username, password_hash, operator_name, role, is_active
            FROM Operator
            WHERE username = %s
        """
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if not result:
            print(f"User '{username}' not found")
            return None

        operator_id, username, password_hash, operator_name, role, is_active = result

        # Check if account is active
        if not is_active:
            print(f"User '{username}' account is inactive")
            return None

        # Verify password
        if not verify_password(password, password_hash):
            print(f"Invalid password for user '{username}'")
            return None

        # Authentication successful
        return User(
            operator_id=operator_id,
            username=username,
            operator_name=operator_name,
            role=role,
            is_active=is_active
        )

    except Exception as e:
        print(f"Authentication error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        conn.close()


def role_required(*roles):
    """
    Decorator to restrict access to specific roles.

    Usage:
        @app.route('/admin-only')
        @login_required
        @role_required('admin')
        def admin_page():
            return "Admin only content"

    Args:
        *roles: Variable number of allowed roles (strings)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user
            from flask import abort

            if not current_user.is_authenticated:
                abort(401)

            if current_user.role not in roles:
                flash(f'Access denied. This page requires {" or ".join(roles)} role.', 'error')
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route - handles both GET (show form) and POST (process login)
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')

        user = authenticate_user(username, password)

        if user:
            login_user(user)
            flash(f'Welcome back, {user.operator_name}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logout route - clears the user session
    """
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
