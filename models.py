from database import db 
import datetime



# code edited by Seth Jones
# Task model and sets to database  
class Task(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))
    members = db.Column("members", db.String(100))
    end_date = db.Column("end_date", db.String(50))
    status = db.Column("status", db.String(20))
    importance = db.Column("importance", db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="task", cascade="all, delete-orphan", lazy=True)

    # gets and sets 
    def __init__(self, title, text, date, members, end_date, status, importance, user_id):
        self.title = title
        self.text = text
        self.date = date
        self.members = members
        self.end_date = end_date
        self.status = status
        self.importance = importance
        self.user_id = user_id



# User class and sets to database
class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    tasks = db.relationship("Task", backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user",lazy=True)

    # gets and sets 
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.registered_on = datetime.date.today()



# Comment class and sets to database
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.VARCHAR, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # gets and sets 
    def __init__(self, content, task_id, user_id):
        self.date_posted = datetime.date.today()
        self.content = content
        self.task_id = task_id
        self.user_id = user_id
