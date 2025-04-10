# auth.py

Handles user authentication, role checks, and container label-based access.

## Functions
### init_db()
Initializes SQLite user table.

### verify_user(username, password)
Checks hashed password for login.

### get_user_containers(username)
Returns containers where the user is listed in `permissions.owner` label.

### login_required(f)
Decorator to require user login.

### requires_role(role)
Decorator to restrict access to users with specific roles.

### get_user_role(username)
Fetches the role assigned to the user.

