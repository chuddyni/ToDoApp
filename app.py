from flask import Flask, g, render_template, flash, redirect, url_for, request
from datetime import datetime
import flask_login
import os, sqlite3

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY='bardzosekretnawartosc',
    DATABASE=os.path.join(app.root_path, 'db.sqlite'),
    SITE_NAME='Moje zadania'
))
user_name = "chuddyni"


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


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/zadania', methods=['GET', 'POST'])
def zadania():
    error = None
    if request.method == 'POST':
        zadanie = request.form['zadanie'].strip()
        if len(zadanie) > 0:
            zrobione = '0'
            data_pub = datetime.now()
            db = get_db()
            db.execute('INSERT INTO zadania VALUES (?, ?, ?, ?, ?);',
                       [None, user_name, zadanie, zrobione, data_pub])
            db.commit()
            flash('Dodano nowe zadanie.')
            return redirect(url_for('zadania'))

        error = 'Nie możesz dodać pustego zadania!'  # komunikat o błędzie

    db = get_db()
    kursor = db.execute('SELECT * FROM zadania where user =? ORDER BY data_pub DESC;',
                        [user_name])
    zadania = kursor.fetchall()
    for row in zadania:
        # row[0] returns the first column in the query (name), row[1] returns email column.
        print('{0} : {1}, {2}, {3}, {4}'.format(row[0], row[1], row[2], row[3], row[4]))

    return render_template('zadania_lista.html', zadania=zadania, error=error)


@app.route("/zrobione", methods=["POST"])
def zrobione():
    zadanie_id = request.form["id"]
    db = get_db()
    db.execute("update zadania set zrobione=1 where id=? and user=?"
               , [zadanie_id, user_name])
    db.commit()
    flash("Zmieniono status zadania")
    return redirect(url_for("zadania"))


@app.route("/usun", methods=["POST"])
def usun():
    zadanie_id = request.form["id"]
    db = get_db()
    db.execute("delete from zadania where id=? and user=?"
               , [zadanie_id, user_name])
    db.commit()
    flash("Usunieto zadanie")
    return redirect(url_for("zadania"))


if __name__ == '__main__':
    app.run()
