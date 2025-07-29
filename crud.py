import sqlite3
from db import create_connection
from sqlite3 import Error

def get_users():
    conn = create_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    finally:
        conn.close()


def create_user(username, email):
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
        conn.commit()
        print(" User created successfully.")
        return True
    except Exception as e:
        print(f" Error creating user: {e}")
        return False
    finally:
        conn.close()



def get_categories():
    conn = create_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories")
        return cursor.fetchall()
    finally:
        conn.close()


def create_category(category_name):
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (category_name,))
        conn.commit()
        print(" Category created successfully.")
        return True
    except Exception as e:
        print(f" Error creating category: {e}")
        return False
    finally:
        conn.close()


def get_items():
    conn = create_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT items.item_id, item_name, unit, category_name
            FROM items
            JOIN categories ON items.category_id = categories.category_id
        """)
        return cursor.fetchall()
    finally:
        conn.close()


def create_item(item_name, category_id, unit):
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (item_name, category_id, unit) VALUES (%s, %s, %s)",
            (item_name, category_id, unit)
        )
        conn.commit()
        print(" Item created successfully.")
        return True
    except Exception as e:
        print(f" Error creating item: {e}")
        return False
    finally:
        conn.close()


def get_user_shopping_lists(user_id):
    conn = create_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM shopping_lists WHERE user_id = %s",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def create_shopping_list(user_id, list_name):
    from datetime import date
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO shopping_lists (user_id, list_name, created_date) VALUES (%s, %s, %s)",
            (user_id, list_name, date.today())
        )
        conn.commit()
        print(" Shopping list created.")
        return True
    except Exception as e:
        print(f" Error creating shopping list: {e}")
        return False
    finally:
        conn.close()

def delete_shopping_list(list_id: int):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shopping_lists WHERE list_id = %s", (list_id,))
            conn.commit()
            print(f"Deleted list_id: {list_id}, rows affected: {cursor.rowcount}")
            return cursor.rowcount > 0
        except Error as e:
            print(f"Delete list error: {e}")
            return False
        finally:
            conn.close()



def get_list_items(list_id):
    conn = create_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT li.list_item_id, i.item_name, c.category_name, i.unit, li.quantity, li.is_purchased
            FROM list_items li
            JOIN items i ON li.item_id = i.item_id
            JOIN categories c ON i.category_id = c.category_id
            WHERE li.list_id = %s
        """, (list_id,))
        return cursor.fetchall()
    finally:
        conn.close()


def add_item_to_list(list_id, item_id, quantity):
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO list_items (list_id, item_id, quantity) VALUES (%s, %s, %s)",
            (list_id, item_id, quantity)
        )
        conn.commit()
        print(" Item added to list.")
        return True
    except Exception as e:
        print(f" Error adding item to list: {e}")
        return False
    finally:
        conn.close()


def update_list_item_quantity(list_item_id, new_quantity):
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE list_items SET quantity = %s WHERE list_item_id = %s",
            (new_quantity, list_item_id)
        )
        conn.commit()
        print(" Quantity updated.")
        return True
    except Exception as e:
        print(f" Error updating quantity: {e}")
        return False
    finally:
        conn.close()


def mark_list_item_purchased(list_item_id, is_purchased: bool):
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE list_items SET is_purchased = %s WHERE list_item_id = %s",
            (is_purchased, list_item_id)
        )
        conn.commit()
        print(" Purchased status updated.")
        return True
    except Exception as e:
        print(f" Error updating purchase status: {e}")
        return False
    finally:
        conn.close()


def delete_list_item(list_item_id):
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM list_items WHERE list_item_id = %s", (list_item_id,))
        conn.commit()
        print(" Item removed from list.")
        return True
    except Exception as e:
        print(f" Error deleting item: {e}")
        return False
    finally:
        conn.close()
        
def delete_user(user_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()

        #  Find all list_ids for this user
        cursor.execute("SELECT list_id FROM shopping_lists WHERE user_id = %s", (user_id,))
        list_ids = [row[0] for row in cursor.fetchall()]

        #  Delete all list_items for those lists
        for list_id in list_ids:
            cursor.execute("DELETE FROM list_items WHERE list_id = %s", (list_id,))

        #  Delete all shopping_lists for this user
        cursor.execute("DELETE FROM shopping_lists WHERE user_id = %s", (user_id,))

        #  Delete the user
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print("Error deleting user:", e)
        return False
    finally:
        conn.close()



