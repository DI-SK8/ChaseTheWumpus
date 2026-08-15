from flask import Flask, render_template, session, request, redirect, url_for, flash
from gameLogic import *
from db import *
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'une_cle_secrete_tres_simple_pour_le_test')

app.config['SESSION_COOKIE_HTTPONLY'] = True #prot javascrips et xss
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' #CSRF

try:
    init_db()
except Exception as e:
    print(f"Erreur d'initialisation BDD : {e}")

@app.after_request
def add_header(response): #evite le retour
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/home')
def home():
    if 'user' not in session:
        flash("Veuillez vous connecter.", "error")
        return redirect(url_for('login'))

    stats = get_stats(session['user'])

    return render_template('home.html', user=session['user'], stats=stats)

@app.route('/logout',methods=['POST','GET'])
def logout():
    session.clear()
    flash("Vous avez été déconnecté avec succès.", "info")
    return redirect(url_for('login'))

@app.route('/leaderboard',methods=['POST','GET'])
def leaderboard():
    if 'user' not in session:
        flash("Veuillez vous connecter pour voir le classement.", "error")
        return redirect(url_for('login'))

    leaderboard = get_leaderboard()

    return render_template('leaderboard.html', leaderboard=leaderboard)

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name_user = request.form.get('nom', '')
        pswd_user = request.form.get('password', '')

        if not name_user or not pswd_user:
            flash("Merci de remplir tous les champs", "error")
            return render_template('index.html')

        isValid = verify_user(name_user, pswd_user)
        if not isValid:
            flash("Informations de connexion incorrectes", "error")
            return render_template('index.html')

        session['user'] = name_user

        return redirect(url_for('home'))

    return render_template('index.html')

@app.route('/SignIn',methods=['GET', 'POST'])
def SignIn():
    if 'user' in session:
        session.clear()
    if request.method == 'POST':  # post methode
        name_user = request.form.get('nom', '')
        pswd_user = request.form.get('password', '')
        if name_user == '' or pswd_user == '':
            flash("Merci de remplir les champs", "error")
        elif is_user_used(name_user) :
            flash("le pseudo est déjà utilisé", "error")
        elif not is_pwd_ok(pswd_user) :
            flash("le mot de passe doit faire minimu 6 charcatere avec un chiffre et une majuscule", "error")
        else :
            add_user(name_user, pswd_user)
            session['user'] = name_user
            return redirect(url_for('home'))
    return render_template('SignIn.html')

@app.route('/game', methods=['POST', 'GET'])
def game():
    if 'user' not in session:
        flash("Veuillez vous connecter pour jouer.", "error")
        return redirect(url_for('login'))

    if request.method == 'GET' and 'grid' not in session:
        flash("Veuillez démarrer une nouvelle partie.", "info")
        return redirect(url_for('home'))

    if request.method == 'POST' and 'gameMode' in request.form:
        difficulty = request.form.get('gameMode')
        speed = request.form.get('fast')
        mode = request.form.get('blind')
        session['mode'] = mode
        session['speed'] = speed

        grid, wumpus = GenerateGrid(difficulty)
        start = GetStartCharacter(grid, 'player')
        pos_creature = {"player" :start,
                    "wumpus" :wumpus}
        pos_creature["bats"] = GetBat(difficulty, grid, pos_creature)

        fog_grid = None
        fog_grid = GetFog(pos_creature,mode, fog_grid)

        session['fogGrid'] = fog_grid
        session['pos_creature'] = pos_creature
        session['grid'] = grid
        session['is_dead'] = False
        session['shoot'] = False

        return redirect(url_for('game'))
    elif request.method == 'POST':
        pos_creature = session.get('pos_creature')
        grid = session.get('grid')

        if not session.get('is_dead', False):
            if request.form.get('shoot') == 'shoot':
                direction = request.form.get("shoot_dir")
                win = ShootArrow(grid, direction, pos_creature)
                if win:
                    flash("Victory", "win")
                    update_stats(session['user'], 'win')
                else:
                    flash("Tir raté", "lose")
                    update_stats(session['user'], 'miss')

                session['is_dead'] = True
                session['fogGrid'] = GetFog(pos_creature, 'clear', None)

            else:
                direction = request.form.get('direction')
                speed = session.get('speed', None)
                DepPlayer(grid, direction, pos_creature, speed)
                pos_creature = UseBat(grid, pos_creature)

                mode = session.get('mode', None)
                fog_grid = session.get('fogGrid')
                session['fogGrid'] = GetFog(pos_creature, mode, fog_grid)

                type_of_death = IsHeDead(grid, pos_creature)
                if type_of_death == 1:
                    flash("Mort par le Wumpus.", "lose")
                    session['is_dead'] = True
                    update_stats(session['user'], 'wumpus')
                    session['fogGrid'] = GetFog(pos_creature, 'clear', None)

                elif type_of_death == 2:
                    flash("Mort par un puits.", "lose")
                    session['is_dead'] = True
                    update_stats(session['user'], 'pits')
                    session['fogGrid'] = GetFog(pos_creature, 'clear', None)

            session['pos_creature'] = pos_creature
            return redirect(url_for('game'))
    else:
        pos_creature = session.get('pos_creature')
        grid = session.get('grid')
        fog_grid = session.get('fogGrid')

    return render_template('game.html',
                           grid=grid,
                           pos_creature=pos_creature,
                           is_dead=session.get('is_dead', False),
                           shoot=session.get('shoot', False),
                           fog_grid=fog_grid,)

if __name__ == '__main__':
    app.run(debug=False) # mettre en false a la fin