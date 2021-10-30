# Create MySql Connection
import pymysql

class mysql_connect:
	conn = pymysql.connect(host="127.0.0.1",user='root',password='password',db='airflow',cursorclass=pymysql.cursors.DictCursor)
