from flask import Flask, request, redirect, session
import psycopg2
import requests

# ---------------- APP ----------------
ShopBoss = Flask(__name__)
ShopBoss.secret_key = "secret123"

# ---------------- DATABASE ----------------
def db():
    return psycopg2.connect(
        host="localhost",
        database="shopboss",
        user="postgres",
        password="123456789"
    )

def init_db():

    conn = db()
    cur = conn.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # PRODUCTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id SERIAL PRIMARY KEY,
        name TEXT,
        price INTEGER,
        image TEXT,
        category TEXT DEFAULT 'General'
    )
    """)

    # ADD CATEGORY COLUMN IF OLD TABLE EXISTS
    try:
        cur.execute("""
        ALTER TABLE products
        ADD COLUMN category TEXT DEFAULT 'General'
        """)
        conn.commit()

    except:
        conn.rollback()

    # DEMO PRODUCTS
    cur.execute("SELECT * FROM products")

    if not cur.fetchall():

        cur.execute("""
        INSERT INTO products(name,price,image,category)
        VALUES
        (
            'iPhone 15',
            120000,
            'https://m.media-amazon.com/images/I/71d7rfSl0wL.jpg',
            'Electronics'
        ),

        (
            'Nike Shoes',
            4500,
            'https://m.media-amazon.com/images/I/61utX8kBDlL._UY695_.jpg',
            'Fashion'
        ),

        (
            'Headphones',
            2500,
            'https://m.media-amazon.com/images/I/61CGHv6kmWL.jpg',
            'Electronics'
        )
        """)

    conn.commit()

    cur.close()
    conn.close()
# ---------------- HEADER ----------------
def header():

    cart = session.get("cart", {})
    count = sum(cart.values())

    return f"""
    <div style="
        background:#131921;
        color:white;
        padding:10px;
        display:flex;
        align-items:center;
        font-family:Arial;
    ">

        <div style="
            color:#ff9900;
            font-size:24px;
            font-weight:bold;
            margin-right:20px;
        ">
            ShopBoss
        </div>

        <form action="/" method="get"
        style="
            flex:1;
            display:flex;
            margin:0 20px;
        ">

            <input
            name="q"
            placeholder="Search products"
            style="
                flex:1;
                padding:10px;
                border:none;
                outline:none;
            ">

            <button style="
                background:#febd69;
                border:none;
                padding:10px 20px;
                cursor:pointer;
            ">
                Search
            </button>

        </form>

        <div style="
            display:flex;
            gap:20px;
        ">

            <a href="/"
            style="color:white;text-decoration:none;">
                Home
            </a>

            <a href="/cart"
            style="color:white;text-decoration:none;">
                Cart ({count})
            </a>

            <a href="/admin"
            style="color:white;text-decoration:none;">
                Admin
            </a>

            <a href="/logout"
            style="color:white;text-decoration:none;">
                Logout
            </a>

        </div>

    </div>
    """

# ---------------- SPLASH ----------------
@ShopBoss.route("/splash")
def splash():

    return """
    <html>

    <head>

        <meta http-equiv="refresh" content="3;url=/check">

        <title>Welcome To Shopboss</title>

        <style>

            body{
                margin:0;
                background:#131921;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
                font-family:Arial;
                overflow:hidden;
            }

            .box{
                text-align:center;
                animation:zoom 2s;
            }

            h1{
                color:#ff9900;
                font-size:70px;
                margin:0;
            }

            p{
                color:white;
                font-size:20px;
                margin-top:10px;
            }
            

            @keyframes zoom{
                from{
                    transform:scale(0.5);
                    opacity:0;
                }

                to{
                    transform:scale(1);
                    opacity:1;
                }
            }

        </style>

    </head>

    <body>

        <div class="box">

            <h1>Welcome To Shopboss</h1>

            <p>Kashmir's First Shopping App</p>

            <div class="loader"></div>

        </div>

    </body>

    </html>
    """
# ---------------- CHECK ----------------
@ShopBoss.route("/check")
def check():

    # USER ALREADY LOGGED IN
    if session.get("user"):

        return redirect("/")

    # FIRST TIME USER
    if not session.get("signedup"):

        return redirect("/signup")

    # USER SIGNED UP BUT NOT LOGGED IN
    return redirect("/login")

# ---------------- HOME ----------------
@ShopBoss.route("/")
def home():

    if not session.get("user"):
        return redirect("/splash")

    query = request.args.get("q")

    conn = db()
    cur = conn.cursor()

    # SEARCH
    if query:

        cur.execute(
            """
            SELECT * FROM products
            WHERE LOWER(name) LIKE LOWER(%s)
            OR LOWER(category) LIKE LOWER(%s)
            ORDER BY id DESC
            """,
            ('%' + query + '%', '%' + query + '%')
        )

    else:

        cur.execute(
            "SELECT * FROM products ORDER BY id DESC"
        )

    products = cur.fetchall()

    cur.close()
    conn.close()

    html = header()

    # -------- CATEGORY BAR --------
    html += """
    <div style="
        background:white;
        padding:15px 20px;
        display:flex;
        gap:15px;
        overflow-x:auto;
        font-family:Arial;
        border-bottom:1px solid #ddd;
    ">

        <a href="/?q=Cricket"
        style="
            text-decoration:none;
            background:#f3f3f3;
            padding:10px 18px;
            border-radius:30px;
            color:black;
            font-weight:bold;
            white-space:nowrap;
        ">
            🏏 Cricket
        </a>

        <a href="/?q=Football"
        style="
            text-decoration:none;
            background:#f3f3f3;
            padding:10px 18px;
            border-radius:30px;
            color:black;
            font-weight:bold;
            white-space:nowrap;
        ">
            ⚽ Football
        </a>

        <a href="/?q=Fashion"
        style="
            text-decoration:none;
            background:#f3f3f3;
            padding:10px 18px;
            border-radius:30px;
            color:black;
            font-weight:bold;
            white-space:nowrap;
        ">
            👕 Fashion
        </a>

        <a href="/?q=Shoes"
        style="
            text-decoration:none;
            background:#f3f3f3;
            padding:10px 18px;
            border-radius:30px;
            color:black;
            font-weight:bold;
            white-space:nowrap;
        ">
            👟 Shoes
        </a>

        <a href="/?q=Electronics"
        style="
            text-decoration:none;
            background:#f3f3f3;
            padding:10px 18px;
            border-radius:30px;
            color:black;
            font-weight:bold;
            white-space:nowrap;
        ">
            📱 Electronics
        </a>

        <a href="/?q=Kitchen"
        style="
            text-decoration:none;
            background:#f3f3f3;
            padding:10px 18px;
            border-radius:30px;
            color:black;
            font-weight:bold;
            white-space:nowrap;
        ">
            🧑‍🍳 Kitchen
        </a>

    </div>
    """

    # -------- PRODUCTS --------
    html += """
    <div style="
        background:#eaeded;
        padding:25px;
        display:flex;
        flex-wrap:wrap;
        gap:20px;
        font-family:Arial;
    ">
    """

    for p in products:

        category = p[4] if len(p) > 4 else "General"

        html += f"""
        <div style="
            width:220px;
            background:white;
            padding:15px;
            border-radius:10px;
            box-shadow:0 2px 5px rgba(0,0,0,0.2);
        ">

            <img src="{p[3]}"
            style="
                width:100%;
                height:220px;
                object-fit:cover;
                border-radius:8px;
            ">

            <h3>{p[1]}</h3>

            <p style="
                color:#555;
                font-size:14px;
            ">
                {category}
            </p>

            <h2 style="color:green;">
                ₹{p[2]}
            </h2>

            <a href="/add/{p[0]}"
            style="
                display:block;
                background:#ffd814;
                padding:10px;
                text-align:center;
                text-decoration:none;
                color:black;
                border-radius:5px;
                font-weight:bold;
            ">
                Add To Cart
            </a>

        </div>
        """

    html += "</div>"

    return html
# ---------------- SIGNUP ----------------
@ShopBoss.route("/signup", methods=["GET","POST"])
def signup():

    if session.get("user"):
        return redirect("/")

    if request.method == "POST":

        username = request.form["u"]
        password = request.form["p"]

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )


        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username,password)
        )

        conn.commit()

        cur.close()
        conn.close()

        session["signedup"] = True
        session["user"] = username

        return redirect("/")

    return """
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        background:#f2f2f2;
        font-family:Arial;
    ">

        <form method="post"
        style="
            background:white;
            padding:30px;
            width:320px;
            border-radius:10px;
        ">

            <h2 style="text-align:center;">
                Sign Up
            </h2>

            <input
            name="u"
            placeholder="Username"
            required
            style="
                width:100%;
                padding:10px;
                margin:10px 0;
            ">

            <input
            type="password"
            name="p"
            placeholder="Password"
            required
            style="
                width:100%;
                padding:10px;
                margin:10px 0;
            ">

            <button
            style="
                width:100%;
                padding:10px;
                background:#ffd814;
                border:none;
            ">
                Sign Up
            </button>

        </form>

    </div>
    """

# ---------------- LOGIN ----------------
@ShopBoss.route("/login", methods=["GET","POST"])
def login():

    if session.get("user"):
        return redirect("/")

    if request.method == "POST":

        username = request.form["u"]
        password = request.form["p"]

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username,password)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:

            session["user"] = username

            return redirect("/")

        return "INVALID LOGIN"

    return """
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        background:#f2f2f2;
        font-family:Arial;
    ">

        <form method="post"
        style="
            background:white;
            padding:30px;
            width:320px;
            border-radius:10px;
        ">

            <h2 style="text-align:center;">
                Login
            </h2>

            <input
            name="u"
            placeholder="Username"
            required
            style="
                width:100%;
                padding:10px;
                margin:10px 0;
            ">

            <input
            type="password"
            name="p"
            placeholder="Password"
            required
            style="
                width:100%;
                padding:10px;
                margin:10px 0;
            ">

            <button
            style="
                width:100%;
                padding:10px;
                background:#ffd814;
                border:none;
            ">
                Login
            </button>

        </form>

    </div>
    """

# ---------------- ADD TO CART ----------------
@ShopBoss.route("/add/<int:id>")
def add(id):

    cart = session.get("cart", {})

    pid = str(id)

    cart[pid] = cart.get(pid, 0) + 1

    session["cart"] = cart

    return redirect("/cart")


# ---------------- MINUS FROM CART ----------------
@ShopBoss.route("/minus/<int:id>")
def minus(id):

    cart = session.get("cart", {})

    pid = str(id)

    if pid in cart:

        cart[pid] -= 1

        # REMOVE ITEM IF 0
        if cart[pid] <= 0:
            del cart[pid]

    session["cart"] = cart

    return redirect("/cart")


# ---------------- DELETE ITEM ----------------
@ShopBoss.route("/delete/<int:id>")
def delete(id):

    cart = session.get("cart", {})

    pid = str(id)

    if pid in cart:
        del cart[pid]

    session["cart"] = cart

    return redirect("/cart")


# ---------------- CART ----------------
@ShopBoss.route("/cart")
def cart():

    cart = session.get("cart", {})

    conn = db()
    cur = conn.cursor()

    total = 0

    html = header()

    html += """
    <div style="
        display:flex;
        padding:30px;
        background:#eaeded;
        font-family:Arial;
        min-height:100vh;
    ">
    """

    # LEFT SIDE
    html += """
    <div style="
        width:70%;
    ">
    """

    # EMPTY CART
    if not cart:

        html += """
        <div style="
            background:white;
            padding:40px;
            border-radius:10px;
            text-align:center;
        ">

            <h1>Your Cart Is Empty 🛒</h1>

            <a href="/"
            style="
                display:inline-block;
                margin-top:20px;
                background:#ffd814;
                padding:12px 20px;
                text-decoration:none;
                color:black;
                border-radius:5px;
                font-weight:bold;
            ">
                Continue Shopping
            </a>

        </div>
        """

    # PRODUCTS
    for pid, qty in cart.items():

        cur.execute(
            "SELECT * FROM products WHERE id=%s",
            (pid,)
        )

        p = cur.fetchone()

        if p:

            subtotal = p[2] * qty

            total += subtotal

            html += f"""
            <div style="
                background:white;
                padding:20px;
                margin-bottom:20px;
                display:flex;
                border-radius:12px;
                box-shadow:0 2px 6px rgba(0,0,0,0.1);
            ">

                <img src="{p[3]}"
                style="
                    width:180px;
                    height:200px;
                    object-fit:cover;
                    border-radius:10px;
                    margin-right:20px;
                ">

                <div style="
                    flex:1;
                ">

                    <h2>{p[1]}</h2>

                    <h3 style="
                        color:green;
                    ">
                        ₹{p[2]}
                    </h3>

                    <div style="
                        display:flex;
                        align-items:center;
                        gap:10px;
                        margin-top:15px;
                    ">

                        <!-- MINUS -->
                        <a href="/minus/{p[0]}"
                        style="
                            width:40px;
                            height:40px;
                            display:flex;
                            justify-content:center;
                            align-items:center;
                            background:#ddd;
                            text-decoration:none;
                            color:black;
                            font-size:22px;
                            border-radius:6px;
                            font-weight:bold;
                        ">
                            -
                        </a>

                        <!-- QUANTITY -->
                        <div style="
                            width:50px;
                            text-align:center;
                            font-size:20px;
                            font-weight:bold;
                        ">
                            {qty}
                        </div>

                        <!-- PLUS -->
                        <a href="/add/{p[0]}"
                        style="
                            width:40px;
                            height:40px;
                            display:flex;
                            justify-content:center;
                            align-items:center;
                            background:#ffd814;
                            text-decoration:none;
                            color:black;
                            font-size:22px;
                            border-radius:6px;
                            font-weight:bold;
                        ">
                            +
                        </a>

                        <!-- DELETE -->
                        <a href="/delete/{p[0]}"
                        style="
                            height:40px;
                            display:flex;
                            justify-content:center;
                            align-items:center;
                            background:red;
                            color:white;
                            padding:0 14px;
                            text-decoration:none;
                            border-radius:6px;
                            font-weight:bold;
                        ">
                            Delete
                        </a>

                    </div>

                    <h3 style="
                        margin-top:20px;
                    ">
                        Subtotal ₹{subtotal}
                    </h3>

                </div>

            </div>
            """

    html += "</div>"

    # RIGHT SIDE
    html += f"""
    <div style="
        width:30%;
        padding-left:20px;
    ">

        <div style="
            background:white;
            padding:25px;
            border-radius:12px;
            box-shadow:0 2px 6px rgba(0,0,0,0.1);
            position:sticky;
            top:20px;
        ">

            <h2>Order Summary</h2>

            <hr>

            <h1 style="
                color:green;
            ">
                ₹{total}
            </h1>

            <a href="/address"
            style="
                display:block;
                margin-top:20px;
                background:#ffd814;
                padding:14px;
                text-align:center;
                text-decoration:none;
                color:black;
                border-radius:6px;
                font-weight:bold;
                font-size:18px;
            ">
                Proceed To Buy
            </a>

        </div>

    </div>
    """

    html += "</div>"

    cur.close()
    conn.close()

    return html

# ---------------- ADDRESS ----------------
@ShopBoss.route("/address", methods=["GET","POST"])
def address():

    if request.method == "POST":

        mobile = request.form["mobile"]
        address = request.form["address"]
        payment = request.form["payment"]

        conn = db()
        cur = conn.cursor()

        total = 0

        message = f"""
NEW ORDER RECEIVED

User: {session.get('user')}

Mobile: {mobile}

Address: {address}

Payment: {payment}

Items:
"""

        for pid, qty in session.get("cart", {}).items():

            cur.execute(
                "SELECT name,price FROM products WHERE id=%s",
                (pid,)
            )

            p = cur.fetchone()

            if p:

                total += p[1] * qty

                message += f"{p[0]} - Qty:{qty} - ₹{p[1]}\n"

        message += f"\nTOTAL = ₹{total}"

        requests.post(
            "https://api.emailjs.com/api/v1.0/email/send",
            headers={
                "Content-Type":"application/json"
            },
            json={
                "service_id":"service_shopboss",
                "template_id":"template_shopboss",
                "user_id":"9bTfVOFVe_u1Mt51L",
                "template_params":{
                    "name":session.get("user"),
                    "email":"kfayizwani@gmail.com",
                    "message":message
                }
            }
        )

        session["cart"] = {}

        return f"""
        <div style="
            height:100vh;
            display:flex;
            justify-content:center;
            align-items:center;
            background:#eaeded;
            font-family:Arial;
        ">

            <div style="
                background:white;
                padding:40px;
                width:400px;
                border-radius:10px;
                text-align:center;
            ">

                <h1 style="color:green;">✔</h1>

                <h2>Order Placed Successfully</h2>

                <h3>Total Paid ₹{total}</h3>

                <a href="/"
                style="
                    display:inline-block;
                    background:#ffd814;
                    padding:12px 20px;
                    text-decoration:none;
                    color:black;
                ">
                    Continue Shopping
                </a>

            </div>

        </div>
        """

    return """
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        background:#f2f2f2;
        font-family:Arial;
    ">

        <form method="post"
        style="
            background:white;
            padding:30px;
            width:350px;
            border-radius:10px;
        ">

            <h2 style="text-align:center;">
                Checkout
            </h2>

            <input
            name="mobile"
            placeholder="Mobile Number"
            required
            style="
                width:100%;
                padding:10px;
                margin:10px 0;
            ">

            <input
            name="address"
            placeholder="Address"
            required
            style="
                width:100%;
                padding:10px;
                margin:10px 0;
            ">

            <h3>Payment Options</h3>

            <input
            type="radio"
            name="payment"
            value="Cash on Delivery"
            required>
            Cash on Delivery

            <br><br>

            <input
            type="radio"
            name="payment"
            value="Online Payment"
            onclick="showQR()">
            Online Payment

            <div id="qrBox"
            style="
                display:none;
                text-align:center;
            ">

                <img src="/static/qr.png"
                style="
                    width:200px;
                    margin-top:15px;
                ">

                <p>Scan & Pay</p>

                <button
                type="button"
                onclick="confirmPayment()"
                style="
                    background:#ffd814;
                    border:none;
                    padding:10px;
                ">
                    Confirm Payment
                </button>

            </div>

            <button
            style="
                width:100%;
                padding:10px;
                margin-top:20px;
                background:#ffd814;
                border:none;
            ">
                Place Order
            </button>

        </form>

    </div>

<script>

let paid = false;

function showQR(){

    document.getElementById("qrBox").style.display = "block";
}

function confirmPayment(){

    paid = true;

    alert("Payment Confirmed");
}

document.querySelector("form").onsubmit = function(){

    let p = document.querySelector('input[name="payment"]:checked');

    if(p.value === "Online Payment" && !paid){

        alert("Confirm QR Payment First");

        return false;
    }

    return true;
}

</script>
"""

# ---------------- ADMIN ----------------
@ShopBoss.route("/admin", methods=["GET","POST"])
def admin():

    if request.method == "POST":

        if request.form["s"] == "fayiz123":

            session["admin"] = True

            return redirect("/panel")

        # return "Wrong Password"

    return """
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        background:#f2f2f2;
        font-family:Arial;
    ">

        <form method="post"
        style="
            background:white;
            padding:30px;
            width:320px;
            border-radius:10px;
        ">

            <h2 style="text-align:center;">
                Admin Login
            </h2>

            <input
            type="password"
            name="s"
            placeholder="Secret Key"
            required
            style="
                width:100%;
                padding:10px;
                margin:10px 0;
            ">

            <button
            style="
                width:100%;
                padding:10px;
                background:#ffd814;
                border:none;
            ">
                Login
            </button>

        </form>

    </div>
    """

# ---------------- PANEL ----------------
@ShopBoss.route("/panel", methods=["GET","POST"])
def panel():

    if not session.get("admin"):
        return redirect("/admin")

    conn = db()
    cur = conn.cursor()

    # -------- ADD PRODUCT --------
    if request.method == "POST":

        # ADD
        if "add" in request.form:

            cur.execute(
                """
                INSERT INTO products(name,price,image,category)
                VALUES(%s,%s,%s,%s)
                """,
                (
                    request.form["name"],
                    request.form["price"],
                    request.form["image"],
                    request.form["category"]
                )
            )

        # UPDATE
        elif "update" in request.form:

            cur.execute(
                """
                UPDATE products
                SET name=%s, price=%s, image=%s, category=%s
                WHERE id=%s
                """,
                (
                    request.form["name"],
                    request.form["price"],
                    request.form["image"],
                    request.form["category"],
                    request.form["id"]
                )
            )

        # DELETE
        elif "delete" in request.form:

            cur.execute(
                "DELETE FROM products WHERE id=%s",
                (request.form["id"],)
            )

        conn.commit()

    # GET PRODUCTS
    cur.execute("SELECT * FROM products ORDER BY id DESC")

    products = cur.fetchall()

    html = header()

    html += """
    <div style="
        background:#eaeded;
        min-height:100vh;
        padding:25px;
        font-family:Arial;
    ">

        <!-- TOP BAR -->
        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:20px;
        ">

            <h1>Admin Panel</h1>

        </div>

        <!-- ADD PRODUCT BOX -->
        <div style="
            background:white;
            padding:20px;
            border-radius:10px;
            margin-bottom:25px;
            box-shadow:0 2px 8px rgba(0,0,0,0.1);
        ">

            <h2>Add Product</h2>

            <form method="post"
            style="
                display:flex;
                gap:10px;
                flex-wrap:wrap;
            ">

                <input
                name="name"
                placeholder="Product Name"
                required
                style="
                    flex:1;
                    padding:10px;
                ">

                <input
                name="price"
                placeholder="Price"
                required
                style="
                    width:120px;
                    padding:10px;
                ">

                <input
                name="image"
                placeholder="Image URL"
                required
                style="
                    flex:2;
                    padding:10px;
                ">

                <select
                name="category"
                required
                style="
                    padding:10px;
                ">

                    <option value="">Category</option>

                    <option>Cricket</option>

                    <option>Football</option>

                    <option>Fashion</option>

                    <option>Electronics</option>

                    <option>Kitchen</option>

                </select>

                <button
                name="add"
                style="
                    background:#ffd814;
                    border:none;
                    padding:10px 20px;
                    cursor:pointer;
                    font-weight:bold;
                ">
                    Add
                </button>

            </form>

        </div>

        <!-- PRODUCTS GRID -->
        <div style="
            display:grid;
            grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
            gap:20px;
        ">
    """

    # -------- PRODUCTS --------
    for p in products:

        category = p[4] if len(p) > 4 else "General"

        html += f"""
        <div style="
            background:white;
            padding:15px;
            border-radius:10px;
            box-shadow:0 2px 8px rgba(0,0,0,0.1);
        ">

            <img src="{p[3]}"
            style="
                width:100%;
                height:220px;
                object-fit:cover;
                border-radius:8px;
            ">

            <form method="post"
            style="
                margin-top:12px;
                display:flex;
                flex-direction:column;
                gap:10px;
            ">

                <input type="hidden" name="id" value="{p[0]}">

                <input
                name="name"
                value="{p[1]}"
                style="padding:10px;">

                <input
                name="price"
                value="{p[2]}"
                style="padding:10px;">

                <input
                name="image"
                value="{p[3]}"
                style="padding:10px;">

                <select
                name="category"
                style="padding:10px;">

                    <option {"selected" if category=="Cricket" else ""}>
                        Cricket
                    </option>

                    <option {"selected" if category=="Football" else ""}>
                        Football
                    </option>

                    <option {"selected" if category=="Fashion" else ""}>
                        Fashion
                    </option>

                    <option {"selected" if category=="Electronics" else ""}>
                        Electronics
                    </option>

                </select>

                <div style="display:flex;gap:10px;">

                    <button
                    name="update"
                    style="
                        flex:1;
                        background:green;
                        color:white;
                        border:none;
                        padding:10px;
                        cursor:pointer;
                    ">
                        Update
                    </button>

                    <button
                    name="delete"
                    style="
                        flex:1;
                        background:red;
                        color:white;
                        border:none;
                        padding:10px;
                        cursor:pointer;
                    ">
                        Delete
                    </button>

                </div>

            </form>

        </div>
        """

    html += """
        </div>
    </div>
    """

    cur.close()
    conn.close()

    return html

# ---------------- LOGOUT ----------------
@ShopBoss.route("/logout")
def logout():

    session.clear()

    return redirect("/splash")

# ---------------- RUN ----------------
if __name__ == "__main__":

    init_db()

    ShopBoss.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )