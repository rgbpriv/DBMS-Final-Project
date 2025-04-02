DROP TABLE IF EXISTS menu_items;
CREATE TABLE menu_items (
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  description TEXT,
  price DECIMAL(5,2),
  category VARCHAR(50),
  availability TINYINT(1)
);

INSERT INTO menu_items (item_id, name, description, price, category, availability) VALUES
(1,'Margherita Pizza','Classic cheese and tomato pizza.',10.00,'Pizza',1),
(2,'Cheeseburger','Beef patty with cheese in a bun.',8.00,'Burger',1),
(3,'Caesar Salad','Fresh romaine with Caesar dressing.',7.00,'Salad',1);

DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  total_price DECIMAL(6,2),
  status VARCHAR(20) DEFAULT 'Pending'
);

INSERT INTO orders (order_id, order_date, total_price, status) VALUES
(1,'2025-04-01 19:30:48',26.00,'Completed'),
(2,'2025-04-01 19:33:44',18.00,'Preparing'),
(3,'2025-04-01 20:22:34',25.00,'Pending'),
(4,'2025-04-01 20:24:07',25.00,'Pending'),
(5,'2025-04-01 20:24:31',15.00,'Completed'),
(6,'2025-04-01 20:25:31',15.00,'Completed');

DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (
  order_item_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  item_id INT,
  quantity INT,
  subtotal DECIMAL(6,2),
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

INSERT INTO order_items (order_item_id, order_id, item_id, quantity, subtotal) VALUES
(1,1,1,1,10.00),
(2,1,2,2,16.00),
(3,2,1,1,10.00),
(4,2,2,1,8.00),
(5,3,1,1,10.00),
(6,3,2,1,8.00),
(7,3,3,1,7.00),
(8,4,1,1,10.00),
(9,4,2,1,8.00),
(10,4,3,1,7.00),
(11,5,2,1,8.00),
(12,5,3,1,7.00),
(13,6,2,1,8.00),
(14,6,3,1,7.00);

DROP TABLE IF EXISTS restaurant_staff;
CREATE TABLE restaurant_staff (
  staff_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  username VARCHAR(50) UNIQUE,
  password VARCHAR(100),
  role VARCHAR(50)
);

INSERT INTO restaurant_staff (staff_id, name, username, password, role) VALUES
(2,'Alice Manager','alice','$2b$12$vMXmkKnOGFxG89UEiaeVFOfGrl3PmpLT5f9cT6ofAAlGLHFHq2CC2','Manager'),
(3,'bob','bob','$2b$12$2.mUor2NbCDjFRbFSwjicO4sdawz0lvfMD.SSvimUAYbHyw/vFHTW','Waiter'),
(4,'Ragib','rgbehsan','$2b$12$QcttVOa8QpbohY/P4uA4deO1baygQEw.LVPpOjBHC75x45DgjSkXm','Manager'),
(5,'Aysha','aysha','$2b$12$iRWvkMEtb2uN42A2.kYFQeG9fObVfVJvNNJyYzUZxn4Fe8nYNvy1S','Manager');

DROP TABLE IF EXISTS staff_shifts;
CREATE TABLE staff_shifts (
  shift_id INT AUTO_INCREMENT PRIMARY KEY,
  staff_id INT,
  shift_date DATE,
  start_time TIME,
  end_time TIME,
  FOREIGN KEY (staff_id) REFERENCES restaurant_staff(staff_id)
);
