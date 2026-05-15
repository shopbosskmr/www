from flask import Flask, request, redirect, session
import psycopg2
import requests
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------- APP ----------------
ShopBoss = Flask(__name__)

# SECURITY KEY
ShopBoss.secret_key = "fayiz"

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

    try:
        cur.execute("""
        ALTER TABLE products
        ADD COLUMN category TEXT DEFAULT 'General'
        """)
        conn.commit()

    except:
        conn.rollback()

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
        padding:10px 14px;
        display:flex;
        align-items:center;
        gap:10px;
        flex-wrap:wrap;
        font-family:Arial;
        box-sizing:border-box;
    ">

        <div style="
            color:#ff9900;
            font-size:24px;
            font-weight:bold;
        ">
            ShopBoss
        </div>

        <form action="/" method="get"
        style="
            flex:1;
            min-width:220px;
            display:flex;
        ">

            <input
            name="q"
            placeholder="Search products"
            style="
                flex:1;
                padding:10px;
                border:none;
                outline:none;
                border-radius:4px 0 0 4px;
            ">

            <button style="
                background:#febd69;
                border:none;
                padding:10px 16px;
                cursor:pointer;
                border-radius:0 4px 4px 0;
            ">
                Search
            </button>

        </form>

        <div style="
            display:flex;
            gap:14px;
            flex-wrap:wrap;
            font-size:14px;
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

        <meta name="viewport"
        content="width=device-width, initial-scale=1.0">

        <meta http-equiv="refresh" content="3;url=/check">

        <title>Welcome To ShopBoss</title>

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
                padding:20px;
                box-sizing:border-box;
                text-align:center;
            }

            .box{
                animation:zoom 2s;
            }

            h1{
                color:#ff9900;
                font-size:clamp(36px,8vw,70px);
                margin:0;
            }

            p{
                color:white;
                font-size:18px;
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

            <h1>Welcome To ShopBoss</h1>

            <p>Kashmir's First Shopping App</p>

        </div>

    </body>

    </html>
    """

# ---------------- CHECK ----------------
@ShopBoss.route("/check")
def check():

    if session.get("user"):
        return redirect("/")

    if not session.get("signedup"):
        return redirect("/signup")

    return redirect("/login")

# ---------------- HOME ----------------
@ShopBoss.route("/")
def home():

    if not session.get("user"):
        return redirect("/splash")

    query = request.args.get("q")

    conn = db()
    cur = conn.cursor()

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

    html = """
    <meta name="viewport"
    content="width=device-width, initial-scale=1.0">
    """

    html += header()

    # -------- CATEGORY BAR --------
    html += """
    <div style="
        background:white;
        padding:12px 14px;
        display:flex;
        gap:10px;
        overflow-x:auto;
        font-family:Arial;
        border-bottom:1px solid #ddd;
        white-space:nowrap;
        box-sizing:border-box;
    ">
    """

    categories = [
        ("🏏 Cricket", "Cricket"),
        ("⚽ Football", "Football"),
        ("👕 Fashion", "Fashion"),
        ("👟 Shoes", "Shoes"),
        ("📱 Electronics", "Electronics"),
        ("🧑‍🍳 Kitchen", "Kitchen")
    ]

    for text, value in categories:

        html += f"""
        <a href="/?q={value}"
        style="
            text-decoration:none;
            background:#f3f3f3;
            padding:8px 14px;
            border-radius:30px;
            color:black;
            font-weight:bold;
            font-size:14px;
            flex-shrink:0;
        ">
            {text}
        </a>
        """

    html += "</div>"

    # -------- PRODUCTS --------
    html += """
    <div style="
        background:#eaeded;
        padding:14px;
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
        gap:14px;
        font-family:Arial;
        box-sizing:border-box;
    ">
    """

    for p in products:

        category = p[4] if len(p) > 4 else "General"

        html += f"""
        <div style="
            background:white;
            padding:10px;
            border-radius:10px;
            box-shadow:0 2px 5px rgba(0,0,0,0.12);
            width:100%;
            box-sizing:border-box;
        ">

            <img loading="lazy" src="{p[3]}"
            style="
                width:100%;
                height:145px;
                object-fit:cover;
                border-radius:8px;
                display:block;
            ">

            <h3 style="
                font-size:15px;
                margin:10px 0 5px;
                min-height:38px;
                overflow:hidden;
            ">
                {p[1]}
            </h3>

            <p style="
                color:#666;
                font-size:13px;
                margin:0;
            ">
                {category}
            </p>

            <h2 style="
                color:green;
                font-size:19px;
                margin:10px 0;
            ">
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
                border-radius:6px;
                font-weight:bold;
                font-size:14px;
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

        existing = cur.fetchone()

        if existing:

            cur.close()
            conn.close()

            return """
            <h2 style='
                font-family:Arial;
                text-align:center;
                margin-top:100px;
                color:red;
            '>
                Username Already Exists
            </h2>
            """

        hashed = generate_password_hash(password)

        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username,hashed)
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
        padding:15px;
        box-sizing:border-box;
    ">

        <form method="post"
        style="
            background:white;
            padding:30px;
            width:100%;
            max-width:320px;
            border-radius:10px;
            box-sizing:border-box;
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
                box-sizing:border-box;
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
                box-sizing:border-box;
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
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):

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
        padding:15px;
        box-sizing:border-box;
    ">

        <form method="post"
        style="
            background:white;
            padding:30px;
            width:100%;
            max-width:320px;
            border-radius:10px;
            box-sizing:border-box;
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
                box-sizing:border-box;
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
                box-sizing:border-box;
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

    html = """
    <meta name="viewport"
    content="width=device-width, initial-scale=1.0">
    """

    html += header()

    html += """
    <div style="
        display:flex;
        flex-wrap:wrap;
        gap:20px;
        padding:14px;
        background:#eaeded;
        font-family:Arial;
        min-height:100vh;
        box-sizing:border-box;
    ">
    """

    html += """
    <div style="
        flex:1;
        min-width:300px;
    ">
    """

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
                padding:14px;
                margin-bottom:20px;
                display:flex;
                gap:15px;
                flex-wrap:wrap;
                border-radius:12px;
                box-shadow:0 2px 6px rgba(0,0,0,0.1);
            ">

                <img src="{p[3]}"
                style="
                    width:130px;
                    height:140px;
                    object-fit:cover;
                    border-radius:10px;
                ">

                <div style="flex:1;min-width:200px;">

                    <h2>{p[1]}</h2>

                    <h3 style="color:green;">
                        ₹{p[2]}
                    </h3>

                    <div style="
                        display:flex;
                        align-items:center;
                        gap:10px;
                        margin-top:15px;
                        flex-wrap:wrap;
                    ">

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

                        <div style="
                            width:50px;
                            text-align:center;
                            font-size:20px;
                            font-weight:bold;
                        ">
                            {qty}
                        </div>

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

                    <h3 style="margin-top:20px;">
                        Subtotal ₹{subtotal}
                    </h3>

                </div>

            </div>
            """

    html += "</div>"

    html += f"""
    <div style="
        width:100%;
        max-width:320px;
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

            <h1 style="color:green;">
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

# ---------------- LOGOUT 
# ---------------- LOGOUT ----------------
@ShopBoss.route("/logout")
def logout():

    # KEEP signup memory
    signedup = session.get("signedup")

    # CLEAR SESSION
    session.clear()

    # RESTORE signup memory
    if signedup:
        session["signedup"] = True

    return redirect("/splash")


# ---------------- RUN ----------------
if __name__ == "__main__":

    init_db()

    ShopBoss.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
                )
