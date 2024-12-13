from db_components import *
from os import getenv






def post_content(nickname,content):



    hostname = getenv('DB_HOSTNAME')
    database = getenv('DB_NAME')
    username = getenv('DB_USERNAME')
    password = getenv('DB_PASSWORD')
    port=3307

    connection = connect_to_db(hostname,username,password,database,port)


    insert_post_data(connection,nickname,content)


    close_conn(connection)
