from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.forms import LoginForm, RegistrationForm, RecipeForm, EditRecipeForm
from db import create_tables, mysql
from models import User, Recipe
from werkzeug.utils import secure_filename
from forms.forms import RecipeForm
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/gambar'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'resep-app'
app.config['MYSQL_HOST'] = 'localhost'

mysql.init_app(app)

app.secret_key = 'aq 4l4y'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    create_tables()  # Inisialisasi tabel setelah aplikasi dan mysql diinisialisasi

def check_user_authentication():
    return 'user_id' in session

@login_manager.user_loader
def load_user(user_id):
    return User(user_id, 'username', 'password')

@app.route('/')
@app.route('/home')
def index():
    # Ambil semua resep dari database
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, content, category FROM recipe")
    resep_list = cur.fetchall()
    cur.close()
    return render_template('slider.html', resep_list=resep_list)

@app.route('/static/gambar/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/search', methods=['GET'])
def search():
    # Retrieve search query from the URL parameters
    query = request.args.get('search', '')

    # Execute a simple search query on the 'recipe' table
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, content, category, gambar FROM recipe WHERE title LIKE %s", ('%' + query + '%',))
    columns = [column[0] for column in cur.description]
    recipes = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()

    return render_template('search_results.html', recipes=recipes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Proses otentikasi
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (form.username.data, form.password.data))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('index'))

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout berhasil!', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Proses registrasi
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (form.username.data, form.password.data))
        mysql.connection.commit()
        cursor.close()

        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        # Proses penambahan resep ke database
        new_recipe = Recipe(
            id=None,
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            user_id=current_user.id,
            gambar=None  # Atur nilai gambar sesuai dengan cara Anda mengelolanya
        )

        # Unggah gambar dan simpan nama file gambar ke dalam database
        if 'gambar' in request.files:
            gambar = request.files['gambar']
            if gambar.filename != '':
                filename = secure_filename(gambar.filename)
                gambar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_recipe.gambar = filename

        # Simpan resep ke database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO recipe (title, content, category, user_id, gambar)
            VALUES (%s, %s, %s, %s, %s)
        """, (new_recipe.title, new_recipe.content, new_recipe.category, new_recipe.user_id, new_recipe.gambar))
        mysql.connection.commit()
        cur.close()

        flash('Resep berhasil ditambahkan!', 'success')
        return redirect(url_for('index'))

    return render_template('add_recipe.html', form=form)

@app.route('/edit_recipe/<int:id>', methods=['GET', 'POST'])
def edit_recipe(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, content, category FROM recipe WHERE id = %s", (id,))
    recipe_data = cur.fetchone()
    
    if recipe_data:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            category = request.form['category']

            # Update data di database
            cur.execute("UPDATE recipe SET title=%s, content=%s, category=%s WHERE id=%s", (title, content, category, id))
            mysql.connection.commit()

            return redirect(url_for('view_recipes'))

        return render_template('edit_recipe.html', id=id, recipe=recipe_data)

    return "Resep tidak ditemukan"

@app.route('/hapus_resep/<int:resep_id>')
@login_required
def hapus_resep(resep_id):
    # Implementasi penghapusan resep
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM recipe WHERE id=%s", (resep_id,))
    mysql.connection.commit()
    cursor.close()

    flash('Resep berhasil dihapus!', 'success')
    return redirect(url_for('index'))


@app.route('/recipes')
def view_recipes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, content, category, gambar FROM recipe")
    recipes_data = cur.fetchall()
    cur.close()
    recipes = [Recipe(id, title, content, category, gambar) for id, title, content, category, gambar in recipes_data]
    return render_template('recipes.html', recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
