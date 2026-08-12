CREATE DATABASE IF NOT EXISTS isp_subscription_system;
USE isp_subscription_system;
CREATE TABLE packages (  
    package_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    price DECIMAL(10,2) NOT NULL
);
DESCRIBE packages;
INSERT INTO packages(name, description, price)
VALUES
('Home Fibre 10Mbps', 'Unlimited fibre internet for basic home browsing.', 299.99),
('Home Fibre 100Mbps', 'Ultra-fast fibre for heavy internet users.', 899.99),
('Home Fibre 200Mbps', 'Premium fibre package for multiple devices.', 1299.99),
('Business Fibre 50Mbps', 'Reliable business fibre with unlimited data.', 799.99),
('Business Fibre 100Mbps', 'High-performance business internet solution.', 1199.99),
('Business Fibre 500Mbps', 'Enterprise-grade fibre connectivity.', 2499.99),
('LTE Basic 20GB', '20GB monthly LTE data package.', 199.99),
('LTE Standard 50GB', '50GB LTE package for everyday use.', 349.99),
('LTE Unlimited', 'Unlimited LTE internet package.', 799.99),
('APN Starter', 'Secure APN package for small businesses.', 499.99),
('APN Professional', 'Business APN with enhanced connectivity.', 899.99),
('VoIP Home', 'Affordable VoIP package for home users.', 149.99),
('VoIP Business', 'Business VoIP solution with unlimited local calls.', 399.99),
('Gaming Fibre 100Mbps', 'Low-latency fibre package for online gaming.', 999.99),
('Student Fibre 30Mbps', 'Affordable fibre package for students.', 349.99),
('Work From Home Fibre', 'Optimized fibre package for remote workers.', 699.99),
('Unlimited Premium Fibre', 'Top-tier unlimited fibre with maximum speed.', 1599.99);
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100)
);
DESCRIBE customers;
INSERT INTO customers(name, phone, email)
VALUES
('John Snow','0823456789','john@email.com');
CREATE TABLE subscriptions (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    package_id INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    vat DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (package_id)
        REFERENCES packages(package_id)
);
DESCRIBE subscriptions;
INSERT INTO subscriptions
(customer_id, package_id, subtotal, vat, total)
VALUES (1, 1, 399.99, 60.00, 459.99);