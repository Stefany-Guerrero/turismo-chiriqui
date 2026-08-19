from app import db, bcrypt
from flask_login import UserMixin
from datetime import datetime
from app.utils import panama_now

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    rol = db.Column(db.String(20), default='cliente')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=panama_now)
    reset_token = db.Column(db.String(200), nullable=True)
    reset_token_expira = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    blocked_until = db.Column(db.DateTime, nullable=True)
    
    cliente = db.relationship('Cliente', back_populates='usuario', uselist=False)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.rol == 'admin'
    
    def generar_token_reset(self):
        import secrets
        from datetime import timedelta
        token = secrets.token_hex(16)
        self.reset_token = token
        self.reset_token_expira = panama_now() + timedelta(hours=1)
        db.session.commit()
        return token
    
    def verificar_token_reset(self, token):
        from datetime import datetime
        if self.reset_token != token:
            return False
        if not self.reset_token_expira or panama_now() > self.reset_token_expira:
            return False
        return True
    
    def get_cliente(self):
        if self.cliente:
            return self.cliente
        from app.models.cliente import Cliente
        cliente = Cliente(
            nombre=self.nombre_completo,
            email=self.email,
            telefono=self.telefono or '',
            usuario_id=self.id
        )
        db.session.add(cliente)
        db.session.commit()
        return cliente
    
    def __repr__(self):
        return f'<Usuario {self.username}>'