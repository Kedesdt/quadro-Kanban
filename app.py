from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Team, Card, CardHistory
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-mude-em-producao'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Função para arquivar cards antigos
def archive_old_completed_cards():
    """Arquiva cards que estão há mais de 2 dias na coluna 'done'"""
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    old_cards = Card.query.filter(
        Card.status == 'done',
        Card.completed_at.isnot(None),
        Card.completed_at <= two_days_ago,
        Card.archived == False
    ).all()
    
    for card in old_cards:
        card.archived = True
        card.archived_at = datetime.utcnow()
        
        # Registrar no histórico
        history = CardHistory(
            card_id=card.id,
            action='archived',
            old_status='done',
            new_status='archived',
            user_id=card.creator_id,
            details='Card arquivado automaticamente após 2 dias concluído'
        )
        db.session.add(history)
    
    if old_cards:
        db.session.commit()
    
    return len(old_cards)

# Rotas de Autenticação
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('kanban'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('kanban'))
        else:
            flash('Usuário ou senha inválidos', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        team_name = request.form.get('team_name')
        
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        # Criar admin
        new_user = User(username=username, password=hashed_password, is_admin=True)
        db.session.add(new_user)
        db.session.commit()
        
        # Criar equipe
        new_team = Team(name=team_name, admin_id=new_user.id)
        db.session.add(new_team)
        db.session.commit()
        
        # Associar admin à equipe
        new_user.team_id = new_team.id
        db.session.commit()
        
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rotas do Kanban
@app.route('/kanban')
@login_required
def kanban():
    if not current_user.team_id:
        flash('Você não está em nenhuma equipe', 'error')
        return redirect(url_for('logout'))
    
    # Arquivar cards antigos
    archive_old_completed_cards()
    
    # Buscar apenas cards não arquivados
    cards = Card.query.filter_by(
        team_id=current_user.team_id, 
        archived=False
    ).order_by(Card.position).all()
    
    team_members = User.query.filter_by(team_id=current_user.team_id).all()
    
    # Cores disponíveis para os cards
    card_colors = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe',
        '#43e97b', '#fa709a', '#fee140', '#30cfd0',
        '#a8edea', '#ff9a9e', '#fbc2eb', '#a1c4fd'
    ]
    
    return render_template('kanban.html', cards=cards, team_members=team_members, card_colors=card_colors)

@app.route('/team', methods=['GET', 'POST'])
@login_required
def team_management():
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores.', 'error')
        return redirect(url_for('kanban'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_member':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if User.query.filter_by(username=username).first():
                flash('Usuário já existe', 'error')
            else:
                hashed_password = generate_password_hash(password)
                new_member = User(
                    username=username, 
                    password=hashed_password, 
                    is_admin=False,
                    team_id=current_user.team_id
                )
                db.session.add(new_member)
                db.session.commit()
                flash(f'Membro {username} adicionado com sucesso!', 'success')
        
        elif action == 'remove_member':
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            if user and user.team_id == current_user.team_id and not user.is_admin:
                db.session.delete(user)
                db.session.commit()
                flash('Membro removido com sucesso!', 'success')
    
    team = Team.query.get(current_user.team_id)
    members = User.query.filter_by(team_id=current_user.team_id).all()
    
    return render_template('team.html', team=team, members=members)

@app.route('/export')
@login_required
def export_data():
    cards = Card.query.filter_by(team_id=current_user.team_id, archived=False).order_by(Card.created_at.desc()).all()
    return render_template('export.html', cards=cards)

@app.route('/history')
@login_required
def history():
    """Página de histórico com cards arquivados e relatórios"""
    archived_cards = Card.query.filter_by(
        team_id=current_user.team_id,
        archived=True
    ).order_by(Card.archived_at.desc()).all()
    
    # Estatísticas
    total_archived = len(archived_cards)
    
    # Calcular tempo médio de conclusão
    completed_times = []
    for card in archived_cards:
        if card.completed_at and card.created_at:
            time_diff = (card.completed_at - card.created_at).total_seconds() / 3600  # horas
            completed_times.append(time_diff)
    
    avg_completion_time = sum(completed_times) / len(completed_times) if completed_times else 0
    
    return render_template('history.html', 
                         archived_cards=archived_cards,
                         total_archived=total_archived,
                         avg_completion_time=avg_completion_time)

@app.route('/api/export/json')
@login_required
def export_json():
    cards = Card.query.filter_by(team_id=current_user.team_id).all()
    data = []
    for card in cards:
        data.append({
            'id': card.id,
            'title': card.title,
            'description': card.description,
            'status': card.status,
            'creator': card.creator.username,
            'created_at': card.created_at.isoformat(),
            'updated_at': card.updated_at.isoformat()
        })
    return jsonify(data)

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(f'team_{current_user.team_id}')
        emit('user_connected', {'username': current_user.username}, room=f'team_{current_user.team_id}')

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f'team_{current_user.team_id}')

@socketio.on('create_card')
def handle_create_card(data):
    if not current_user.is_authenticated:
        return
    
    new_card = Card(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'todo'),
        position=data.get('position', 0),
        color=data.get('color', '#667eea'),
        creator_id=current_user.id,
        team_id=current_user.team_id
    )
    
    db.session.add(new_card)
    db.session.commit()
    
    # Registrar no histórico
    history = CardHistory(
        card_id=new_card.id,
        action='created',
        new_status='todo',
        user_id=current_user.id,
        details=f'Card criado por {current_user.username}'
    )
    db.session.add(history)
    db.session.commit()
    
    emit('card_created', {
        'id': new_card.id,
        'title': new_card.title,
        'description': new_card.description,
        'status': new_card.status,
        'position': new_card.position,
        'color': new_card.color,
        'creator': current_user.username,
        'assigned_to': None,
        'created_at': new_card.created_at.isoformat()
    }, room=f'team_{current_user.team_id}')

@socketio.on('update_card')
def handle_update_card(data):
    if not current_user.is_authenticated:
        return
    
    card = Card.query.get(data['id'])
    
    if card and card.team_id == current_user.team_id:
        old_status = card.status
        old_assigned = card.assigned_to_id
        
        if 'title' in data:
            card.title = data['title']
        if 'description' in data:
            card.description = data['description']
        if 'status' in data:
            card.status = data['status']
            
            # Se moveu o card, atribuir ao usuário atual
            if old_status != data['status']:
                card.assigned_to_id = current_user.id
                
                # Se moveu para "done", registrar data de conclusão
                if data['status'] == 'done' and old_status != 'done':
                    card.completed_at = datetime.utcnow()
                
                # Registrar movimento no histórico
                history = CardHistory(
                    card_id=card.id,
                    action='moved',
                    old_status=old_status,
                    new_status=data['status'],
                    user_id=current_user.id,
                    details=f'{current_user.username} moveu de {old_status} para {data["status"]}'
                )
                db.session.add(history)
                
                # Se foi atribuído, registrar no histórico
                if old_assigned != current_user.id:
                    assign_history = CardHistory(
                        card_id=card.id,
                        action='assigned',
                        user_id=current_user.id,
                        details=f'Card atribuído a {current_user.username}'
                    )
                    db.session.add(assign_history)
        
        if 'position' in data:
            card.position = data['position']
        
        card.updated_at = datetime.utcnow()
        db.session.commit()
        
        emit('card_updated', {
            'id': card.id,
            'title': card.title,
            'description': card.description,
            'status': card.status,
            'position': card.position,
            'color': card.color,
            'assigned_to': card.assigned_to.username if card.assigned_to else None,
            'assigned_to_id': card.assigned_to_id,
            'updated_by': current_user.username
        }, room=f'team_{current_user.team_id}')

@socketio.on('delete_card')
def handle_delete_card(data):
    if not current_user.is_authenticated:
        return
    
    card = Card.query.get(data['id'])
    
    if card and card.team_id == current_user.team_id:
        # Deletar permanentemente (histórico será deletado em cascata)
        db.session.delete(card)
        db.session.commit()
        
        emit('card_deleted', {
            'id': data['id'],
            'deleted_by': current_user.username
        }, room=f'team_{current_user.team_id}')

# Criar banco de dados
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
