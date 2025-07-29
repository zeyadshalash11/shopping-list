from db import create_connection

def test_db_connection():
    conn = create_connection()
    if conn:
        print(" Test passed: You are connected!")
        conn.close()
    else:
        print(" Test failed: Could not connect.")

if __name__ == "__main__":
    test_db_connection()
