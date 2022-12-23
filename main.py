# imports
import os # os is used to get environment variables IP & PORT

from flask import Flask, render_template, request, redirect, url_for, session # Flask is the web app that we will customize
from forms import RegisterForm, LoginForm, CommentForm
from flask_bcrypt import Bcrypt
from database import db
from models import Task as Task 
from models import User as User
from models import Comment as Comment




# code edited by Seth Jones
# creates the app
app = Flask(__name__)    


# sets the encryption 
bcrypt = Bcrypt(app)
app.secret_key = "super secret key"
app.config['SECRETY_KEY'] = 'SE3155'


# sets the database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_task_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False


#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)


# Setup models for database  
with app.app_context():
    db.create_all()   


# Homepage route
@app.route('/')
@app.route('/index')
def index():
    if session.get('user'):
        # gets user's session if they have an account 
      return render_template('index.html', user = session['user'])
    return render_template("index.html")



# Tasks route
@app.route('/tasks')
def get_tasks():
    if session.get('user'):
        # gets tasks from user's database 
        my_tasks = db.session.query(Task).filter_by(user_id=session['user_id']).all()

        return render_template('tasks.html', tasks=my_tasks, user=session['user'])
    else:
        return redirect(url_for('login'))



# Specific task route 
@app.route('/tasks/<task_id>')
def get_task(task_id):
    
    if session.get('user'):
        # gets task from database and renders it 
        my_task = db.session.query(Task).filter_by(id=task_id, user_id=session['user_id']).one()
        form = CommentForm()
        return render_template('task.html', task = my_task, user =session['user'], form=form)
    else:
        return redirect(url_for('login'))



# New task route
@app.route('/tasks/new', methods=['GET','POST'])
def new_task():
    if session.get('user'):
        #check method 
        if request.method == 'POST':
            # gets task objects 
            title = request.form['title']
            text = request.form['taskText']
            members = request.form['taskMembers']
            end_date = request.form['taskEndDate']
            status = request.form['taskStatus']
            # create time stamp
            from datetime import date 
            today = date.today()
            # format date 
            today = today.strftime("%m-%d-%Y")
            #importance 
            importance = request.form['importanceValue']

            new_record = Task(title, text, today, members, end_date, status, importance, session['user_id'])
            db.session.add(new_record)
            db.session.commit()

            return redirect(url_for('get_tasks'))
        else:
            return render_template('new.html', user = session['user'])
    else:
        return redirect(url_for('login'))



# Edited task route
@app.route('/tasks/edit/<task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    
    if session.get('user'):
        if request.method == 'POST':

            # gets task objects 
            title = request.form['title']
            text = request.form['taskText']
            members = request.form['taskMembers']
            end_date = request.form['taskEndDate']
            status = request.form['taskStatus']
            importance = request.form['importanceValue']

            task = db.session.query(Task).filter_by(id=task_id).one()
            task.title = title
            task.text = text
            task.members = members
            task.end_date = end_date
            task.status = status
            task.importance = importance

            # commits 
            db.session.add(task)
            db.session.commit()

            return redirect(url_for('get_tasks'))
        else:
            my_task = db.session.query(Task).filter_by(id=task_id).one()
            return render_template('new.html', task=my_task, user=session['user'])
    else: 
        return redirect(url_for('login'))



# Route for deleting task 
@app.route('/tasks/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    if session.get('user'):
        my_task = db.session.query(Task).filter_by(id=task_id).one()
        db.session.delete(my_task)
        db.session.commit()

        return redirect(url_for('get_tasks'))
    else:
        return redirect(url_for('login'))



# Route for posting a comment to a task 
@app.route('/tasks/<task_id>/comment', methods=['POST'])
def new_comment(task_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(task_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_task', task_id=task_id))
    else:
        return redirect(url_for('login'))



# Route for registering an account 
@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # generates password hash
        h_password = bcrypt.generate_password_hash(request.form['password'])
        
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create new user
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  
        # show user dashboard view
        return redirect(url_for('get_tasks'))

    # error register view 
    return render_template('register.html', form=form)



# Route for login
@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():

        the_user = db.session.query(User).filter_by(email=request.form['email']).one()

        if bcrypt.check_password_hash( the_user.password, request.form['password']):
            # password match and adding user info to the session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render task view
            return redirect(url_for('get_tasks'))

        # password check failed
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)



# Route for logging out 
@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()
    # returns the hompage "index" after logging out    
    return redirect(url_for('index'))



app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

