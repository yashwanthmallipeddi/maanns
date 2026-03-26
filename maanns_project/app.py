from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'maanns_super_secret_key_2024'

# ─── Connect to MongoDB ────────────────────────────────────────────────────────
client = MongoClient('mongodb://localhost:27017/')
db = client['maans_db']

users_col    = db['users']
products_col = db['products']
cart_col     = db['cart']
orders_col   = db['orders']

# ─── Add Sample Products Once ──────────────────────────────────────────────────
def seed_products():
    if products_col.count_documents({}) == 0:
        products = [
            # ── Shirts
            {
                'name': 'Classic White Shirt',
                'category': 'shirts',
                'price': 999,
                'old_price': 1299,
                'image': 'https://images.unsplash.com/photo-1603252109303-2751441dd157?w=500&q=80',
                'description': 'Premium 100% cotton formal shirt. Perfect for office & events.',
                'sizes': ['S', 'M', 'L', 'XL']
            },
            {
                'name': 'Oxford Blue Shirt',
                'category': 'shirts',
                'price': 1199,
                'old_price': 1499,
                'image': 'https://images.unsplash.com/photo-1598032895397-b9472444bf93?w=500&q=80',
                'description': 'Slim fit oxford weave shirt. A wardrobe essential.',
                'sizes': ['S', 'M', 'L', 'XL']
            },
            {
                'name': 'Midnight Black Shirt',
                'category': 'shirts',
                'price': 1099,
                'old_price': 1399,
                'image': 'https://images.unsplash.com/photo-1594938298603-c8148c4b4a41?w=500&q=80',
                'description': 'Elegant black formal shirt for sharp evenings.',
                'sizes': ['S', 'M', 'L', 'XL']
            },
            # ── T-Shirts
            {
                'name': 'Essential White Tee',
                'category': 'tshirts',
                'price': 499,
                'old_price': 699,
                'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80',
                'description': 'Super soft 100% cotton basic tee. Goes with everything.',
                'sizes': ['S', 'M', 'L', 'XL', 'XXL']
            },
            {
                'name': 'Urban Graphic Tee',
                'category': 'tshirts',
                'price': 599,
                'old_price': 799,
                'image': 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500&q=80',
                'description': 'Trendy street-style graphic print t-shirt.',
                'sizes': ['S', 'M', 'L', 'XL']
            },
            {
                'name': 'Classic Polo Tee',
                'category': 'tshirts',
                'price': 799,
                'old_price': 999,
                'image': 'https://images.unsplash.com/photo-1625910513316-87c0d1f4bf4f?w=500&q=80',
                'description': 'Premium polo collar t-shirt with embroidered logo.',
                'sizes': ['S', 'M', 'L', 'XL']
            },
            # ── Pants
            {
                'name': 'Slim Chino Pants',
                'category': 'pants',
                'price': 1499,
                'old_price': 1799,
                'image': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&q=80',
                'description': 'Modern slim fit chino. Versatile for work and casual wear.',
                'sizes': ['28', '30', '32', '34', '36']
            },
            {
                'name': 'Black Formal Trousers',
                'category': 'pants',
                'price': 1699,
                'old_price': 1999,
                'image': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=500&q=80',
                'description': 'Tailored formal trousers. Crisp and professional.',
                'sizes': ['28', '30', '32', '34', '36']
            },
            {
                'name': 'Dark Slim Jeans',
                'category': 'pants',
                'price': 1899,
                'old_price': 2299,
                'image': 'https://images.unsplash.com/photo-1555689502-c4b22d76c56f?w=500&q=80',
                'description': 'Dark wash slim-fit denim. Perfect everyday style.',
                'sizes': ['28', '30', '32', '34', '36']
            },
            # ── Tracks
            {
                'name': 'Pro Sports Track',
                'category': 'tracks',
                'price': 899,
                'old_price': 1199,
                'image': 'https://images.unsplash.com/photo-1539185441755-769473a23570?w=500&q=80',
                'description': 'Lightweight sports track pants for gym and run.',
                'sizes': ['S', 'M', 'L', 'XL']
            },
            {
                'name': 'Comfort Jogger Track',
                'category': 'tracks',
                'price': 999,
                'old_price': 1299,
                'image': 'https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500&q=80',
                'description': 'Super cozy cotton blend jogger pants.',
                'sizes': ['S', 'M', 'L', 'XL', 'XXL']
            },
            # ── Shorts
            {
                'name': 'Training Shorts',
                'category': 'shorts',
                'price': 599,
                'old_price': 799,
                'image': 'https://images.unsplash.com/photo-1591195853828-11db59a44f43?w=500&q=80',
                'description': 'Breathable training shorts with quick-dry fabric.',
                'sizes': ['S', 'M', 'L', 'XL']
            },
            {
                'name': 'Summer Casual Shorts',
                'category': 'shorts',
                'price': 699,
                'old_price': 899,
                'image': 'https://images.unsplash.com/photo-1562183241-840b8af0721e?w=500&q=80',
                'description': 'Relaxed fit casual shorts for everyday comfort.',
                'sizes': ['28', '30', '32', '34']
            },
        ]
        products_col.insert_many(products)
        print("✅ Products seeded!")

seed_products()

# ─── Helper: check if user is logged in ───────────────────────────────────────
def is_logged_in():
    return 'username' in session

# ─── Home Page ─────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    featured = list(products_col.find().limit(6))
    categories = ['shirts', 'tshirts', 'pants', 'tracks', 'shorts']
    quotes = [
        "The New Language of Fashion is You.",
        "Dress Sharp. Think Bold. Be Maans.",
        "Crafted for the Man Who Knows His Worth.",
        "Where Tradition Meets Modern Masculinity.",
        "Style is Not What You Wear — It's How You Wear It."
    ]
    return render_template('index.html', featured=featured, categories=categories, quotes=quotes)

# ─── Signup ────────────────────────────────────────────────────────────────────
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if is_logged_in():
        return redirect(url_for('home'))

    if request.method == 'POST':
        name     = request.form.get('name').strip()
        email    = request.form.get('email').strip().lower()
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')

        # Check if username or email already exists
        if users_col.find_one({'username': username}):
            flash('Username already taken. Try another.', 'error')
            return redirect(url_for('signup'))

        if users_col.find_one({'email': email}):
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('signup'))

        # Save new user with hashed password
        hashed_pw = generate_password_hash(password)
        users_col.insert_one({
            'name': name,
            'email': email,
            'username': username,
            'password': hashed_pw,
            'joined': datetime.now()
        })

        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# ─── Login ─────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')

        user = users_col.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['name']     = user['name']
            flash(f"Welcome back, {user['name']}! 👋", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# ─── Logout ────────────────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# ─── All Products Page ─────────────────────────────────────────────────────────
@app.route('/products')
def products():
    category = request.args.get('category', 'all')
    if category == 'all':
        all_products = list(products_col.find())
    else:
        all_products = list(products_col.find({'category': category}))

    categories = ['all', 'shirts', 'tshirts', 'pants', 'tracks', 'shorts']
    return render_template('products.html', products=all_products, categories=categories, active=category)

# ─── Single Category Page ──────────────────────────────────────────────────────
@app.route('/category/<cat_name>')
def category(cat_name):
    items = list(products_col.find({'category': cat_name}))
    categories = ['all', 'shirts', 'tshirts', 'pants', 'tracks', 'shorts']
    return render_template('products.html', products=items, categories=categories, active=cat_name)

# ─── Add to Cart ───────────────────────────────────────────────────────────────
@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not is_logged_in():
        flash('Please login to add items to cart.', 'error')
        return redirect(url_for('login'))

    username = session['username']
    existing = cart_col.find_one({'username': username, 'product_id': product_id})

    if existing:
        # Increase quantity if already in cart
        cart_col.update_one(
            {'username': username, 'product_id': product_id},
            {'$inc': {'quantity': 1}}
        )
    else:
        product = products_col.find_one({'_id': ObjectId(product_id)})
        if product:
            cart_col.insert_one({
                'username': username,
                'product_id': product_id,
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': 1
            })

    flash('Item added to cart!', 'success')
    return redirect(request.referrer or url_for('products'))

# ─── View Cart ─────────────────────────────────────────────────────────────────
@app.route('/cart')
def cart():
    if not is_logged_in():
        flash('Please login to view your cart.', 'error')
        return redirect(url_for('login'))

    username  = session['username']
    cart_items = list(cart_col.find({'username': username}))
    total = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total=total)

# ─── Remove from Cart ──────────────────────────────────────────────────────────
@app.route('/remove_from_cart/<item_id>')
def remove_from_cart(item_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    cart_col.delete_one({'_id': ObjectId(item_id)})
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))

# ─── Update Cart Quantity ──────────────────────────────────────────────────────
@app.route('/update_cart/<item_id>/<action>')
def update_cart(item_id, action):
    if not is_logged_in():
        return redirect(url_for('login'))

    item = cart_col.find_one({'_id': ObjectId(item_id)})
    if item:
        if action == 'inc':
            cart_col.update_one({'_id': ObjectId(item_id)}, {'$inc': {'quantity': 1}})
        elif action == 'dec':
            if item['quantity'] > 1:
                cart_col.update_one({'_id': ObjectId(item_id)}, {'$inc': {'quantity': -1}})
            else:
                cart_col.delete_one({'_id': ObjectId(item_id)})

    return redirect(url_for('cart'))

# ─── Checkout / Place Order ────────────────────────────────────────────────────
@app.route('/checkout', methods=['POST'])
def checkout():
    if not is_logged_in():
        return redirect(url_for('login'))

    username   = session['username']
    cart_items = list(cart_col.find({'username': username}))

    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('cart'))

    total = sum(item['price'] * item['quantity'] for item in cart_items)

    # Build order items list
    order_items = [{
        'name'    : item['name'],
        'price'   : item['price'],
        'quantity': item['quantity'],
        'image'   : item['image'],
        'subtotal': item['price'] * item['quantity']
    } for item in cart_items]

    # Save order
    orders_col.insert_one({
        'username'  : username,
        'items'     : order_items,
        'total'     : total,
        'date'      : datetime.now(),
        'status'    : 'Order Placed',
        'address'   : request.form.get('address', 'Default Address'),
        'phone'     : request.form.get('phone', ''),
    })

    # Clear cart after order
    cart_col.delete_many({'username': username})

    flash('🎉 Order placed successfully! Thank you for shopping with Maans.', 'success')
    return redirect(url_for('orders'))

# ─── Orders History ────────────────────────────────────────────────────────────
@app.route('/orders')
def orders():
    if not is_logged_in():
        flash('Please login to view your orders.', 'error')
        return redirect(url_for('login'))

    username    = session['username']
    user_orders = list(orders_col.find({'username': username}).sort('date', -1))

    return render_template('orders.html', orders=user_orders)

# ─── Cart Count (for navbar badge) ────────────────────────────────────────────
@app.context_processor
def inject_cart_count():
    count = 0
    if is_logged_in():
        count = cart_col.count_documents({'username': session['username']})
    return {'cart_count': count}

# ─── Run App ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run()

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)