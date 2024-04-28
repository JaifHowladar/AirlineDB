import traceback
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'airticket'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            if user_type == 'customer':
                query = "SELECT * FROM Customer WHERE email_address = %s AND password = %s"
                cursor.execute(query, (username_or_email, password))
            elif user_type == 'staff':
                query = """
                    SELECT * FROM AirlineStaff
                    WHERE (username = %s OR email_address = %s) AND password = %s
                """
                cursor.execute(query, (username_or_email, username_or_email, password))
            else:
                return render_template('login.html', error='Invalid user type')

            user = cursor.fetchone()

            if user:
                session['user_id'] = user[0]  # Assuming the first column is the unique identifier
                session['user_type'] = user_type
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid username, email, or password')

        except Exception as e:
            print(f"An error occurred during login: {str(e)}")
            return render_template('login.html', error='An error occurred during login')

        finally:
            cursor.close()
            conn.close()
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form['user_type']

        if user_type == 'customer':
            try:
                email = request.form['customer_email']
                password = request.form['customer_password']
                first_name = request.form['customer_first_name']
                last_name = request.form['customer_last_name']
                building_no = request.form['customer_building_no']
                street_name = request.form['customer_street_name']
                apartment_num = request.form['customer_apartment_num']
                city = request.form['customer_city']
                state = request.form['customer_state']
                zip_code = request.form['customer_zip']
                passport_num = request.form['customer_passport_num']
                passport_exp = request.form['customer_passport_exp']
                passport_country = request.form['customer_passport_country']
                date_of_birth = request.form['customer_date_of_birth']

                conn = get_db_connection()
                cursor = conn.cursor()

                query = "INSERT INTO Customer (email_address, password, first_name, last_name, building_no, street_name, apartment_num, city, state, zip, passport_num, passport_exp, passport_country, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (email, password, first_name, last_name, building_no, street_name, apartment_num, city, state, zip_code, passport_num, passport_exp, passport_country, date_of_birth)

                cursor.execute(query, values)
                conn.commit()

                cursor.close()
                conn.close()

                return render_template('register_success.html', user_type='customer')

            except Exception as e:
                error_message = str(e)
                error_traceback = traceback.format_exc()
                print(f"An error occurred during customer registration: {error_message}")
                print(f"Traceback: {error_traceback}")
                return render_template('register.html', error="An error occurred during customer registration. Please try again.")

        elif user_type == 'staff':
            try:
                username = request.form['staff_username']
                password = request.form['staff_password']
                first_name = request.form['staff_first_name']
                last_name = request.form['staff_last_name']
                airline_name = request.form['staff_airline_name']
                date_of_birth = request.form['staff_date_of_birth']
                email = request.form['staff_email']

                conn = get_db_connection()
                cursor = conn.cursor()

                # Check if the airline exists
                query = "SELECT COUNT(*) FROM Airline WHERE airline_name = %s"
                cursor.execute(query, (airline_name,))
                airline_exists = cursor.fetchone()[0]

                if airline_exists:
                    # Insert data into the AirlineStaff table
                    query = "INSERT INTO AirlineStaff (username, password, first_name, last_name, airline_name, dob) VALUES (%s, %s, %s, %s, %s, %s)"
                    values = (username, password, first_name, last_name, airline_name, date_of_birth)
                    cursor.execute(query, values)

                    # Check if the email address already exists for the username
                    query = "SELECT COUNT(*) FROM Email WHERE username = %s"
                    cursor.execute(query, (username,))
                    email_exists = cursor.fetchone()[0]

                    if email_exists:
                        # Update the existing email address
                        query = "UPDATE Email SET email_address = %s WHERE username = %s"
                        values = (email, username)
                    else:
                        # Insert a new email address
                        query = "INSERT INTO Email (username, email_address) VALUES (%s, %s)"
                        values = (username, email)

                    cursor.execute(query, values)

                    conn.commit()
                    cursor.close()
                    conn.close()

                    return render_template('register_success.html', user_type='staff')
                else:
                    return render_template('register.html', error="Invalid airline name. Please enter a valid airline name.")

            except Exception as e:
                error_message = str(e)
                error_traceback = traceback.format_exc()
                print(f"An error occurred during staff registration: {error_message}")
                print(f"Traceback: {error_traceback}")
                return render_template('register.html', error="An error occurred during staff registration. Please try again.")
    else:
        return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user_type = session['user_type']

        if user_type == 'customer':
            conn = get_db_connection()
            cursor = conn.cursor()

            query = "SELECT * FROM Flight"
            cursor.execute(query)
            flights = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template('customer_dashboard.html', user_id=user_id, flights=flights)
        elif user_type == 'staff':
            conn = get_db_connection()
            cursor = conn.cursor()

            query = "SELECT * FROM Flight WHERE airline_name = (SELECT airline_name FROM AirlineStaff WHERE username = %s)"
            cursor.execute(query, (user_id,))
            flights = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template('staff_dashboard.html', user_id=user_id, flights=flights)
    else:
        return redirect(url_for('login'))

@app.route('/search_flights', methods=['GET', 'POST'])
def search_flights():
    if request.method == 'POST':
        source_city = request.form['source_city']
        destination_city = request.form['destination_city']
        departure_date = request.form['departure_date']
        trip_type = request.form['trip_type']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM Flight WHERE departure_airport_code = (SELECT airport_code FROM Airport WHERE city = %s) AND arrival_airport_code = (SELECT airport_code FROM Airport WHERE city = %s) AND departure_date = %s"
        values = (source_city, destination_city, departure_date)

        if trip_type == 'round_trip':
            return_date = request.form['return_date']
            query += " AND arrival_date <= %s"
            values += (return_date,)

        cursor.execute(query, values)
        flights = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('search_results.html', flights=flights)
    else:
        return render_template('search_flights.html')

@app.route('/book_flight', methods=['POST'])
def book_flight():
    if 'user_id' in session and session['user_type'] == 'customer':
        user_id = session['user_id']
        flight_no = request.form['flight_no']
        departure_date = request.form['departure_date']
        departure_time = request.form['departure_time']
        airline_name = request.form['airline_name']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "INSERT INTO Ticket (flight_no, departure_date, departure_time, airline_name, first_name, last_name, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (flight_no, departure_date, departure_time, airline_name, first_name, last_name, dob)
        cursor.execute(query, values)

        ticket_id = cursor.lastrowid

        query = "INSERT INTO Buy (ticket_ID, email_address, buy_date, buy_time) VALUES (%s, %s, %s, %s)"
        values = (ticket_id, user_id, datetime.now().date(), datetime.now().time())
        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/cancel_flight', methods=['POST'])
def cancel_flight():
    if 'user_id' in session and session['user_type'] == 'customer':
        ticket_id = request.form['ticket_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "DELETE FROM Buy WHERE ticket_ID = %s"
        cursor.execute(query, (ticket_id,))

        query = "DELETE FROM Ticket WHERE ticket_ID = %s"
        cursor.execute(query, (ticket_id,))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/rate_flight', methods=['POST'])
def rate_flight():
    if 'user_id' in session and session['user_type'] == 'customer':
        user_id = session['user_id']
        flight_no = request.form['flight_no']
        departure_date = request.form['departure_date']
        departure_time = request.form['departure_time']
        airline_name = request.form['airline_name']
        rating = request.form['rating']
        comment = request.form['comment']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "INSERT INTO Review (flight_no, departure_date, departure_time, airline_name, email_address, rate, comment) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (flight_no, departure_date, departure_time, airline_name, user_id, rating, comment)
        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/track_spending', methods=['GET', 'POST'])
def track_spending():
    if 'user_id' in session and session['user_type'] == 'customer':
        user_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            start_date = request.form['start_date']
            end_date = request.form['end_date']

            query = "SELECT SUM(Ticket.ticket_base_price) AS total_spending FROM Buy JOIN Ticket ON Buy.ticket_ID = Ticket.ticket_ID WHERE Buy.email_address = %s AND Buy.buy_date BETWEEN %s AND %s"
            values = (user_id, start_date, end_date)
            cursor.execute(query, values)
            total_spending = cursor.fetchone()[0]

            query = "SELECT MONTH(Buy.buy_date) AS month, SUM(Ticket.ticket_base_price) AS monthly_spending FROM Buy JOIN Ticket ON Buy.ticket_ID = Ticket.ticket_ID WHERE Buy.email_address = %s AND Buy.buy_date BETWEEN %s AND %s GROUP BY MONTH(Buy.buy_date)"
            values = (user_id, start_date, end_date)
            cursor.execute(query, values)
            monthly_spending = cursor.fetchall()
        else:
            query = "SELECT SUM(Ticket.ticket_base_price) AS total_spending FROM Buy JOIN Ticket ON Buy.ticket_ID = Ticket.ticket_ID WHERE Buy.email_address = %s AND Buy.buy_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"
            cursor.execute(query, (user_id,))
            total_spending = cursor.fetchone()[0]

            query = "SELECT MONTH(Buy.buy_date) AS month, SUM(Ticket.ticket_base_price) AS monthly_spending FROM Buy JOIN Ticket ON Buy.ticket_ID = Ticket.ticket_ID WHERE Buy.email_address = %s AND Buy.buy_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) GROUP BY MONTH(Buy.buy_date)"
            cursor.execute(query, (user_id,))
            monthly_spending = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('track_spending.html', total_spending=total_spending, monthly_spending=monthly_spending)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)