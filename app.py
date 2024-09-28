from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Khóa bí mật để sử dụng session

# Hàm kết nối cơ sở dữ liệu
def get_db_connection():
    conn = sqlite3.connect('store.db')
    conn.row_factory = sqlite3.Row
    return conn


# Khởi tạo cơ sở dữ liệu
def initialize_db():
    conn = get_db_connection()
    with conn:
        # Tạo bảng mới nếu chưa tồn tại
        conn.execute('''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            );''')
        
        # Tạo bảng khách hàng và hóa đơn
        conn.execute('''CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL
            );''')
        conn.execute('''CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                total_price REAL NOT NULL,
                date TEXT NOT NULL
            );''')
    conn.close()

# Trang chủ
@app.route('/')
def index():
    return render_template('index.html')

# Quản lý sản phẩm (hiển thị và thêm sản phẩm)
@app.route('/products', methods=['GET', 'POST'])
def products():
    conn = get_db_connection()
    
    # Tìm kiếm sản phẩm
    search_query = request.args.get('search')
    if search_query:
        products = conn.execute('SELECT * FROM products WHERE name LIKE ?',
                                ('%' + search_query + '%',)).fetchall()
    else:
        products = conn.execute('SELECT * FROM products').fetchall()

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']
        conn.execute('INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)',
                     (name, category, price, quantity))
        conn.commit()
        flash('Sản phẩm đã được thêm thành công!')
        return redirect(url_for('products'))

    conn.close()
    return render_template('products.html', products=products)


# Chỉnh sửa sản phẩm
@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']
        conn.execute('UPDATE products SET name = ?, category = ?, price = ?, quantity = ? WHERE id = ?',
                     (name, category, price, quantity, id))
        conn.commit()
        flash('Sản phẩm đã được cập nhật thành công!')
        return redirect(url_for('products'))

    conn.close()
    return render_template('edit_product.html', product=product)

# Xóa sản phẩm
@app.route('/products/delete/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    flash('Sản phẩm đã được xóa thành công!')
    return redirect(url_for('products'))

# Quản lý khách hàng (hiển thị và thêm khách hàng)
@app.route('/customers', methods=['GET', 'POST'])
def customers():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        conn.execute('INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)',
                     (name, phone, address))
        conn.commit()
        flash('Khách hàng đã được thêm thành công!')
        return redirect(url_for('customers'))

    customers = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

# Chỉnh sửa khách hàng
@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    conn = get_db_connection()
    customer = conn.execute('SELECT * FROM customers WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        conn.execute('UPDATE customers SET name = ?, phone = ?, address = ? WHERE id = ?',
                     (name, phone, address, id))
        conn.commit()
        flash('Khách hàng đã được cập nhật thành công!')
        return redirect(url_for('customers'))

    conn.close()
    return render_template('edit_customer.html', customer=customer)

# Xóa khách hàng
@app.route('/customers/delete/<int:id>')
def delete_customer(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM customers WHERE id = ?', (id,))
    conn.commit()
    flash('Khách hàng đã được xóa thành công!')
    return redirect(url_for('customers'))

# Quản lý hóa đơn (hiển thị và thêm hóa đơn)
@app.route('/invoices', methods=['GET', 'POST'])
def invoices():
    conn = get_db_connection()
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        total_price = request.form['total_price']
        conn.execute('INSERT INTO invoices (customer_name, total_price, date) VALUES (?, ?, date("now"))',
                     (customer_name, total_price))
        conn.commit()
        flash('Hóa đơn đã được tạo thành công!')
        return redirect(url_for('invoices'))

    invoices = conn.execute('SELECT * FROM invoices').fetchall()
    conn.close()
    return render_template('invoices.html', invoices=invoices)

# Xóa hóa đơn
@app.route('/invoices/delete/<int:id>', methods=['POST'])
def delete_invoice(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM invoices WHERE id = ?', (id,))
    conn.commit()
    flash('Hóa đơn đã được xóa thành công!')
    return redirect(url_for('invoices'))

# Báo cáo (hiển thị báo cáo)
@app.route('/report')
def report():
    return render_template('report.html')

# Giỏ hàng
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    # Tạo giỏ hàng trong session nếu chưa có
    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])  # Lấy số lượng sản phẩm

        # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
        cart = session['cart']
        found = False
        for item in cart:
            if item['product_id'] == product_id:
                item['quantity'] += quantity  # Cộng dồn số lượng nếu đã có
                found = True
                break
        if not found:
            cart.append({'product_id': product_id, 'quantity': quantity})  # Thêm sản phẩm vào giỏ

        session['cart'] = cart  # Cập nhật lại session
        session.modified = True
        flash('Sản phẩm đã được thêm vào giỏ hàng!')
        return redirect(url_for('cart'))

    # Lấy thông tin sản phẩm từ cơ sở dữ liệu dựa trên ID trong giỏ hàng
    conn = get_db_connection()
    product_ids = [item['product_id'] for item in session['cart']]
    if product_ids:
        placeholders = ','.join('?' * len(product_ids))
        products = conn.execute(f'SELECT * FROM products WHERE id IN ({placeholders})', product_ids).fetchall()
    else:
        products = []
    
    # Tính tổng tiền giỏ hàng
    total_price = 0
    for product in products:
        for item in session['cart']:
            if item['product_id'] == str(product['id']):
                total_price += product['price'] * item['quantity']

    conn.close()
    return render_template('cart.html', products=products, total_price=total_price)

@app.route('/upload_image/<int:id>', methods=['POST'])
def upload_image(id):
    if 'image' not in request.files:
        flash('Không có tệp hình ảnh nào được chọn.')
        return redirect(url_for('products'))

    file = request.files['image']
    if file.filename == '':
        flash('Không có tệp hình ảnh nào được chọn.')
        return redirect(url_for('products'))

    if file and file.filename.endswith('.jpg'):
        # Đường dẫn đến thư mục lưu ảnh
        image_path = f'static/images/{id}.jpg'

        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        # Lưu tệp hình ảnh vào thư mục static/images
        file.save(image_path)
        flash('Hình ảnh đã được thay đổi thành công!')
    else:
        flash('Vui lòng chọn tệp hình ảnh có định dạng .jpg.')

    return redirect(url_for('products'))

if __name__ == '__main__':
    initialize_db()  # Khởi tạo cơ sở dữ liệu khi chạy ứng dụng
    app.run(host='0.0.0.0', port=5000, debug=True)
