"""
Predefined Database Queries
===========================

This module contains predefined SQL queries for the mock e-commerce system.
"""

def get_top_spenders(limit: int = 5) -> str:
    """Get users who spent the most money."""
    return f"""
    SELECT u.name, u.email, u.total_spent 
    FROM users u 
    ORDER BY u.total_spent DESC 
    LIMIT {limit}
    """

def get_user_purchases(user_name: str) -> str:
    """Get all products purchased by a specific user."""
    return f"""
    SELECT p.name, p.category, p.price, o.quantity, o.total_price, o.order_date
    FROM orders o
    JOIN products p ON o.product_id = p.id
    JOIN users u ON o.user_id = u.id
    WHERE u.name LIKE '%{user_name}%'
    ORDER BY o.order_date DESC
    """

def get_products_by_category(category: str) -> str:
    """Get all products in a specific category."""
    return f"""
    SELECT name, price, stock, category
    FROM products 
    WHERE category LIKE '%{category}%'
    ORDER BY price DESC
    """

def get_expensive_products(limit: int = 10) -> str:
    """Get the most expensive products."""
    return f"""
    SELECT name, price, category, stock
    FROM products 
    ORDER BY price DESC 
    LIMIT {limit}
    """

def get_low_stock_products(threshold: int = 50) -> str:
    """Get products with low stock."""
    return f"""
    SELECT name, price, category, stock
    FROM products 
    WHERE stock < {threshold}
    ORDER BY stock ASC
    """

def get_user_stats() -> str:
    """Get general user statistics."""
    return """
    SELECT 
        COUNT(*) as total_users,
        AVG(total_spent) as avg_spent,
        MAX(total_spent) as max_spent,
        MIN(total_spent) as min_spent
    FROM users
    """

def get_product_stats() -> str:
    """Get general product statistics."""
    return """
    SELECT 
        COUNT(*) as total_products,
        COUNT(DISTINCT category) as total_categories,
        AVG(price) as avg_price,
        MAX(price) as max_price,
        MIN(price) as min_price
    FROM products
    """

def get_recent_orders(limit: int = 10) -> str:
    """Get recent orders with user and product details."""
    return f"""
    SELECT 
        u.name as user_name,
        p.name as product_name,
        o.quantity,
        o.total_price,
        o.order_date
    FROM orders o
    JOIN users u ON o.user_id = u.id
    JOIN products p ON o.product_id = p.id
    ORDER BY o.order_date DESC
    LIMIT {limit}
    """

def get_category_sales() -> str:
    """Get sales by category."""
    return """
    SELECT 
        p.category,
        COUNT(o.id) as total_orders,
        SUM(o.total_price) as total_sales,
        AVG(o.total_price) as avg_order_value
    FROM orders o
    JOIN products p ON o.product_id = p.id
    GROUP BY p.category
    ORDER BY total_sales DESC
    """
