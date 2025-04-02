from flask import Flask, render_template, request, session, redirect, url_for

import mysql.connector


db = mysql.connector.connect(
    host="localhost",
    user="restaurant_user",
    password="password123",
    database="restaurant_db"
)

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # used for session security

@app.route('/')
def home():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu_items WHERE availability = TRUE")
    menu_items = cursor.fetchall()
    cursor.close()
    return render_template('customer_home.html', menu_items=menu_items)



@app.route('/place_order', methods=['POST'])
def place_order():
    selected_items = request.form.getlist('items')
    if not selected_items:
        return "No items selected."

    cursor = db.cursor(dictionary=True)
    total_price = 0
    order_items_data = []

    for item_id in selected_items:
        quantity = int(request.form.get(f'quantity_{item_id}', 1))
        cursor.execute("SELECT name, price FROM menu_items WHERE item_id = %s", (item_id,))
        item = cursor.fetchone()
        if item:
            subtotal = item['price'] * quantity
            total_price += subtotal
            order_items_data.append({
                'item_id': item_id,
                'name': item['name'],
                'quantity': quantity,
                'subtotal': subtotal
            })

    # Insert order
    cursor.execute("INSERT INTO orders (total_price) VALUES (%s)", (total_price,))
    order_id = cursor.lastrowid

    # Insert order items
    for item in order_items_data:
        cursor.execute("""
            INSERT INTO order_items (order_id, item_id, quantity, subtotal)
            VALUES (%s, %s, %s, %s)
        """, (order_id, item['item_id'], item['quantity'], item['subtotal']))

    db.commit()
    cursor.close()

    return render_template('order_success.html', order_id=order_id, total_price=round(total_price, 2), order_items=order_items_data)


    # Insert into orders table
    cursor.execute("INSERT INTO orders (total_price) VALUES (%s)", (total_price,))
    order_id = cursor.lastrowid

    # Insert into order_items table
    for item_id, quantity, subtotal in order_items_data:
        cursor.execute("""
            INSERT INTO order_items (order_id, item_id, quantity, subtotal)
            VALUES (%s, %s, %s, %s)
        """, (order_id, item_id, quantity, subtotal))

    db.commit()
    cursor.close()

    return f"✅ Order placed successfully! Order ID: {order_id}, Total: ${total_price:.2f}"

@app.route('/track_order', methods=['GET', 'POST'])
def track_order():
    if request.method == 'POST':
        order_id = request.form.get('order_id')

        cursor = db.cursor(dictionary=True)

        # Get order info
        cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()

        if not order:
            cursor.close()
            return render_template('track_order.html', error="Order not found.")

        # Get items in that order
        cursor.execute("""
            SELECT mi.name, oi.quantity, oi.subtotal
            FROM order_items oi
            JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        cursor.close()

        return render_template('track_order.html', order=order, items=items)

    return render_template('track_order.html')

import bcrypt

@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM restaurant_staff WHERE username = %s", (username,))
        staff = cursor.fetchone()
        cursor.close()

        if staff and bcrypt.checkpw(password.encode('utf-8'), staff['password'].encode('utf-8')):
            session['staff_id'] = staff['staff_id']
            session['staff_name'] = staff['name']
            session['staff_role'] = staff['role']  
            return redirect(url_for('staff_dashboard'))

        else:
            return render_template('staff_login.html', error="Invalid credentials")

    return render_template('staff_login.html')

@app.route('/staff')
def staff_dashboard():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders ORDER BY order_date DESC")
    orders = cursor.fetchall()
    cursor.close()
    return render_template('staff_dashboard.html', orders=orders)

@app.route('/staff_logout')
def staff_logout():
    session.clear()
    return redirect(url_for('staff_login'))


@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    # Make sure the user is logged in and is staff
    if not session.get('staff_id'):
        return redirect(url_for('staff_login'))

    # Get the order ID and new status from the form
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')

    # Validate inputs
    if not order_id or not new_status:
        return "Invalid data provided.", 400

    # Update the order in the database
    cursor = db.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (new_status, order_id))
    db.commit()
    cursor.close()

    # Redirect back to the staff dashboard
    return redirect(url_for('staff_dashboard'))


    return redirect(url_for('staff_login'))

@app.route('/register_staff', methods=['GET', 'POST'])
def register_staff():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    if session.get('staff_role') != 'Manager':
        return "❌ Unauthorized: Managers only.", 403

    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO restaurant_staff (name, username, password, role)
                VALUES (%s, %s, %s, %s)
            """, (name, username, hashed_pw, role))
            db.commit()
            cursor.close()
            return render_template('register_staff.html', success=f"Staff '{name}' registered successfully.")
        except mysql.connector.errors.IntegrityError:
            return render_template('register_staff.html', error="Username already exists.")

    return render_template('register_staff.html')

@app.route('/manage_staff')
def manage_staff():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    if session.get('staff_role') != 'Manager':
        return "❌ Unauthorized: Managers only.", 403

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT staff_id, name, username, role FROM restaurant_staff")
    staff_list = cursor.fetchall()
    cursor.close()

    return render_template('manage_staff.html', staff_list=staff_list)

@app.route('/delete_staff', methods=['POST'])
def delete_staff():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    if session.get('staff_role') != 'Manager':
        return "❌ Unauthorized: Managers only.", 403

    staff_id_to_delete = int(request.form.get('staff_id'))

    # Prevent deleting self
    if staff_id_to_delete == session['staff_id']:
        return "❌ You cannot delete yourself.", 400

    cursor = db.cursor()
    cursor.execute("DELETE FROM restaurant_staff WHERE staff_id = %s", (staff_id_to_delete,))
    db.commit()
    cursor.close()

    return redirect(url_for('manage_staff'))

@app.route('/manage_menu')
def manage_menu():
    if 'staff_id' not in session or session.get('staff_role') != 'Manager':
        return "❌ Unauthorized: Managers only.", 403

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu_items")
    menu_items = cursor.fetchall()
    cursor.close()

    return render_template('manage_menu.html', menu_items=menu_items)

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    if 'staff_id' not in session or session.get('staff_role') != 'Manager':
        return "❌ Unauthorized: Managers only.", 403

    name = request.form['name']
    description = request.form.get('description', '')
    price = float(request.form['price'])
    category = request.form.get('category', '')
    availability = 1 if 'availability' in request.form else 0

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO menu_items (name, description, price, category, availability)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, description, price, category, availability))
    db.commit()
    cursor.close()

    return redirect(url_for('manage_menu'))

@app.route('/update_menu_item', methods=['POST'])
def update_menu_item():
    if 'staff_id' not in session or session.get('staff_role') != 'Manager':
        return "❌ Unauthorized: Managers only.", 403

    item_id = request.form['item_id']
    name = request.form['name']
    price = float(request.form['price'])
    category = request.form['category']
    availability = int(request.form['availability'])

    cursor = db.cursor()
    cursor.execute("""
        UPDATE menu_items
        SET name = %s, price = %s, category = %s, availability = %s
        WHERE item_id = %s
    """, (name, price, category, availability, item_id))
    db.commit()
    cursor.close()

    return redirect(url_for('manage_menu'))
@app.route('/delete_menu_item', methods=['POST'])
def delete_menu_item():
    if 'staff_id' not in session or session.get('staff_role') != 'Manager':
        return "❌ Unauthorized: Managers only.", 403

    item_id = request.form['item_id']

    cursor = db.cursor()
    cursor.execute("DELETE FROM menu_items WHERE item_id = %s", (item_id,))
    db.commit()
    cursor.close()

    return redirect(url_for('manage_menu'))

@app.route('/order_history')
def order_history():
    if 'staff_id' not in session or session.get('staff_role') != 'Manager':
        return "❌ Unauthorized: Managers only.", 403

    cursor = db.cursor(dictionary=True)

    # Get all orders
    cursor.execute("SELECT * FROM orders ORDER BY order_date DESC")
    orders_raw = cursor.fetchall()

    orders = []

    for order in orders_raw:
        cursor.execute("""
            SELECT mi.name, oi.quantity, oi.subtotal
            FROM order_items oi
            JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE oi.order_id = %s
        """, (order['order_id'],))
        items = cursor.fetchall()
        order['items'] = items
        orders.append(order)

    cursor.close()

    return render_template('order_history.html', orders=orders)

@app.route('/add_shift', methods=['POST'])
def add_shift():
    if 'staff_id' not in session or session.get('staff_role') != 'Manager':
        return "❌ Unauthorized", 403

    staff_id = request.form['staff_id']
    shift_date = request.form['shift_date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO staff_shifts (staff_id, shift_date, start_time, end_time)
        VALUES (%s, %s, %s, %s)
    """, (staff_id, shift_date, start_time, end_time))
    db.commit()
    cursor.close()

    return redirect(url_for('manage_shifts'))

@app.route('/manage_shifts')
def manage_shifts():
    if 'staff_id' not in session or session.get('staff_role') != 'Manager':
        return "❌ Unauthorized", 403

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT staff_id, name, role FROM restaurant_staff")
    staff_list = cursor.fetchall()

    cursor.execute("""
        SELECT s.name, s.role, sh.shift_date, sh.start_time, sh.end_time,
               TIMESTAMPDIFF(MINUTE, sh.start_time, sh.end_time)/60 AS hours
        FROM staff_shifts sh
        JOIN restaurant_staff s ON sh.staff_id = s.staff_id
        ORDER BY sh.shift_date DESC, sh.start_time ASC
    """)
    shifts = cursor.fetchall()
    cursor.close()

    return render_template('manage_shifts.html', staff_list=staff_list, shifts=shifts)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
