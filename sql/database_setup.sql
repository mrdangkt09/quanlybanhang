-- Tạo bảng products
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
);

-- Chèn dữ liệu mẫu
INSERT INTO products (name, category, price, quantity) VALUES ('Sản phẩm A', 'Danh mục 1', 100.00, 10);
INSERT INTO products (name, category, price, quantity) VALUES ('Sản phẩm B', 'Danh mục 2', 200.00, 5);
