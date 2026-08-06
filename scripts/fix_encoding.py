import pymongo

c = pymongo.MongoClient('mongodb://localhost:27017')
db = c['turismo_chiriqui']

fixes = [
    ('ChiriquÃ\xad', 'Chiriquí'),
    ('ChiriquÃ\xad', 'Chiriquí'),
    ('PanamÃ¡', 'Panamá'),
    ('CoclÃ©', 'Coclé'),
    ('AntÃ³n', 'Antón'),
    ('ColÃ³n', 'Colón'),
    ('Ã¡', 'á'),
    ('Ã­', 'í'),
    ('Ã³', 'ó'),
    ('Ã±', 'ñ'),
    ('Ã‰', 'É'),
]

total_fixed = 0
for col_name in db.list_collection_names():
    col = db[col_name]
    for doc in col.find():
        updates = {}
        for key, val in doc.items():
            if isinstance(val, str):
                for bad, good in fixes:
                    if bad in val:
                        val = val.replace(bad, good)
                if val != doc[key]:
                    updates[key] = val
        if updates:
            col.update_one({'_id': doc['_id']}, {'$set': updates})
            total_fixed += 1
            print(f'Fixed {col_name} id={doc.get("id", "?")} keys={list(updates.keys())}')

print(f'\nTotal fixed: {total_fixed}')
