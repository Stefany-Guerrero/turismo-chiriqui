import pymysql
import pymongo
import json
from datetime import datetime, date
from decimal import Decimal

MARIADB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin2026',
    'database': 'turismo_chiriqui',
    'port': 3306
}

MONGO_URI = 'mongodb://localhost:27017'
MONGO_DB = 'turismo_chiriqui'

def default_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    return str(obj)

def sync():
    mariadb = pymysql.connect(**MARIADB_CONFIG)
    mongo = pymongo.MongoClient(MONGO_URI)
    mdb = mongo[MONGO_DB]

    cur = mariadb.cursor()
    cur.execute('SHOW TABLES')
    tables = [r[0] for r in cur.fetchall()]

    for table in tables:
        cur.execute(f'SELECT * FROM `{table}`')
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

        documents = []
        for row in rows:
            doc = {}
            for col, val in zip(columns, row):
                if val is not None:
                    doc[col] = json.loads(json.dumps(val, default=default_serializer))
                else:
                    doc[col] = None
            documents.append(doc)

        collection = mdb[table]
        collection.drop()
        if documents:
            collection.insert_many(documents)

        print(f'{table}: {len(documents)} documentos sincronizados')

    mariadb.close()
    print(f'\nSincronizacion completada: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

if __name__ == '__main__':
    sync()
