import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'whatever_you_want'

# MySQL database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # No password for default XAMPP setup
    'database': 'Airticket'  # Replace 'your_database_name' with your actual database name
}

@app.route('/')
def root():
    # Return content for the root page
    return render_template('login.html')

# Define your authenticate_user function here
def authenticate_user(username, password):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Execute the query to check username and password
        query = "SELECT * FROM AirlineStaff WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))

        # Fetch the result
        user = cursor.fetchone()

        if user:
            return True
        else:
            return False
    except mysql.connector.Error as err:
        print("Error:", err)
        return False
    finally:
        # Close the connection
        if 'conn' in locals():
            conn.close()



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle POST request for login
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Authenticate user
        if authenticate_user(username, password):
            # Set session variable to indicate user is logged in
            session['logged_in'] = True
            session['username'] = username  # Optionally store username in session
            return redirect(url_for('protected'))
        else:
            # Authentication failed, redirect back to login page with error message
            return render_template('login.html', error="Invalid username or password")
    else:
        # Handle GET request for login (render login form)
        return render_template('login.html')
    
# Basic protected route example
@app.route('/protected', methods=['GET'])
def protected():
    if session.get('logged_in'):
        # let the user see the protected page
        return render_template('protected.html', username=session['username'])
    else:
        # otherwise redirect to somewhere else
        return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)




# /usr/local/bin/python3 app.py