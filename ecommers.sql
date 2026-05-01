create database ecommerce_db;
use ecommerce_db;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    condition_type ENUM('New','Used','Refurbished') DEFAULT 'New',
    discount DECIMAL(5,2) DEFAULT 0.00,
    best_seller BOOLEAN DEFAULT FALSE,
    image VARCHAR(255),
    rating DECIMAL(3,2) DEFAULT 0.0,
    category VARCHAR(100),
    return_policy TEXT,
    brand VARCHAR(100),
    status ENUM('active','out_of_stock','discontinued') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


INSERT INTO products 
(name, description, price, quantity, condition_type, discount, best_seller, image, rating, category, return_policy, brand, status)
VALUES

-- 📱 Electronics
('Samsung Galaxy S23', 
 'Latest Samsung flagship smartphone with AMOLED display and powerful processor',
 74999.00, 25, 'New', 10.00, TRUE, 'samsung_s23.jpg', 4.6, 'Mobiles',
 '7 days replacement policy', 'Samsung', 'active'),

('Apple iPhone 14', 
 'Apple iPhone with A15 Bionic chip and advanced camera system',
 69999.00, 15, 'New', 5.00, TRUE, 'iphone14.jpg', 4.7, 'Mobiles',
 '7 days replacement policy', 'Apple', 'active'),

-- 💻 Laptops
('HP Pavilion Laptop', 
 'HP Pavilion 15.6-inch laptop with Intel i5 processor',
 58999.00, 10, 'New', 12.00, FALSE, 'hp_pavilion.jpg', 4.4, 'Laptops',
 '10 days replacement policy', 'HP', 'active'),

('Dell Inspiron 3511', 
 'Dell Inspiron laptop suitable for office and student use',
 52999.00, 8, 'New', 15.00, FALSE, 'dell_inspiron.jpg', 4.3, 'Laptops',
 '10 days replacement policy', 'Dell', 'active'),

-- 👕 Fashion
('Men Cotton Casual Shirt', 
 'Comfortable cotton casual shirt for daily wear',
 1499.00, 50, 'New', 30.00, TRUE, 'mens_shirt.jpg', 4.1, 'Fashion',
 '5 days return policy', 'Roadster', 'active'),

('Women Kurti Set', 
 'Stylish ethnic kurti set for women',
 2499.00, 40, 'New', 25.00, FALSE, 'women_kurti.jpg', 4.2, 'Fashion',
 '5 days return policy', 'Biba', 'active'),

-- 🏠 Home & Kitchen
('Prestige Induction Cooktop', 
 'Energy efficient induction cooktop with multiple cooking modes',
 3199.00, 20, 'New', 18.00, TRUE, 'prestige_induction.jpg', 4.5, 'Home Appliances',
 '7 days replacement policy', 'Prestige', 'active'),

('Milton Water Bottle 1L', 
 'Stainless steel insulated water bottle',
 899.00, 100, 'New', 20.00, FALSE, 'milton_bottle.jpg', 4.0, 'Home & Kitchen',
 'No return available', 'Milton', 'active'),

-- 🎧 Accessories
('Boat Rockerz Headphones', 
 'Wireless Bluetooth headphones with deep bass',
 1999.00, 35, 'New', 35.00, TRUE, 'boat_headphones.jpg', 4.4, 'Accessories',
 '7 days replacement policy', 'boAt', 'active'),

('Logitech Wireless Mouse', 
 'Ergonomic wireless mouse for laptops and desktops',
 1299.00, 60, 'New', 22.00, FALSE, 'logitech_mouse.jpg', 4.3, 'Accessories',
 '10 days replacement policy', 'Logitech', 'active'),

-- 📺 Appliances
('LG 43-inch Smart TV', 
 'Full HD Smart LED TV with webOS',
 32999.00, 5, 'New', 20.00, TRUE, 'lg_tv.jpg', 4.6, 'Televisions',
 '10 days replacement policy', 'LG', 'active'),

('Whirlpool Washing Machine', 
 'Top load washing machine with smart wash technology',
 18999.00, 3, 'New', 18.00, FALSE, 'whirlpool_wm.jpg', 4.2, 'Appliances',
 '10 days replacement policy', 'Whirlpool', 'out_of_stock');

select * from products;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phonenumber VARCHAR(15),
    gender ENUM('Male', 'Female', 'Other'),
    address TEXT NULL,
	city VARCHAR(100) NULL,
	state VARCHAR(100) NULL,
	pincode VARCHAR(10) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM ecommerce_db.users;

truncate users;
