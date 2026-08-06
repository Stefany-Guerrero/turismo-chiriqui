import pymysql, pymongo, socket

hostname = socket.gethostname().lower()
if hostname in ('kali', 'kali-linux', 'kali.lan'):
    mysql_conn = pymysql.connect(host='192.168.56.1', user='root', password='admin2026', database='turismo_chiriqui', charset='utf8mb4')
    mongo = pymongo.MongoClient('mongodb://192.168.56.1:27017')['turismo_chiriqui']
else:
    mysql_conn = pymysql.connect(host='localhost', user='root', password='admin2026', database='turismo_chiriqui', charset='utf8mb4')
    mongo = pymongo.MongoClient('mongodb://localhost:27017')['turismo_chiriqui']

cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)
cursor.execute('SELECT * FROM reservas')
rows = cursor.fetchall()

for row in rows:
    for k, v in row.items():
        if hasattr(v, 'isoformat'):
            row[k] = v.isoformat()
        elif isinstance(v, bytes):
            row[k] = v.decode('utf-8', errors='replace')
    mongo.reservas.update_one({'id': row['id']}, {'$set': row}, upsert=True)

print(f'Sincronizadas {len(rows)} reservas a MongoDB')
cursor.close()
mysql_conn.close()
