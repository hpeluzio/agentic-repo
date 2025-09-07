"""
Database Service
===============

This service handles all database operations and business logic.
It acts as a layer between the tools and the database.
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from database.models import get_connection, create_database
from database.queries import (
    get_top_spenders, get_user_purchases, get_products_by_category,
    get_expensive_products, get_low_stock_products, get_user_stats,
    get_product_stats, get_recent_orders, get_category_sales
)

# Configure logging for database operations
logger = logging.getLogger(__name__)

class DatabaseService:
    """Service class for database operations."""
    
    def __init__(self):
        """Initialize the database service."""
        create_database()
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a raw SQL query.
        
        Args:
            query: SQL SELECT query to execute
            
        Returns:
            Dictionary with results and metadata
        """
        start_time = datetime.now()
        logger.info(f"🔍 Executing SQL query: {query}")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            conn.close()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Query executed successfully in {execution_time:.3f}s - {len(results)} rows returned")
            
            formatted_results = []
            for row in results:
                row_dict = dict(zip(columns, row))
                formatted_results.append(row_dict)
            
            return {
                "success": True,
                "data": formatted_results,
                "count": len(results),
                "columns": columns,
                "query": query,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Query failed after {execution_time:.3f}s: {str(e)}")
            logger.error(f"Failed query: {query}")
            
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "count": 0,
                "query": query,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
    
    def get_top_customers(self, limit: int = 5) -> Dict[str, Any]:
        """
        Get top spending customers.
        
        Args:
            limit: Number of customers to return
            
        Returns:
            Dictionary with top customers data
        """
        start_time = datetime.now()
        query = get_top_spenders(limit)
        logger.info(f"🔍 Getting top {limit} customers")
        logger.info(f"SQL: {query}")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            conn.close()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Top customers query executed in {execution_time:.3f}s - {len(results)} customers found")
            
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "name": row[0],
                    "email": row[1],
                    "total_spent": float(row[2]),
                    "formatted_spent": f"${row[2]:.2f}"
                })
            
            return {
                "success": True,
                "data": formatted_results,
                "count": len(results),
                "message": f"Top {limit} customers by spending",
                "query": query,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Top customers query failed after {execution_time:.3f}s: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "count": 0,
                "query": query,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
    
    def get_customer_purchases(self, customer_name: str) -> Dict[str, Any]:
        """
        Get purchases by a specific customer.
        
        Args:
            customer_name: Name of the customer
            
        Returns:
            Dictionary with customer purchases
        """
        start_time = datetime.now()
        query = get_user_purchases(customer_name)
        logger.info(f"🔍 Getting purchases for customer: {customer_name}")
        logger.info(f"SQL: {query}")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            conn.close()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if not results:
                logger.info(f"✅ Customer purchases query executed in {execution_time:.3f}s - No purchases found")
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "message": f"No purchases found for customer: {customer_name}",
                    "query": query,
                    "execution_time": execution_time,
                    "timestamp": start_time.isoformat()
                }
            
            logger.info(f"✅ Customer purchases query executed in {execution_time:.3f}s - {len(results)} purchases found")
            
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "product": row[0],
                    "category": row[1],
                    "price": float(row[2]),
                    "quantity": row[3],
                    "total": float(row[4]),
                    "date": row[5],
                    "formatted_price": f"${row[2]:.2f}",
                    "formatted_total": f"${row[4]:.2f}"
                })
            
            return {
                "success": True,
                "data": formatted_results,
                "count": len(results),
                "message": f"Purchases by {customer_name}",
                "query": query,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Customer purchases query failed after {execution_time:.3f}s: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "count": 0,
                "query": query,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
    
    def get_products_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get products by category.
        
        Args:
            category: Product category
            
        Returns:
            Dictionary with products in category
        """
        start_time = datetime.now()
        query = get_products_by_category(category)
        logger.info(f"🔍 Getting products in category: {category}")
        logger.info(f"SQL: {query}")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            conn.close()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if not results:
                logger.info(f"✅ Products by category query executed in {execution_time:.3f}s - No products found")
                return {
                    "success": True,
                    "data": [],
                    "count": 0,
                    "message": f"No products found in category: {category}",
                    "query": query,
                    "execution_time": execution_time,
                    "timestamp": start_time.isoformat()
                }
            
            logger.info(f"✅ Products by category query executed in {execution_time:.3f}s - {len(results)} products found")
            
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "name": row[0],
                    "price": float(row[1]),
                    "stock": row[2],
                    "category": row[3],
                    "formatted_price": f"${row[1]:.2f}"
                })
            
            return {
                "success": True,
                "data": formatted_results,
                "count": len(results),
                "message": f"Products in {category} category",
                "query": query,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Products by category query failed after {execution_time:.3f}s: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "count": 0,
                "query": query,
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get general database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        start_time = datetime.now()
        logger.info("🔍 Getting database statistics")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # User stats
            user_query = get_user_stats()
            logger.info(f"SQL (user stats): {user_query}")
            cursor.execute(user_query)
            user_stats = cursor.fetchone()
            
            # Product stats
            product_query = get_product_stats()
            logger.info(f"SQL (product stats): {product_query}")
            cursor.execute(product_query)
            product_stats = cursor.fetchone()
            
            # Category sales
            category_query = get_category_sales()
            logger.info(f"SQL (category sales): {category_query}")
            cursor.execute(category_query)
            category_sales = cursor.fetchall()
            
            conn.close()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Database stats query executed in {execution_time:.3f}s")
            
            stats = {
                "users": {
                    "total": user_stats[0],
                    "avg_spent": float(user_stats[1]),
                    "max_spent": float(user_stats[2]),
                    "min_spent": float(user_stats[3]),
                    "formatted_avg": f"${user_stats[1]:.2f}",
                    "formatted_max": f"${user_stats[2]:.2f}",
                    "formatted_min": f"${user_stats[3]:.2f}"
                },
                "products": {
                    "total": product_stats[0],
                    "categories": product_stats[1],
                    "avg_price": float(product_stats[2]),
                    "max_price": float(product_stats[3]),
                    "min_price": float(product_stats[4]),
                    "formatted_avg": f"${product_stats[2]:.2f}",
                    "formatted_max": f"${product_stats[3]:.2f}",
                    "formatted_min": f"${product_stats[4]:.2f}"
                },
                "category_sales": []
            }
            
            for row in category_sales:
                stats["category_sales"].append({
                    "category": row[0],
                    "orders": row[1],
                    "total_sales": float(row[2]),
                    "avg_order": float(row[3]),
                    "formatted_sales": f"${row[2]:.2f}",
                    "formatted_avg": f"${row[3]:.2f}"
                })
            
            return {
                "success": True,
                "data": stats,
                "message": "Database statistics",
                "queries": {
                    "user_stats": user_query,
                    "product_stats": product_query,
                    "category_sales": category_query
                },
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Database stats query failed after {execution_time:.3f}s: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "data": {},
                "message": "Error getting database statistics",
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            }

# Global service instance
database_service = DatabaseService()
