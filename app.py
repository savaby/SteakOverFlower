from flask import Flask, g, request, render_template, url_for, session
from werkzeug.utils import redirect
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import functools
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'connection'):
        g.connection.close()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id', None) is None:
            return redirect(url_for('login'))
        
        return view(**kwargs)
    return wrapped_view

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('''select question.id, question.title, question.explanation, user.name, count(answer.id) as answers 
                        from question join user on user.id = question.user_id 
                        left join answer on question.id = answer.question_id 
                        group by question.id, question.title, question.explanation, user.name 
                        order by question.id desc''')
    questions = cur.fetchall()
    return render_template('index.html', questions = questions)

@app.route('/login', methods=["POST", "GET"])
def login():
    error = ''
    if request.method == "POST":
        db = get_db()
        name = request.form['name']
        password = request.form['password']
        cur = db.execute ("select id, name, password from user where name = ?", [name])
        user = cur.fetchone()
        if user:
            if check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))
        else:
            error = "Error credentials!"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=["POST", "GET"])
def register():
    error = ''
    if request.method == "POST":
        db = get_db()
        name = request.form['name']
        password = request.form['password']
        password = generate_password_hash(password, method='sha256')
        cur = db.execute ("select name from user where name = ?", [name])
        if not cur.fetchone():
            db.execute('insert into user(name, password) values(?, ?)', [name, password])
            db.commit()
            return redirect(url_for('login'))
        else:
            error = "User name exists!"
    return render_template('register.html', error=error)

@app.route('/question', methods=["POST", "GET"])
@login_required
def question():
    if request.method == "POST":
        db = get_db()
        user = session['user_id']
        text = request.form['text']
        explanation = request.form['explanation']
        db.execute('insert into question(title, explanation, user_id) values(?, ?, ?)', [text, explanation, user])
        db.commit()
        return redirect(url_for('index'))
    return render_template('question.html')

@app.route('/answer/<int:question>', methods=["POST", "GET"])
@login_required
def answer(question):
    db = get_db()
    if request.method == "POST":

        user = session['user_id']
        explanation = request.form['explanation']
        question = request.form['question']
        db.execute('insert into answer(explanation, user_id, question_id) values(?, ?, ?)', [explanation, user, question])
        db.commit()
        return redirect(url_for('index'))
    cur = db.execute('select id, title, explanation from question where id = ?', [question])
    q = cur.fetchone()
    return render_template('answer.html', q = q)

@app.route('/view/<int:question>')
def view(question):
    db = get_db()
    cur = db.execute('''select question.id, question.title, question.explanation, user.name 
                        from question join user on user.id = question.user_id where question.id = ?''', [question])
    q = cur.fetchone()
    cur = db.execute('''select answer.explanation, user.name from answer join user on user.id = answer.user_id where answer.question_id = ?''', [question])
    a = cur.fetchall()
    return render_template('view.html', q=q, a=a)











if __name__ == "__main__":
    app.run(debug=True)