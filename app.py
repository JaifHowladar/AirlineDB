import traceback
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

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
                query = "SELECT * FROM Customer WHERE email_address = %s"
                cursor.execute(query, (username_or_email,))
                user = cursor.fetchone()

                if user:
                    hashed_password = user[3]  # Password is stored in the fourth column for Customer
                    if check_password_hash(hashed_password, password):
                        session['user_id'] = user[0]  # Assuming the email_address is the unique identifier
                        session['user_type'] = user_type
                        return redirect(url_for('dashboard'))
                    else:
                        return render_template('login.html', error='Invalid username, email, or password')
                else:
                    return render_template('login.html', error='Invalid username, email, or password')

            elif user_type == 'staff':
                query = "SELECT * FROM AirlineStaff WHERE username = %s"
                cursor.execute(query, (username_or_email,))
                user = cursor.fetchone()

                if user:
                    hashed_password = user[1]  # Password is stored in the second column for AirlineStaff
                    if check_password_hash(hashed_password, password):
                        session['user_id'] = user[0]  # Assuming the username is the unique identifier
                        session['user_type'] = user_type
                        session['airline_name'] = user[4]  # Store the airline name in the session
                        return redirect(url_for('dashboard'))
                    else:
                        return render_template('login.html', error='Invalid username, email, or password')
                else:
                    return render_template('login.html', error='Invalid username, email, or password')

            else:
                return render_template('login.html', error='Invalid user type')

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

                hashed_password = generate_password_hash(password)
                print(password)
                print(hashed_password)

                query = "INSERT INTO Customer (email_address, first_name, last_name, password, building_no, street_name, apartment_num, city, state, zip, passport_num, passport_exp, passport_country, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (email, first_name, last_name, hashed_password, building_no, street_name, apartment_num, city, state, zip_code, passport_num, passport_exp, passport_country, date_of_birth)

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

                hashed_password = generate_password_hash(password)

                # Check if the airline exists
                query = "SELECT COUNT(*) FROM Airline WHERE airline_name = %s"
                cursor.execute(query, (airline_name,))
                airline_exists = cursor.fetchone()[0]

                if airline_exists:
                    # Insert data into the AirlineStaff table
                    query = "INSERT INTO AirlineStaff (username, password, first_name, last_name, airline_name, dob) VALUES (%s, %s, %s, %s, %s, %s)"
                    values = (username, hashed_password, first_name, last_name, airline_name, date_of_birth)
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

        # Check if the customer already has a ticket for the same flight
        query = "SELECT COUNT(*) FROM Ticket WHERE flight_no = %s AND departure_date = %s AND departure_time = %s AND airline_name = %s AND first_name = %s AND last_name = %s AND date_of_birth = %s"
        values = (flight_no, departure_date, departure_time, airline_name, first_name, last_name, dob)
        cursor.execute(query, values)
        ticket_exists = cursor.fetchone()[0]

        if ticket_exists:
            cursor.close()
            conn.close()
            return "You have already booked a ticket for this flight."

        # Insert the ticket into the database
        query = "INSERT INTO Ticket (flight_no, departure_date, departure_time, airline_name, first_name, last_name, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (flight_no, departure_date, departure_time, airline_name, first_name, last_name, dob)
        cursor.execute(query, values)
        ticket_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('payment', ticket_id=ticket_id, email_address=user_id))
    else:
        return redirect(url_for('login'))

@app.route('/payment')
def payment():
    ticket_id = request.args.get('ticket_id')
    email_address = request.args.get('email_address')
    return render_template('payment.html', ticket_id=ticket_id, email_address=email_address)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    ticket_id = request.form['ticket_id']
    email_address = request.form['email_address']
    exp_date = request.form['exp_date']
    card_name = request.form['card_name']
    card_num = request.form['card_num']
    payment_type = request.form['payment_type']
    buy_date = datetime.now().date()
    buy_time = datetime.now().time()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the payment record into the Buy table
    query = "INSERT INTO Buy (ticket_ID, email_address, exp_date, card_name, card_num, buy_date, buy_time, payment_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (ticket_id, email_address, exp_date, card_name, card_num, buy_date, buy_time, payment_type)
    cursor.execute(query, values)

    conn.commit()
    cursor.close()
    conn.close()

    return "Flight booked successfully!"

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

            query = "SELECT SUM(Ticket.ticket_price) AS total_spending FROM Buy JOIN Ticket ON Buy.ticket_ID = Ticket.ticket_ID WHERE Buy.email_address = %s AND Buy.buy_date BETWEEN %s AND %s"
            values = (user_id, start_date, end_date)
            cursor.execute(query, values)
            total_spending = cursor.fetchone()[0]

            query = "SELECT MONTH(Buy.buy_date) AS month, SUM(Ticket.ticket_price) AS monthly_spending FROM Buy JOIN Ticket ON Buy.ticket_ID = Ticket.ticket_ID WHERE Buy.email_address = %s AND Buy.buy_date BETWEEN %s AND %s GROUP BY MONTH(Buy.buy_date)"
            values = (user_id, start_date, end_date)
            cursor.execute(query, values)
            monthly_spending = cursor.fetchall()
        else:
            query = "SELECT SUM(Ticket.ticket_price) AS total_spending FROM Buy JOIN Ticket ON Buy.ticket_ID = Ticket.ticket_ID WHERE Buy.email_address = %s AND Buy.buy_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"
            cursor.execute(query, (user_id,))
            total_spending = cursor.fetchone()[0]

            query = "SELECT MONTH(Buy.buy_date) AS month, SUM(Ticket.ticket_price) AS monthly_spending FROM Buy JOIN Ticket ON Buy.ticket_ID = Ticket.ticket_ID WHERE Buy.email_address = %s AND Buy.buy_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) GROUP BY MONTH(Buy.buy_date)"
            cursor.execute(query, (user_id,))
            monthly_spending = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('track_spending.html', total_spending=total_spending, monthly_spending=monthly_spending)
    else:
        return redirect(url_for('login'))

@app.route('/flight_status', methods=['GET', 'POST'])
def flight_status():
    if request.method == 'POST':
        airline_name = request.form['airline_name']
        flight_number = request.form['flight_number']
        arrival_departure_date = request.form['arrival_departure_date']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM Flight WHERE airline_name = %s AND flight_no = %s AND (departure_date = %s OR arrival_date = %s)"
        values = (airline_name, flight_number, arrival_departure_date, arrival_departure_date)
        cursor.execute(query, values)
        flight = cursor.fetchone()

        cursor.close()
        conn.close()

        if flight:
            return render_template('flight_status.html', flight=flight)
        else:
            return render_template('flight_status.html', error='No flight found.')
    else:
        return render_template('flight_status.html')
    
@app.route('/view_flight_customers', methods=['GET'])
def view_flight_customers():
    if 'user_id' in session and session['user_type'] == 'staff':
        flight_no = request.args.get('flight_no')
        departure_date = request.args.get('departure_date')
        departure_time = request.args.get('departure_time')
        airline_name = request.args.get('airline_name')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT c.email_address, c.first_name, c.last_name
            FROM Customer c
            JOIN Buy b ON c.email_address = b.email_address
            JOIN Ticket t ON b.ticket_ID = t.ticket_ID
            WHERE t.flight_no = %s AND t.departure_date = %s AND t.departure_time = %s AND t.airline_name = %s
        """
        values = (flight_no, departure_date, departure_time, airline_name)
        cursor.execute(query, values)
        customers = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('flight_customers.html', customers=customers)
    else:
        return redirect(url_for('login'))

@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
    if 'user_id' in session and session['user_type'] == 'staff':
        if request.method == 'POST':
            flight_no = request.form['flight_no']
            departure_date = request.form['departure_date']
            departure_time = request.form['departure_time']
            airline_name = request.form['airline_name']
            arrival_date = request.form['arrival_date']
            arrival_time = request.form['arrival_time']
            ticket_base_price = request.form['ticket_base_price']
            status = request.form['status']
            airplane_id = request.form['airplane_id']
            departure_airport_code = request.form['departure_airport_code']
            arrival_airport_code = request.form['arrival_airport_code']

            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if the airline exists
            query = "SELECT COUNT(*) FROM Airline WHERE airline_name = %s"
            cursor.execute(query, (airline_name,))
            airline_exists = cursor.fetchone()[0]

            if airline_exists:
                # Check if the airplane exists and belongs to the airline
                query = "SELECT COUNT(*) FROM Airplane WHERE airplane_id = %s AND airline_name = %s"
                cursor.execute(query, (airplane_id, airline_name))
                airplane_exists = cursor.fetchone()[0]

                if airplane_exists:
                    # Insert the new flight into the database
                    query = """
                        INSERT INTO Flight (flight_no, departure_date, departure_time, airline_name, arrival_date, arrival_time, ticket_base_price, status, airplane_id, departure_airport_code, arrival_airport_code)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (flight_no, departure_date, departure_time, airline_name, arrival_date, arrival_time, ticket_base_price, status, airplane_id, departure_airport_code, arrival_airport_code)
                    cursor.execute(query, values)
                    conn.commit()

                    cursor.close()
                    conn.close()

                    return redirect(url_for('staff_dashboard'))
                else:
                    return render_template('create_flight.html', error='Invalid airplane ID')
            else:
                return render_template('create_flight.html', error='Invalid airline name')
        return render_template('create_flight.html')
    return redirect(url_for('login'))

@app.route('/change_flight_status', methods=['POST'])
def change_flight_status():
    if 'user_id' in session and session['user_type'] == 'staff':
        flight_no = request.form['flight_no']
        departure_date = request.form['departure_date']
        departure_time = request.form['departure_time']
        airline_name = request.form['airline_name']
        new_status = request.form['new_status']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the flight status in the database
        query = """
            UPDATE Flight
            SET status = %s
            WHERE flight_no = %s AND departure_date = %s AND departure_time = %s AND airline_name = %s
        """
        values = (new_status, flight_no, departure_date, departure_time, airline_name)
        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('staff_dashboard'))
    return redirect(url_for('login'))


@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    if 'user_id' in session and session['user_type'] == 'staff':
        if request.method == 'POST':
            airline_name = session['airline_name']  # Fetch the airline name from the session
            num_seats = request.form['num_seats']
            manufacturer = request.form['manufacturer']
            model_num = request.form['model_num']
            manufacture_date = request.form['manufacture_date']
            
            # Calculate the age based on the manufacture date
            manufacture_date = datetime.strptime(manufacture_date, '%Y-%m-%d').date()
            age = (date.today() - manufacture_date).days // 365

            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert the new airplane into the database
            query = """
                INSERT INTO Airplane (airline_name, num_seats, manufacturer, model_num, manufacture_date, age)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (airline_name, num_seats, manufacturer, model_num, manufacture_date, age)
            cursor.execute(query, values)
            conn.commit()

            cursor.close()
            conn.close()

            return redirect(url_for('staff_dashboard'))
        return render_template('add_airplane.html')
    return redirect(url_for('login'))


@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
    if 'user_id' in session and session['user_type'] == 'staff':
        if request.method == 'POST':
            airport_code = request.form['airport_code']
            airport_name = request.form['airport_name']
            city = request.form['city']
            country = request.form['country']
            num_terminals = request.form['num_terminals']
            airport_type = request.form['airport_type']

            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert the new airport into the database
            query = """
                INSERT INTO Airport (airport_code, airport_name, city, country, num_terminals, airport_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (airport_code, airport_name, city, country, num_terminals, airport_type)
            cursor.execute(query, values)
            conn.commit()

            cursor.close()
            conn.close()

            return redirect(url_for('staff_dashboard'))
        return render_template('add_airport.html')
    return redirect(url_for('login'))


@app.route('/view_flight_ratings', methods=['GET'])
def view_flight_ratings():
    if 'user_id' in session and session['user_type'] == 'staff':
        flight_no = request.args.get('flight_no')
        departure_date = request.args.get('departure_date')
        departure_time = request.args.get('departure_time')
        airline_name = request.args.get('airline_name')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve flight ratings and comments from the database
        query = """
            SELECT rate, comment
            FROM Review
            WHERE flight_no = %s AND departure_date = %s AND departure_time = %s AND airline_name = %s
        """
        values = (flight_no, departure_date, departure_time, airline_name)
        cursor.execute(query, values)
        ratings = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('flight_ratings.html', ratings=ratings)
    return redirect(url_for('login'))


@app.route('/schedule_maintenance', methods=['GET', 'POST'])
def schedule_maintenance():
    if 'user_id' in session and session['user_type'] == 'staff':
        if request.method == 'POST':
            airplane_id = request.form['airplane_id']
            start_date = request.form['start_date']
            start_time = request.form['start_time']
            end_date = request.form['end_date']
            end_time = request.form['end_time']

            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if the airplane exists
            query = "SELECT COUNT(*) FROM Airplane WHERE airplane_id = %s"
            cursor.execute(query, (airplane_id,))
            airplane_exists = cursor.fetchone()[0]

            if airplane_exists:
                # Insert the maintenance schedule into the database
                query = """
                    INSERT INTO Maintenance (airplane_id, start_date, start_time, end_date, end_time)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (airplane_id, start_date, start_time, end_date, end_time)
                cursor.execute(query, values)
                conn.commit()

                cursor.close()
                conn.close()

                return redirect(url_for('staff_dashboard'))
            else:
                return render_template('schedule_maintenance.html', error='Invalid airplane ID')
        return render_template('schedule_maintenance.html')
    return redirect(url_for('login'))


@app.route('/view_frequent_customers', methods=['GET'])
def view_frequent_customers():
    if 'user_id' in session and session['user_type'] == 'staff':
        airline_name = session['user_id']  # Assuming airline staff username is the airline name

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve the most frequent customers within the last year
        query = """
            SELECT c.email_address, c.first_name, c.last_name, COUNT(*) AS flight_count
            FROM Customer c
            JOIN Buy b ON c.email_address = b.email_address
            JOIN Ticket t ON b.ticket_ID = t.ticket_ID
            JOIN Flight f ON t.flight_no = f.flight_no AND t.departure_date = f.departure_date AND t.departure_time = f.departure_time AND t.airline_name = f.airline_name
            WHERE f.airline_name = %s AND b.buy_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            GROUP BY c.email_address, c.first_name, c.last_name
            ORDER BY flight_count DESC
            LIMIT 1
        """
        cursor.execute(query, (airline_name,))
        frequent_customers = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('frequent_customers.html', customers=frequent_customers)
    return redirect(url_for('login'))

@app.route('/view_earned_revenue', methods=['GET'])
def view_earned_revenue():
    if 'user_id' in session and session['user_type'] == 'staff':
        airline_name = session['user_id']  # Assuming airline staff username is the airline name

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve the total revenue earned from ticket sales in the last month
        query = """
            SELECT SUM(t.ticket_price) AS total_revenue_month
            FROM Ticket t
            JOIN Flight f ON t.flight_no = f.flight_no AND t.departure_date = f.departure_date AND t.departure_time = f.departure_time AND t.airline_name = f.airline_name
            JOIN Buy b ON t.ticket_ID = b.ticket_ID
            WHERE f.airline_name = %s AND b.buy_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        """
        cursor.execute(query, (airline_name,))
        total_revenue_month = cursor.fetchone()[0]

        # Retrieve the total revenue earned from ticket sales in the last year
        query = """
            SELECT SUM(t.ticket_price) AS total_revenue_year
            FROM Ticket t
            JOIN Flight f ON t.flight_no = f.flight_no AND t.departure_date = f.departure_date AND t.departure_time = f.departure_time AND t.airline_name = f.airline_name
            JOIN Buy b ON t.ticket_ID = b.ticket_ID
            WHERE f.airline_name = %s AND b.buy_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        """
        cursor.execute(query, (airline_name,))
        total_revenue_year = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return render_template('earned_revenue.html', revenue_month=total_revenue_month, revenue_year=total_revenue_year)
    return redirect(url_for('login'))

@app.route('/staff_dashboard')
def staff_dashboard():
    if 'user_id' in session and session['user_type'] == 'staff':
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM Flight WHERE airline_name = (SELECT airline_name FROM AirlineStaff WHERE username = %s)"
        cursor.execute(query, (session['user_id'],))
        flights = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('staff_dashboard.html', user_id=session['user_id'], flights=flights)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)