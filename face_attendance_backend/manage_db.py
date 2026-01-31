import pymysql

# --- MYSQL CONFIGURATION ---
# ⚠️ UPDATE THESE WITH YOUR ACTUAL MYSQL DETAILS
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "your_password"  # <--- Change this to your MySQL Root Password
DB_NAME = "face_attendance"

def connect_db():
    """Connects to the MySQL database."""
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)

def run_query(query, params=()):
    """Executes a SQL query and returns results if it's a SELECT."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith("SELECT"):
            # Fetch headers and data
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            conn.close()
            return columns, results
        else:
            # Commit changes for INSERT/DELETE
            conn.commit()
            conn.close()
            print("Action executed successfully.")
            return None, None
    except Exception as e:
        print(f"Database Error: {e}")
        return None, None

def view_users():
    print("\n--- REGISTERED USERS ---")
    # We select specific columns to avoid printing the massive binary face_encoding
    query = "SELECT id, name, email, created_at FROM users"
    cols, data = run_query(query)
    
    if data:
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Joined At'}")
        print("-" * 75)
        for row in data:
            # Convert Created_At to string for cleaner printing
            created_at = str(row[3])
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {created_at}")
    else:
        print("No users found.")
    print("\n")

def view_attendance():
    print("\n--- ATTENDANCE LOGS ---")
    # JOIN query to show Name instead of just User ID
    query = """
    SELECT attendance.id, users.name, attendance.date, attendance.timestamp 
    FROM attendance 
    JOIN users ON users.id = attendance.user_id
    ORDER BY attendance.timestamp DESC
    """
    cols, data = run_query(query)
    
    if data:
        print(f"{'Log ID':<8} {'Name':<20} {'Date':<12} {'Exact Time'}")
        print("-" * 65)
        for row in data:
            timestamp = str(row[3])
            print(f"{row[0]:<8} {row[1]:<20} {row[2]:<12} {timestamp}")
    else:
        print("No attendance records found.")
    print("\n")

def delete_user():
    print("\n--- DELETE USER ---")
    try:
        user_id = input("Enter the ID of the user to delete: ")
        # Warning: This deletes the user AND their attendance logs (due to CASCADE)
        query = "DELETE FROM users WHERE id = %s"
        run_query(query, (user_id,))
    except Exception as e:
        print(f"Error: {e}")

def main():
    while True:
        print("==============================")
        print("   MYSQL DATABASE MANAGER     ")
        print("==============================")
        print("1. View All Users")
        print("2. View Attendance Logs")
        print("3. Delete a User")
        print("4. Exit")
        
        choice = input("\nChoose an option (1-4): ")

        if choice == '1':
            view_users()
        elif choice == '2':
            view_attendance()
        elif choice == '3':
            delete_user()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()