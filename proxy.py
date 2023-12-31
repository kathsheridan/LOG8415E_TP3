import sys
import pymysql
from sshtunnel import SSHTunnelForwarder

IPs = {
    'master': 'ip-172-31-17-1.ec2.internal',
    'slave1': 'ip-172-31-17-2.ec2.internal',
    'slave2': 'ip-172-31-17-3.ec2.internal',
    'slave3': 'ip-172-31-17-4.ec2.internal'
}

def execute_queries(ip, name, query):
    with SSHTunnelForwarder(IPs[name], ssh_username="ubuntu", ssh_pkey="tp3key.pem", local_bind_address=('127.0.0.1', 3306), remote_bind_address=('127.0.0.1', 3306)) as tunnel:
        tunnel.start()
        connection = pymysql.connect(host=ip, user='root', password="ClusterPassword", db='sakila', port=3306, autocommit=True)
        cursor = connection.cursor()
        cursor.execute(query)
        for line in cursor:
            print(line)
        connection.close()
        tunnel.close()

def direct_hit(query):
    print("DIRECT HIT - connecting...")
    execute_queries('127.0.0.1', 'master', query)

def main():
    if len(sys.argv) < 2:
        print('ERROR! Make sure the command has the query, like this => python3 proxy.py "SQL QUERY"')
    else:
        SQL_query = sys.argv[1]
        direct_hit(SQL_query)

    print("=====================================================================================================================")

if __name__ == "__main__":
    main()
