from flask import Flask, render_template, request, url_for, flash, redirect, Response, session
from services import alpaca_service
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

app.app_context().push()


class Alpaca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instruction = db.Column(db.String(100))
    input = db.Column(db.String(100))
    output = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer)

    def __init__(self, instruction, input, output, created_by):
        self.instruction = instruction
        self.input = input
        self.output = output
        self.created_by = created_by


@app.route('/alpaca')
def alpaca():
    if not session.get('logged_in'):
        return redirect(url_for('user_index'))

    if session.get('user_info').get('user_role') == 'admin':
        alpacas = Alpaca.query.all()
    else:
        alpacas = Alpaca.query.filter_by(created_by=session.get('user_info').get('user_id'))
    return render_template('index.html', alpacas=alpacas)


@app.route('/')
def index():
    if session.get('logged_in'):
        return render_template('home.html')
    else:
        return render_template('login.html', message="Hello!")


@app.route('/home')
def home():
    if session.get('logged_in'):
        return render_template('home.html')
    else:
        return render_template('login.html', message="Hello!")


@app.route('/alpaca/delete/<int:alpaca_id>', methods=('POST',))
def delete(alpaca_id):
    if not session.get('logged_in'):
        return redirect(url_for('user_index'))

    alpaca = Alpaca.query.filter_by(id=alpaca_id).first()
    db.session.delete(alpaca)
    db.session.commit()
    flash('"{}" was successfully deleted!'.format(alpaca.instruction))
    return redirect(url_for('create'))


@app.route('/alpaca/create', methods=('GET', 'POST'))
def create():
    if not session.get('logged_in'):
        return redirect(url_for('user_index'))

    if request.method == 'GET':
        if session.get('user_info').get('user_role') == 'admin':
            alpacas = Alpaca.query.all()
        else:
            alpacas = Alpaca.query.filter_by(created_by=session.get('user_info').get('user_id'))
        return render_template('create.html', alpacas=alpacas)

    if request.method == 'POST':
        instruction = request.form['instruction']
        input_val = request.form['input']
        output = request.form['output']
        created_by = session.get('user_info').get('user_id')
        if not instruction:
            flash('Instruction is required!')
            return redirect(url_for('create'))
        if not output:
            flash('Output is required!')
            return redirect(url_for('create'))
        try:
            db.session.add(Alpaca(instruction, input_val, output, created_by))
            db.session.commit()
        except Exception as ex:
            flash(f'Error: {ex.args}')
        return redirect(url_for('create'))
    return render_template('create.html')


@app.route('/alpaca/update/<int:alpaca_id>', methods=('GET', 'POST'))
def update(alpaca_id):
    if not session.get('logged_in'):
        return redirect(url_for('user_index'))

    alpaca = Alpaca.query.filter_by(id=alpaca_id).first()

    if request.method == 'GET':
        return render_template('update.html', alpaca=alpaca)

    if request.method == 'POST':
        instruction = request.form['instruction']
        input_val = request.form['input']
        output = request.form['output']

        if not instruction:
            flash('Instruction is required!')
        else:
            try:
                Alpaca.query.filter_by(id=alpaca_id).update(
                    dict(instruction=instruction, input=input_val, output=output))
                db.session.commit()
            except Exception as e:
                flash(f"Error: {e.args}")
            return redirect(url_for('update', alpaca_id=alpaca_id))

    return render_template('update.html', alpaca=alpaca)


@app.route('/alpaca/export', methods=('GET',))
def export():
    if not session.get('logged_in'):
        return redirect(url_for('user_index'))

    user_info = session.get('user_info')
    timestamp = round(datetime.now().timestamp())
    json_data = alpaca_service.export_data_to_json_file(user_info)
    file_name = f'alpacas_{timestamp}' + ".json"
    return Response(json_data,
                    mimetype='application/json',
                    headers={'Content-Disposition': f'attachment;filename={file_name}'})


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(100), default="user")

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/user', methods=['GET'])
def user_index():
    if session.get('logged_in'):
        user = session.get('user_info')
        return render_template('user.html', user=user)
    else:
        return render_template('login.html', message="Hello!")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('login.html', message="User Already Exists")
    else:
        return render_template('user_register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('user_login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        data = User.query.filter_by(username=username, password=password).first()
        if data is not None:
            session['logged_in'] = True
            session['user_info'] = dict(user_id=data.id, username=data.username, user_role=data.role)
            return redirect(url_for('user_index'))
        return render_template('login.html', message="Incorrect Details")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('user_index'))


if __name__ == '__main__':
    app.secret_key = "ThisIsNotASecret:p"
    db.create_all()
    app.run(host='0.0.0.0', port=8080)
