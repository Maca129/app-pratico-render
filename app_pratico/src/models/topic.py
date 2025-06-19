from datetime import datetime, timedelta
from src.models.user import db

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, nullable=False)  # G1, G2, G3
    group_name = db.Column(db.String(100), nullable=False)  # Nome do grupo
    name = db.Column(db.String(200), nullable=False)  # Nome do tópico
    description = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    confidence_level = db.Column(db.String(20), default='Baixo')  # Baixo, Médio, Alto
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    revisions = db.relationship('Revision', backref='topic', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'group_name': self.group_name,
            'name': self.name,
            'description': self.description,
            'is_completed': self.is_completed,
            'confidence_level': self.confidence_level,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class Revision(db.Model):
    __tablename__ = 'revisions'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    revision_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4, 5
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    notify = db.Column(db.Boolean, default=True)  # Se deve notificar o usuário
    color = db.Column(db.String(20), default='#4285f4')  # Cor para visualização no calendário
    
    # Relacionamentos
    notifications = db.relationship('Notification', backref='revision', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'revision_number': self.revision_number,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'notify': self.notify,
            'color': self.color
        }
