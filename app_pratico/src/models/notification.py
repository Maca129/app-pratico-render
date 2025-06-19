from datetime import datetime
from src.models.user import db

class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    enable_browser_notifications = db.Column(db.Boolean, default=True)
    enable_email_notifications = db.Column(db.Boolean, default=False)
    reminder_minutes_before = db.Column(db.Integer, default=30)  # Minutos antes da revisão
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'enable_browser_notifications': self.enable_browser_notifications,
            'enable_email_notifications': self.enable_email_notifications,
            'reminder_minutes_before': self.reminder_minutes_before,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    revision_id = db.Column(db.Integer, db.ForeignKey('revisions.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_for = db.Column(db.DateTime, nullable=True)  # Para notificações agendadas
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'revision_id': self.revision_id,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None
        }
