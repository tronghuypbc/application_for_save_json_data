from flask import Flask, render_template, request, url_for, flash, redirect, Response
from services import alpaca_service
import init_db
from datetime import datetime

init_db.log()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    alpacas = alpaca_service.get_all_alpaca()
    return render_template('index.html', alpacas=alpacas)


@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    alpaca = alpaca_service.get_alpaca(id)
    alpaca_service.delete_alpaca(id)
    flash('"{}" was successfully deleted!'.format(alpaca['instruction']))
    return redirect(url_for('create'))


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'GET':
        alpacas = alpaca_service.get_all_alpaca()
        return render_template('create.html', alpacas=alpacas)

    if request.method == 'POST':
        instruction = request.form['instruction']
        input_val = request.form['input']
        output = request.form['output']
        if not instruction:
            flash('Instruction is required!')
            return redirect(url_for('create'))
        if not output:
            flash('Output is required!')
            return redirect(url_for('create'))
        try:
            alpaca_service.create_alpaca(instruction, input_val, output)
        except Exception as ex:
            flash(f'Error: {ex.args}')
        return redirect(url_for('create'))
    return render_template('create.html')


@app.route('/update/<int:id>', methods=('GET', 'POST'))
def update(id):
    alpaca = alpaca_service.get_alpaca(id)

    if request.method == 'GET':
        return render_template('update.html', alpaca=alpaca)

    if request.method == 'POST':
        instruction = request.form['instruction']
        input_val = request.form['input']
        output = request.form['output']

        if not instruction:
            flash('Instruction is required!')
        else:
            alpaca_service.update_alpaca(instruction, input_val, output, id)
            return redirect(url_for('update', id=id))

    return render_template('update.html', alpaca=alpaca)


@app.route('/export', methods=('GET',))
def export():
    timestamp = round(datetime.now().timestamp())
    json_data = alpaca_service.export_data_to_json_file()
    file_name = f'alpacas_{timestamp}' + ".json"
    return Response(json_data,
                    mimetype='application/json',
                    headers={'Content-Disposition': f'attachment;filename={file_name}'})

def init_app():
    app.run(host="0.0.0.0", port="5000")


if __name__ == "__main__":
    init_app()
