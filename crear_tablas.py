from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tablas creadas correctamente')
    
    # Verificar tablas creadas
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tablas = inspector.get_table_names()
    print(f'📋 Tablas creadas: {tablas}')