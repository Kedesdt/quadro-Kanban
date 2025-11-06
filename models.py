from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    team = db.relationship('Team', foreign_keys=[team_id], back_populates='members')
    created_cards = db.relationship('Card', foreign_keys='Card.creator_id', back_populates='creator', lazy=True)
    assigned_cards = db.relationship('Card', foreign_keys='Card.assigned_to_id', back_populates='assigned_to', lazy=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin = db.relationship('User', foreign_keys=[admin_id])
    members = db.relationship('User', foreign_keys='User.team_id', back_populates='team')
    cards = db.relationship('Card', back_populates='team', lazy=True)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='todo')  # todo, doing, done
    position = db.Column(db.Integer, default=0)
    color = db.Column(db.String(7), default='#667eea')  # Cor em hexadecimal
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    archived = db.Column(db.Boolean, default=False)
    archived_at = db.Column(db.DateTime, nullable=True)
    
    creator = db.relationship('User', foreign_keys=[creator_id], back_populates='created_cards')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], back_populates='assigned_cards')
    team = db.relationship('Team', back_populates='cards')
    history = db.relationship('CardHistory', back_populates='card', cascade='all, delete-orphan', lazy=True)
    
    def get_time_in_status(self):
        """Calcula tempo no status atual"""
        if self.completed_at and self.status == 'done':
            return (self.completed_at - self.created_at).total_seconds() / 3600  # em horas
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600

class CardHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # created, moved, assigned, completed, archived
    old_status = db.Column(db.String(50), nullable=True)
    new_status = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=True)
    
    card = db.relationship('Card', back_populates='history')
    user = db.relationship('User')
