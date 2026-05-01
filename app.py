from flask import Flask, render_template, redirect, url_for, request, session, flash
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from database import db, cursor
import bcrypt
import razorpay

app = Flask(__name__)
app.secret_key = "ecommerce@2025"

# ---------------- TOKEN SERIALIZER ----------------   
s = URLSafeTimedSerializer(app.secret_key)

#---------------- RAZORPAY ---------------- 
RAZORPAY_KEY_ID = "rzp_test_Rn24fP1HWd2Zb6"
RAZORPAY_KEY_SECRET = "rR5ZAwhYTfNfJNzQqMeGZ5yQ"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# ---------------- SMTP CONFIGURATION ---------------- 
SMTP_EMAIL = "vlmgopal2004@gmail.com"
SMTP_PASSWORD = "algb hsms kjys npqm"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ---------------- EMAIL SENDER FUNCTION ---------------- 
def send_email(subject, receiver_email, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True

    except Exception as e:
        print("Email Error:", e)
        return False  

# ---------------- DASHBOARD ----------------
@app.route('/')
def dashboard():
    cursor.execute("SELECT * FROM products WHERE status='active'")
    products = cursor.fetchall()
    return render_template('dashboard.html', products=products)

# ---------------- PRODUCT DETAILS ----------------
@app.route('/product/<int:product_id>')
def product_details(product_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    return render_template('product_details.html', product=product)

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form['phonenumber']
        gender = request.form['gender']

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            flash("Email already registered", "danger")
            return redirect(url_for("register"))

        cursor.execute(
            "INSERT INTO users (username, email, password, phonenumber, gender) VALUES (%s, %s, %s, %s, %s)",
            (username, email, hashed_password, phone, gender)
        )
        db.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        cursor = db.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode("utf-8"), user[2].encode("utf-8")):
            otp = str(random.randint(100000, 999999))
            session["otp"] = otp
            session["temp_user"] = user[0]

            body = f"""
                    Hello {user[1]},
                    Your OTP for login verification is:

                    OTP: {otp}

                    Do not share this OTP with anyone.
            """
            send_email("Login OTP Verification", email, body)
            return redirect(url_for("verify"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")

# ---------------- OTP VERIFICATION ----------------
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        entered_otp = request.form.get("otp")

        if entered_otp == session.get("otp"):
            session["user_id"] = session.get("temp_user")
            session.pop("otp", None)
            session.pop("temp_user", None)
            session["logged_in"] = True

            return redirect(url_for("dashboard"))

        flash("Invalid OTP", "danger")

    return render_template("verify.html")

# ---------------- RESEND OTP ----------------
@app.route("/resend-otp")
def resend_otp():
    if "temp_user" in session:
        # Get user details for the email
        user_id = session.get("temp_user")
        cursor = db.cursor()
        cursor.execute("SELECT username, email FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()

        if user:
            # Generate and save new OTP
            otp = str(random.randint(100000, 999999))
            session["otp"] = otp

            body = f"""
                    Hello {user[0]},
                    Your NEW OTP for login verification is:

                    OTP: {otp}

                    Do not share this OTP with anyone.
            """
            send_email("New Login OTP Verification", user[1], body)
            flash("A new OTP has been sent to your email.", "info")
            return redirect(url_for("verify"))

    flash("Session expired. Please login again.", "danger")
    return redirect(url_for("login"))

#---------------- FORGOT PASSWORD ----------------
@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    if request.method == "POST":
        email = request.form.get("email")

        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            token = s.dumps(email, salt="password-reset-salt")
            reset_url = url_for("resetpassword", token=token, _external=True)

            body = f"""
                    Hello,
                    Click the link below to reset your password:

                    {reset_url}

                    This link will expire in 1 hour.
                """
            send_email("Password Reset Request", email, body)
            flash("Reset link sent to your email", "success")
        else:
            flash("Email not registered", "danger")

    return render_template("forgot_password.html")

#---------------- RESET PASSWORD ----------------
@app.route("/resetpassword/<token>", methods=["GET", "POST"])
def resetpassword(token):
    try:
        email = s.loads(token, salt="password-reset-salt", max_age=3600)
    except SignatureExpired:
        flash("Reset link expired. Try again.", "danger")
        return redirect(url_for("forgotpassword"))

    if request.method == "POST":
        newpassword = request.form.get("newpassword")
        confirmpassword = request.form.get("confirmpassword")

        if newpassword != confirmpassword:
            flash("Passwords do not match", "danger")
            return redirect(request.url)

        hashed = bcrypt.hashpw(newpassword.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        cursor = db.cursor()
        cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed, email))
        db.commit()

        flash("Password updated successfully", "success")
        return redirect(url_for("login"))

    return render_template("resetpassword.html")

#---------------- ADD TO CART ----------------
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, quantity FROM cart 
        WHERE user_id=%s AND product_id=%s
    """, (session['user_id'], product_id))

    item = cursor.fetchone()

    if item:
        cursor.execute("""
            UPDATE cart SET quantity = quantity + 1 
            WHERE id=%s
        """, (item['id'],))
    else:
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity) 
            VALUES (%s, %s, %s)
        """, (session['user_id'], product_id, 1))

    db.commit()

    return redirect(url_for('dashboard'))

# ---------------- CART PAGE ----------------
@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.id as cart_id, c.quantity,
               p.id as product_id, p.name, p.price, p.image, p.status
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (session['user_id'],))

    cart_items = cursor.fetchall()

    # TOTAL PRICE
    total_price = sum((item['price'] or 0) * item['quantity'] for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

#---------------- UPDATE QUANTITY ----------------                     
@app.route('/update_quantity/<int:cart_id>/<string:action>')
def update_quantity(cart_id, action):
    cursor = db.cursor(dictionary=True)

    # Get current quantity
    cursor.execute("SELECT quantity FROM cart WHERE id=%s", (cart_id,))
    item = cursor.fetchone()

    if not item:
        return redirect(url_for('cart'))

    quantity = item['quantity']

    if action == 'increase':
        quantity += 1

        cursor.execute(
            "UPDATE cart SET quantity=%s WHERE id=%s",
            (quantity, cart_id)
        )

    elif action == 'decrease':
        quantity -= 1

        # 🔥 AUTO REMOVE WHEN 0
        if quantity <= 0:
            cursor.execute("DELETE FROM cart WHERE id=%s", (cart_id,))
        else:
            cursor.execute(
                "UPDATE cart SET quantity=%s WHERE id=%s",
                (quantity, cart_id)
            )

    db.commit()

    return redirect(url_for('cart'))

#---------------- TO GET NUMBER OF ITEMS IN CART ----------------
def get_cart_count(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT SUM(quantity) FROM cart WHERE user_id=%s", (user_id,))
    result = cursor.fetchone()

    return result[0] if result[0] else 0
@app.context_processor
def inject_cart_count():
    if 'user_id' in session:
        count = get_cart_count(session['user_id'])
    else:
        count = 0

    return dict(cart_count=count)

#---------------- CHECKOUT ----------------
@app.route('/checkout/<int:product_id>')
def checkout(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()

    if not product:
        return "Product not found", 404

    # ⚠️ IMPORTANT: keep amount SMALL in test mode
    amount = 100 * 100  # ₹100 only

    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template(
        'checkout.html',
        product=product,
        razorpay_order_id=razorpay_order['id'],
        razorpay_key=RAZORPAY_KEY_ID,
        amount=amount
    )

# ---------------- PAYMENT SUCCESS ----------------
@app.route('/payment_success', methods=['POST'])
def payment_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    payment_id = request.form.get("razorpay_payment_id")
    order_id = request.form.get("razorpay_order_id")
    signature = request.form.get("razorpay_signature")
    address = request.form.get("address")

    # 🔐 VERIFY PAYMENT (VERY IMPORTANT)
    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        client.utility.verify_payment_signature(params_dict)

        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO orders 
            (user_id, product_id, quantity, total_price, address, status, payment_mode, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            session.get('product_id'),   # better: store before checkout
            1,
            100,  # test amount
            address,
            "Placed",
            "Razorpay",
            "Completed"
        ))

        db.commit()

        return "<h2>Payment Successful 🎉</h2><a href='/'>Go Home</a>"

    except razorpay.errors.SignatureVerificationError:
        return "<h2>Payment Failed ❌</h2>"

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))



#---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
