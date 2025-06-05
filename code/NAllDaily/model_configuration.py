
import pypyodbc

sql_server = "192.168.1.111"
sql_database = "FinanceData"
sql_uid = "sa"
sql_pwd = "Quant6688"
try:
    channel = pypyodbc.connect("DRIVER={SQL Server};SERVER=" + sql_server + ";DATABASE=" + sql_database + ";UID=" + sql_uid + ";PWD=" + sql_pwd).cursor()
except:
    sql_server = "SERVER"
    channel = pypyodbc.connect("DRIVER={SQL Server};SERVER=" + sql_server + ";DATABASE=" + sql_database + ";UID=" + sql_uid + ";PWD=" + sql_pwd).cursor()
con = pypyodbc.connect("DRIVER={SQL Server};SERVER=" + sql_server + ";DATABASE=" + sql_database + ";UID=" + sql_uid + ";PWD=" + sql_pwd)
