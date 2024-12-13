import mysql.connector
from mysql.connector import Error

def connect_to_db(host,user,password,database,port):
    """Establishes a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            database=database,
            port=port,
            password=password
        )
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


def insert_post_data(connection, nickname, content):
    query = f"INSERT INTO `conaobiad_gradedoubt`.`posts` (`nickPost`, `contentPost`, `likesPost`, `dislikesPost`) VALUES ('{nickname}', '{content}', 0, 0);"
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    print(f"Inserted: {cursor.rowcount} row(s)")


def fetch_data(connection):
    """Fetches and displays data from the table."""
    query = "SELECT * FROM sample_table"
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    print("Data fetched from database:")
    for row in rows:
        print(row)

def update_data(connection, user_id, new_age):
    query = "UPDATE posts SET age = %s WHERE id = %s"
    cursor = connection.cursor()
    cursor.execute(query, (new_age, user_id))
    connection.commit()
    print(f"Updated: {cursor.rowcount} row(s)")




def delete_data(connection, user_id):
    """Deletes a row from the table."""
    query = "DELETE FROM sample_table WHERE id = %s"
    cursor = connection.cursor()
    cursor.execute(query, (user_id,))
    connection.commit()

    print(f"Deleted: {cursor.rowcount} row(s)")



def close_conn(connection):
    connection.close()




def main():
    connection = connect_to_db()
    if connection:

        fetch_data(connection)


        update_data(connection, user_id=1, new_age=26)
        fetch_data(connection)


        delete_data(connection, user_id=2)
        fetch_data(connection)


        connection.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
