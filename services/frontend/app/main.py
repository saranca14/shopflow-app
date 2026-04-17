import httpx
from flask import Flask, render_template, request, redirect, url_for, session, flash
from app.config import Config

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)
app.secret_key = Config.SECRET_KEY


# ---------- Helper: HTTP Client ----------
def _api_get(base_url: str, path: str, timeout: float = 5.0):
    try:
        resp = httpx.get(f"{base_url}{path}", timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def _api_post(base_url: str, path: str, json_data: dict, timeout: float = 5.0):
    try:
        resp = httpx.post(f"{base_url}{path}", json=json_data, timeout=timeout)
        return resp.json(), resp.status_code
    except Exception:
        return None, 500


def _api_delete(base_url: str, path: str, timeout: float = 5.0):
    try:
        resp = httpx.delete(f"{base_url}{path}", timeout=timeout)
        return resp.status_code
    except Exception:
        return 500


def _get_user_id():
    return session.get("user_id", "guest")


# ---------- Routes: Home / Products ----------

@app.route("/")
def home():
    """Home page — product listing."""
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category")
    search = request.args.get("search")

    params = f"?page={page}&page_size=12"
    if category:
        params += f"&category={category}"
    if search:
        params += f"&search={search}"

    data = _api_get(Config.PRODUCT_SERVICE_URL, f"/api/v1/products/{params}")
    products = data.get("items", []) if data else []
    total_pages = data.get("total_pages", 0) if data else 0

    # Get cart count
    cart_data = _api_get(Config.CART_SERVICE_URL, f"/api/v1/cart/{_get_user_id()}")
    cart_count = cart_data.get("total_items", 0) if cart_data else 0

    return render_template(
        "home.html",
        products=products,
        page=page,
        total_pages=total_pages,
        category=category,
        search=search or "",
        cart_count=cart_count,
        user=session.get("username"),
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    """Product detail page."""
    product = _api_get(Config.PRODUCT_SERVICE_URL, f"/api/v1/products/{product_id}")
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("home"))

    cart_data = _api_get(Config.CART_SERVICE_URL, f"/api/v1/cart/{_get_user_id()}")
    cart_count = cart_data.get("total_items", 0) if cart_data else 0

    return render_template(
        "product_detail.html",
        product=product,
        cart_count=cart_count,
        user=session.get("username"),
    )


# ---------- Routes: Cart ----------

@app.route("/cart")
def cart():
    """Shopping cart page."""
    cart_data = _api_get(Config.CART_SERVICE_URL, f"/api/v1/cart/{_get_user_id()}")
    items = cart_data.get("items", []) if cart_data else []
    total_price = cart_data.get("total_price", 0) if cart_data else 0
    cart_count = cart_data.get("total_items", 0) if cart_data else 0

    return render_template(
        "cart.html",
        items=items,
        total_price=total_price,
        cart_count=cart_count,
        user=session.get("username"),
    )


@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    """Add product to cart."""
    product_id = request.form.get("product_id", type=int)
    quantity = request.form.get("quantity", 1, type=int)

    _api_post(
        Config.CART_SERVICE_URL,
        f"/api/v1/cart/{_get_user_id()}/add",
        {"product_id": product_id, "quantity": quantity},
    )
    flash("Item added to cart!", "success")
    return redirect(request.referrer or url_for("home"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    """Remove item from cart."""
    _api_delete(Config.CART_SERVICE_URL, f"/api/v1/cart/{_get_user_id()}/remove/{product_id}")
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart"))


@app.route("/cart/clear", methods=["POST"])
def clear_cart():
    """Clear entire cart."""
    _api_delete(Config.CART_SERVICE_URL, f"/api/v1/cart/{_get_user_id()}/clear")
    flash("Cart cleared.", "info")
    return redirect(url_for("cart"))


# ---------- Routes: Checkout / Orders ----------

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    """Checkout page."""
    if not session.get("user_id"):
        flash("Please login to checkout.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        address = request.form.get("address", "")
        result, status = _api_post(
            Config.ORDER_SERVICE_URL,
            "/api/v1/orders/",
            {"user_id": str(session["user_id"]), "shipping_address": address},
        )

        if status == 201 and result:
            flash(f"Order #{result.get('id')} placed successfully!", "success")
            return redirect(url_for("order_detail", order_id=result["id"]))
        else:
            error_msg = result.get("detail", "Failed to place order") if result else "Service unavailable"
            flash(error_msg, "error")

    cart_data = _api_get(Config.CART_SERVICE_URL, f"/api/v1/cart/{_get_user_id()}")
    items = cart_data.get("items", []) if cart_data else []
    total_price = cart_data.get("total_price", 0) if cart_data else 0
    cart_count = cart_data.get("total_items", 0) if cart_data else 0

    return render_template(
        "checkout.html",
        items=items,
        total_price=total_price,
        cart_count=cart_count,
        user=session.get("username"),
    )


@app.route("/orders")
def orders():
    """User's order history."""
    if not session.get("user_id"):
        flash("Please login to view orders.", "warning")
        return redirect(url_for("login"))

    user_orders = _api_get(
        Config.ORDER_SERVICE_URL,
        f"/api/v1/orders/user/{session['user_id']}",
    )
    if user_orders is None:
        user_orders = []

    cart_data = _api_get(Config.CART_SERVICE_URL, f"/api/v1/cart/{_get_user_id()}")
    cart_count = cart_data.get("total_items", 0) if cart_data else 0

    return render_template(
        "orders.html",
        orders=user_orders,
        cart_count=cart_count,
        user=session.get("username"),
    )


@app.route("/orders/<int:order_id>")
def order_detail(order_id):
    """Order detail page."""
    order = _api_get(Config.ORDER_SERVICE_URL, f"/api/v1/orders/{order_id}")
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders"))

    cart_data = _api_get(Config.CART_SERVICE_URL, f"/api/v1/cart/{_get_user_id()}")
    cart_count = cart_data.get("total_items", 0) if cart_data else 0

    return render_template(
        "order_detail.html",
        order=order,
        cart_count=cart_count,
        user=session.get("username"),
    )


# ---------- Routes: Auth ----------

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        result, status = _api_post(
            Config.USER_SERVICE_URL,
            "/api/v1/users/login",
            {"username": username, "password": password},
        )

        if status == 200 and result:
            session["user_id"] = result["user_id"]
            session["username"] = result["username"]
            session["token"] = result["access_token"]
            flash(f"Welcome back, {result['username']}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials.", "error")

    return render_template("login.html", user=session.get("username"), cart_count=0)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page."""
    if request.method == "POST":
        data = {
            "email": request.form.get("email"),
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "full_name": request.form.get("full_name"),
        }

        result, status = _api_post(
            Config.USER_SERVICE_URL, "/api/v1/users/register", data
        )

        if status == 201:
            flash("Account created! Please login.", "success")
            return redirect(url_for("login"))
        else:
            error_msg = result.get("detail", "Registration failed") if result else "Service unavailable"
            flash(error_msg, "error")

    return render_template("register.html", user=session.get("username"), cart_count=0)


@app.route("/logout")
def logout():
    """Logout."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# ---------- Health ----------

@app.route("/health")
def health():
    return {"status": "healthy", "service": Config.APP_NAME}
