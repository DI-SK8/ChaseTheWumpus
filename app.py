from flask import Flask, render_template, session, request, redirect, url_for, flash
from gameLogic import *
from db import *
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__) # utilisation de flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_fallback') # on peut changer la clé apres avoir redémarer le serveur

app.config['SESSION_COOKIE_HTTPONLY'] = True #prot javascrips et xss
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' #CSRF

init_db()

@app.after_request
def add_header(response): #evite le retour
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
@app.route('/')
def home():
    #faire session
    session['xyz']=42
    a=session['xyz']
    b=session.get('xyz',-1) # voir ce que c'est

    return redirect(url_for('login'))


@app.route('/login',methods=['POST','GET'])
def login():
    if 'user' in session:
        session.clear()
        flash("Vous avez été déconnecté en quittant la partie.", "info")
    if request.method == 'POST':
        name_user=request.form['nom']
        pswd_user=request.form['password']

        if name_user == '' or pswd_user == '':
            flash("Merci de remplir les champs", "error")
        elif not verify_user(name_user, pswd_user):
            flash("les informations de connexion ne sont pas corect", "error")
        else:
            session['user'] = name_user
            return redirect(url_for('game'))

    return render_template('index.html')
@app.route('/SignIn',methods=['GET', 'POST'])
def SignIn():
    if 'user' in session:
        session.clear()
        flash("Vous avez été déconnecté en quittant la partie.", "info")
    if request.method == 'POST':  # post methode
        name_user = request.form['nom']
        pswd_user = request.form['password']
        if name_user == '' or pswd_user == '':
            flash("Merci de remplir les champs", "error")
        elif is_user_used(name_user) :
            flash("le pseudo est déjà utilisé", "error")
        elif not is_pwd_ok(pswd_user) :
            flash("le mot de passe doit faire minimu 6 charcatere avec un chiffre et une majuscule", "error")
        else :
            add_user(name_user, pswd_user)
            session['user'] = name_user
            return redirect(url_for('game'))
    return render_template('SignIn.html')
@app.route('/game', methods=['POST', 'GET'])
def game():
    if 'user' not in session:
        flash("Veuillez vous connecter pour jouer.", "error")
        return redirect(url_for('login'))

    if 'grid' not in session and 'pos_creature' not in session:
        grid, wumpus = GenerateGrid('medium')
        start = GetStartCharacter(grid, 'player')
        pos_creature = {"player" :start,
                    "wumpus" :wumpus}
        bats = GetBat('medium', grid, pos_creature)
        pos_creature["bats"] = bats

        session['pos_creature'] = pos_creature
        session['grid'] = grid
    else :
        pos_creature = session['pos_creature']
        grid = session['grid']

    return render_template('game.html', grid=grid, pos_creature=pos_creature)

if __name__ == '__main__':
    app.run(debug=False) # mettre en false a la fin