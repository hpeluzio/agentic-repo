"""
Database Models for Mock E-commerce System
==========================================

This module defines the database schema for users, products, and orders.
"""

import sqlite3
from typing import List, Dict, Any

def create_database():
    """Create the database and tables with mock data."""
    conn = sqlite3.connect('mock_ecommerce.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            total_spent REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Insert mock data
    insert_mock_data(cursor)
    
    conn.commit()
    conn.close()

def insert_mock_data(cursor):
    """Insert mock data into the database."""
    
    # Mock users
    users = [
        ('João Silva', 'joao@email.com', 1250.50),
        ('Maria Santos', 'maria@email.com', 890.75),
        ('Pedro Costa', 'pedro@email.com', 2100.00),
        ('Ana Oliveira', 'ana@email.com', 675.25),
        ('Carlos Lima', 'carlos@email.com', 1850.80),
        ('Lucia Ferreira', 'lucia@email.com', 3200.15),
        ('Roberto Alves', 'roberto@email.com', 950.40),
        ('Fernanda Rocha', 'fernanda@email.com', 1450.90)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO users (name, email, total_spent) 
        VALUES (?, ?, ?)
    ''', users)
    
    # Mock products
    products = [
        ('iPhone 15', 999.99, 'Electronics', 50),
        ('MacBook Pro', 2499.99, 'Electronics', 25),
        ('Samsung Galaxy S24', 899.99, 'Electronics', 40),
        ('Nike Air Max', 199.99, 'Shoes', 100),
        ('Adidas Ultraboost', 179.99, 'Shoes', 80),
        ('Levi\'s Jeans', 89.99, 'Clothing', 150),
        ('Zara T-Shirt', 29.99, 'Clothing', 200),
        ('Ray-Ban Sunglasses', 159.99, 'Accessories', 60),
        ('Apple Watch', 399.99, 'Electronics', 75),
        ('Sony Headphones', 299.99, 'Electronics', 90)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO products (name, price, category, stock) 
        VALUES (?, ?, ?, ?)
    ''', products)
    
    # Mock orders
    orders = [
        (1, 1, 1, 999.99),  # João bought iPhone
        (1, 4, 2, 399.98),  # João bought 2 Nike
        (2, 3, 1, 899.99),  # Maria bought Samsung
        (2, 6, 3, 269.97),  # Maria bought 3 Jeans
        (3, 2, 1, 2499.99), # Pedro bought MacBook
        (3, 9, 1, 399.99),  # Pedro bought Apple Watch
        (4, 5, 2, 359.98),  # Ana bought 2 Adidas
        (4, 7, 5, 149.95),  # Ana bought 5 T-shirts
        (5, 1, 1, 999.99),  # Carlos bought iPhone
        (5, 8, 1, 159.99),  # Carlos bought Ray-Ban
        (6, 2, 1, 2499.99), # Lucia bought MacBook
        (6, 1, 1, 999.99),  # Lucia bought iPhone
        (6, 10, 1, 299.99), # Lucia bought Sony Headphones
        (7, 3, 1, 899.99),  # Roberto bought Samsung
        (7, 4, 1, 199.99),  # Roberto bought Nike
        (8, 9, 1, 399.99),  # Fernanda bought Apple Watch
        (8, 5, 3, 539.97),  # Fernanda bought 3 Adidas
        (8, 6, 2, 179.98)   # Fernanda bought 2 Jeans
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO orders (user_id, product_id, quantity, total_price, order_date) 
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', orders)

def get_connection():
    """Get a database connection."""
    return sqlite3.connect('mock_ecommerce.db')
