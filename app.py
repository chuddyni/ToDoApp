from flask import Flask, g, render_template, flash, redirect, url_for, request
from datetime import datetime
import flask_login
import os, sqlite3

app = Flask(__name__)

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

app.config.update(dict(
    SECRET_KEY='bardzosekretnawartosc',
    DATABASE=os.path.join(app.root_path, 'db.sqlite'),
    SITE_NAME='Moje zadania'
))

users = {'chuddyni': {'password': '123'},
         'admin': {'password': '123'}}


def get_db():
    """Funkcja tworząca połączenie z bazą danych"""
    if not g.get('db'):  # jeżeli brak połączenia, to je tworzymy
        con = sqlite3.connect(app.config['DATABASE'])
        con.row_factory = sqlite3.Row
        g.db = con  # zapisujemy połączenie w kontekście aplikacji
    return g.db  # zwracamy połączenie z bazą


@app.teardown_appcontext
def close_db(error):
    """Zamykanie połączenia z bazą"""
    if g.get('db'):
        g.db.close()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    user.is_authenticated = request.form['password'] == users[email]['password']

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    email = request.form['email']
    if email not in users:
        return "Bad Username"
    if request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('zadania'))

    return 'Bad password'


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


@app.route("/")
@flask_login.login_required
def index():
    return redirect(url_for('zadania'))


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@app.route('/zadania', methods=['GET', 'POST'])
@flask_login.login_required
def zadania():
    error = None
    if request.method == 'POST':
        zadanie = request.form['zadanie'].strip()
        if len(zadanie) > 0:
            zrobione = '0'
            data_pub = datetime.now()
            db = get_db()
            db.execute('INSERT INTO zadania VALUES (?, ?, ?, ?, ?);',
                       [None, flask_login.current_user.id, zadanie, zrobione, data_pub])
            db.commit()
            flash('Dodano nowe zadanie.')
            return redirect(url_for('zadania'))

        error = 'Nie możesz dodać pustego zadania!'  # komunikat o błędzie

    db = get_db()
    kursor = db.execute('SELECT * FROM zadania where user =? ORDER BY data_pub DESC;',
                        [flask_login.current_user.id])
    zadania = kursor.fetchall()

    return render_template('zadania_lista.html', zadania=zadania, error=error)


@app.route("/zrobione", methods=["POST"])
@flask_login.login_required
def zrobione():
    zadanie_id = request.form["id"]
    db = get_db()
    db.execute("update zadania set zrobione=1 where id=? and user=?"
               , [zadanie_id, flask_login.current_user.id])
    db.commit()
    flash("Zmieniono status zadania")
    return redirect(url_for("zadania"))


@app.route("/usun", methods=["POST"])
@flask_login.login_required
def usun():
    zadanie_id = request.form["id"]
    db = get_db()
    db.execute("delete from zadania where id=? and user=?"
               , [zadanie_id, flask_login.current_user.id])
    db.commit()
    flash("Usunieto zadanie")
    return redirect(url_for("zadania"))


if __name__ == '__main__':
    app.run()
