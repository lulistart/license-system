CREATE DATABASE IF NOT EXISTS license_system;
USE license_system;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE licenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_key VARCHAR(50) UNIQUE NOT NULL,
    user_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    expire_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    max_machines INT DEFAULT 1,
    activation_count INT DEFAULT 0,
    last_used DATETIME,
    batch_id VARCHAR(50),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE machine_bindings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_id INT,
    machine_code VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (license_id) REFERENCES licenses(id)
);

CREATE TABLE usage_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_id INT,
    machine_code VARCHAR(100),
    action VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (license_id) REFERENCES licenses(id)
);

-- 创建默认管理员账户，密码为 admin123
INSERT INTO users (username, password) 
VALUES ('admin', SHA2('admin123', 256)); 