from datetime import datetime
from src.models.user import db

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)  # Duração em minutos
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)  # Opcional, se estiver estudando um tópico específico
    description = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'topic_id': self.topic_id,
            'description': self.description
        }
    
    def calculate_duration(self):
        """Calcula a duração da sessão de estudo em minutos"""
        if self.end_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
            return self.duration_minutes
        return None

class QuestionRecord(db.Model):
    __tablename__ = 'question_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)  # Opcional, se estiver associado a um tópico
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    source = db.Column(db.String(200), nullable=True)  # Ex: "Prova 2012", "Simulado X"
    specific_topic = db.Column(db.String(200), nullable=True)  # Tópico específico dentro da matéria
    difficulty_level = db.Column(db.String(20), nullable=True)  # Fácil, Médio, Difícil
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    wrong_answers = db.Column(db.Integer, nullable=False)
    accuracy_percentage = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic_id': self.topic_id,
            'date': self.date.isoformat(),
            'source': self.source,
            'specific_topic': self.specific_topic,
            'difficulty_level': self.difficulty_level,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'accuracy_percentage': self.accuracy_percentage,
            'notes': self.notes
        }
    
    def calculate_accuracy(self):
        """Calcula a porcentagem de acertos"""
        if self.total_questions > 0:
            self.accuracy_percentage = (self.correct_answers / self.total_questions) * 100
            return self.accuracy_percentage
        return 0

class EditalItem(db.Model):
    __tablename__ = 'edital_items'
    
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(100), nullable=False)  # Seção do edital
    subsection = db.Column(db.String(100), nullable=True)  # Subseção (opcional)
    content = db.Column(db.Text, nullable=False)  # Conteúdo do item
    order_index = db.Column(db.Integer, nullable=False)  # Índice para ordenação
    
    # Relacionamentos
    progress_records = db.relationship('EditalProgress', backref='edital_item', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'section': self.section,
            'subsection': self.subsection,
            'content': self.content,
            'order_index': self.order_index
        }

class EditalProgress(db.Model):
    __tablename__ = 'edital_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    edital_item_id = db.Column(db.Integer, db.ForeignKey('edital_items.id'), nullable=False)
    is_studied = db.Column(db.Boolean, default=False)
    study_date = db.Column(db.DateTime, nullable=True)
    confidence_level = db.Column(db.String(20), default='Baixo')  # Baixo, Médio, Alto
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'edital_item_id': self.edital_item_id,
            'is_studied': self.is_studied,
            'study_date': self.study_date.isoformat() if self.study_date else None,
            'confidence_level': self.confidence_level,
            'notes': self.notes
        }
