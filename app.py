from sqlalchemy import text
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# Initialisation de l'application Flask
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})  # Autorise uniquement React en local  # Permettre CORS pour les appels d'API depuis le frontend

# Configuration de la connexion MySQL avec SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/task_manager_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de SQLAlchemy
db = SQLAlchemy(app)
@app.route('/test_db_connection')
def test_db_connection():
    try:
        # Essayer de se connecter et d'exécuter une commande SQL
        db.session.execute(text('SELECT 1'))
        return "Connexion à la base de données réussie!", 200
    except Exception as e:
        return f"Erreur de connexion : {str(e)}", 500
# Modèle User (Utilisateur)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Modèle Task (Tâche)  
# Modèle Task (Tâche)  
class Task(db.Model):  
    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String(100), nullable=False)  
    description = db.Column(db.String(255), nullable=True)  
    completed = db.Column(db.Boolean, default=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)  # Lien avec Project  

    user = db.relationship('User', backref=db.backref('tasks', lazy=True))  
   
    def __repr__(self):  
        return f"<Task {self.title}>"  

# Modèle Project (Projet)  
class Project(db.Model):  
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(100), nullable=False)  
    description = db.Column(db.String(255), nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  

    tasks = db.relationship('Task', backref='project', lazy=True)  # Gardez le backref ici  

    def __repr__(self):  
        return f"<Project {self.name}>"


# Routes pour User
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "All fields (username, email, password) are required."}), 400

    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": user.id}), 201

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} for user in users])

@app.route('/api/users/<int:id>', methods=['GET'])  
def get_user(id):  
    user = User.query.get(id)  
    if not user:  
        return jsonify({"error": "User not found"}), 404  

    return jsonify({  
        "id": user.id,  
        "username": user.username,  
        "email": user.email  
    })  
@app.route('/api/users/username/<string:username>', methods=['GET'])  
def get_user_by_username(username):  
    user = User.query.filter_by(username=username).first()  
    if not user:  
        return jsonify({"error": "User not found"}), 404  

    return jsonify({  
        "id": user.id,  
        "username": user.username,  
        "email": user.email  
    })
@app.route('/api/users/<int:id>', methods=['PUT'])  
def update_user(id):  
    user = User.query.get(id)  
    if not user:  
        return jsonify({"error": "User not found"}), 404  

    data = request.get_json()  
    user.username = data.get('username', user.username)  
    user.email = data.get('email', user.email)  
    user.password = data.get('password', user.password)  # Mettez à jour le mot de passe uniquement si fourni  

    db.session.commit()  

    return jsonify({  
        "message": "User updated successfully",  
        "user": {  
            "id": user.id,  
            "username": user.username,  
            "email": user.email  
        }  
    })  

@app.route('/api/users/<int:id>', methods=['DELETE'])  
def delete_user(id):  
    user = User.query.get(id)  
    if not user:  
        return jsonify({"error": "User not found"}), 404  

    db.session.delete(user)  
    db.session.commit()  

    return jsonify({"message": "User deleted successfully"})  
#AJOUTER TOUS LES CRUD PAR NOM
# Créez la base de données et les tables si elles n'existent pas déjà  
with app.app_context():  
     # (optionnel, seulement si vous pouvez perdre les données)  
    db.create_all()  

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    user_id = data.get('user_id')
    project_id = data.get('project_id')  # Champ pour lier la tâche à un projet

    if not title or not description :
        return jsonify({"error": "All fields (title, description) are required."}), 400

    task = Task(title=title, description=description, user_id=user_id, project_id=project_id)
    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task created successfully", "task_id": task.id}), 201

@app.route('/api/tasks/title/<string:title>', methods=['GET'])  
def get_task_by_title(title):  
    task = Task.query.filter_by(title=title).first()  
    if not task:  
        return jsonify({"error": "Task not found"}), 404  

    return jsonify({  
        "id": task.id,  
        "title": task.title,  
        "description": task.description,  
        "completed": task.completed,  
        "created_at": task.created_at,  
        "user_id": task.user_id,  
        "project_id": task.project_id  
    })
@app.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
def get_tasks_for_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    tasks = project.tasks  # Accède aux tâches du projet via la relation
    return jsonify([{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at,
        "user_id": task.user_id
    } for task in tasks])


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at,
        "user_id": task.user_id,
        "project_id": task.project_id
        
    } for task in tasks])

@app.route('/api/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at,
        "user_id": task.user_id
    })


@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)

    db.session.commit()

    return jsonify({
        "message": "Task updated successfully",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at,
            "user_id": task.user_id
        }
    })

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"})

# Routes pour Project
@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({"error": "Project name is required."}), 400

    project = Project(name=name, description=description)
    db.session.add(project)
    db.session.commit()

    return jsonify({"message": "Project created successfully", "project_id": project.id}), 201


@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([{
        "id": project.id,
        "name": project.name,
        "description": project.description
    } for project in projects])

@app.route('/api/projects/<int:id>', methods=['GET'])
def get_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    return jsonify({
        "id": project.id,
        "name": project.name,
        "description": project.description

    })
@app.route('/api/projects/name/<string:name>', methods=['GET'])  
def get_project_by_name(name):  
    project = Project.query.filter_by(name=name).first()  
    if not project:  
        return jsonify({"error": "Project not found"}), 404  

    return jsonify({  
        "id": project.id,  
        "name": project.name,  
        "description": project.description  
    })
@app.route('/api/projects/<int:id>', methods=['PUT'])
def update_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    project.name = data.get('name', project.name)
    project.description = data.get('description', project.description)

    db.session.commit()

    return jsonify({
        "message": "Project updated successfully",
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description
        }
    })

@app.route('/api/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({"message": "Project deleted successfully"})

@app.route('/api/projects/<int:project_id>/tasks/<int:task_id>/toggle-completion', methods=['PATCH'])
def toggle_task_completion(project_id, task_id):
    task = Task.query.filter_by(id=task_id, project_id=project_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    task.completed = not task.completed
    db.session.commit()

    return jsonify({
        "message": "Task completion toggled successfully",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at,
            "user_id": task.user_id,
            "project_id": task.project_id
        }
    })



# Créez la base de données et les tables si elles n'existent pas déjà
with app.app_context():  
     # (optionnel, seulement si vous pouvez perdre les données)  
    db.create_all()
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001)
