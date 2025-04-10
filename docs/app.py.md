# app.py

Main Flask application. Sets up routes, initializes database, and controls user sessions.

## Functions
### index()
Displays containers visible to the logged-in user with environment variables.

### login()
Handles login form, session creation, and role assignment.

### logout()
Clears session and redirects to login.

### control(container_id, action)
Starts, stops, or restarts a container by ID.

