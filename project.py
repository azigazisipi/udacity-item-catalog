from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Gameshop, Game, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Gameshop"


# Connect to Database and create database session
engine = create_engine('sqlite:///gameshopwusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# DISCONNECT - Revoke a current user's token and reset login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['email']
        del login_session['username']

        flash('Successfully Logged out.')
        return redirect(url_for('showGameshops'))
    else:
        # If token is invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Gameshop Information
@app.route('/gameshop/<int:gameshop_id>/list/JSON')
def gameshopListJSON(gameshop_id):
    gameshop = session.query(Gameshop).filter_by(id=gameshop_id).one()
    games = session.query(Game).filter_by(
        gameshop_id=gameshop_id).all()
    return jsonify(Games=[i.serialize for i in games])


@app.route('/gameshop/<int:gameshop_id>/list/<int:game_id>/JSON')
def gameJSON(gameshop_id, game_id):
    List_Item = session.query(Game).filter_by(id=game_id).one()
    return jsonify(List_Item=List_Item.serialize)


@app.route('/gameshop/JSON')
def gameshopsJSON():
    gameshops = session.query(Gameshop).all()
    return jsonify(gameshops=[r.serialize for r in gameshops])


# Show all gameshops
@app.route('/')
@app.route('/gameshop/')
def showGameshops():
    gameshops = session.query(Gameshop).order_by(asc(Gameshop.name))
    if 'username' not in login_session:
        return render_template('publicgameshops.html', gameshops=gameshops)
    else:
        return render_template('gameshops.html', gameshops=gameshops)

# Create a new gameshop


@app.route('/gameshops/new/', methods=['GET', 'POST'])
def newGameshop():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGameshop = Gameshop(name=request.form[
            'name'], user_id=login_session['user_id'])
        session.add(newGameshop)
        flash('New Gameshop %s Successfully Created' % newGameshop.name)
        session.commit()
        return redirect(url_for('showGameshops'))
    else:
        return render_template('newgameshop.html')

# Edit a gameshop


@app.route('/gameshop/<int:gameshop_id>/edit/', methods=['GET', 'POST'])
def editGameshop(gameshop_id):
    editedGameshop = session.query(
        Gameshop).filter_by(id=gameshop_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedGameshop.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this gameshop. You can edit only your own gameshop!');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedGameshop.name = request.form['name']
            flash('Gameshop Successfully Edited %s' % editedGameshop.name)
            return redirect(url_for('showGameshops'))
    else:
        return render_template('editgameshop.html', gameshop=editedGameshop)


# Delete a gameshop
@app.route('/gameshop/<int:gameshop_id>/delete/', methods=['GET', 'POST'])
def deleteGameshop(gameshop_id):
    gameshopToDelete = session.query(
        Gameshop).filter_by(id=gameshop_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if gameshopToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this gameshop. You can delete only your own gameshop.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(gameshopToDelete)
        flash('%s Successfully Deleted' % gameshopToDelete.name)
        session.commit()
        return redirect(url_for('showGameshops', gameshop_id=gameshop_id))
    else:
        return render_template(
            'deletegameshop.html', gameshop=gameshopToDelete)

# Show a gameshop list


@app.route('/gameshop/<int:gameshop_id>/')
@app.route('/gameshop/<int:gameshop_id>/list/')
def showList(gameshop_id):
    gameshop = session.query(Gameshop).filter_by(id=gameshop_id).one()
    creator = getUserInfo(gameshop.user_id)
    items = session.query(Game).filter_by(
        gameshop_id=gameshop_id).all()
    if 'username' not in login_session or creator.id != login_session[
            'user_id']:
        return render_template(
            'publiclist.html', items=items, gameshop=gameshop, creator=creator)
    else:
        return render_template(
            'list.html', items=items, gameshop=gameshop, creator=creator)


# Create a new Game
@app.route('/gameshop/<int:gameshop_id>/list/new/', methods=['GET', 'POST'])
def newGame(gameshop_id):
    if 'username' not in login_session:
        return redirect('/login')
    gameshop = session.query(Gameshop).filter_by(id=gameshop_id).one()
    if login_session['user_id'] != gameshop.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add game to this gameshop. Youo can add games only your own gameshop!);}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        newGame = Game(name=request.form['name'], description=request.form[
            'description'], price=request.form['price'], genre=request.form[
                'genre'], gameshop_id=gameshop_id, user_id=gameshop.user_id)
        session.add(newGame)
        session.commit()
        flash('New Game %s Successfully Created' % (newGame.name))
        return redirect(url_for('showList', gameshop_id=gameshop_id))
    else:
        return render_template('newgame.html', gameshop_id=gameshop_id)

# Edit a game


@app.route('/gameshop/<int:gameshop_id>/list/<int:game_id>/edit', methods=[
    'GET', 'POST'])
def editGame(gameshop_id, game_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedGame = session.query(Game).filter_by(id=game_id).one()
    gameshop = session.query(Gameshop).filter_by(id=gameshop_id).one()
    if login_session['user_id'] != gameshop.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit a game. You can edit a game only in your own gameshop!');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedGame.name = request.form['name']
        if request.form['description']:
            editedGame.description = request.form['description']
        if request.form['price']:
            editedGame.price = request.form['price']
        if request.form['genre']:
            editedGame.genre = request.form['genre']
        session.add(editedGame)
        session.commit()
        flash('Game Successfully Edited')
        return redirect(url_for('showList', gameshop_id=gameshop_id))
    else:
        return render_template(
            'editgame.html',
            gameshopt_id=gameshop_id,
            game_id=game_id,
            game=editedGame)


# Delete a game
@app.route('/gameshop/<int:gameshop_id>/list/<int:game_id>/delete', methods=[
    'GET', 'POST'])
def deleteGame(gameshop_id, game_id):
    if 'username' not in login_session:
        return redirect('/login')
    gameshop = session.query(Gameshop).filter_by(id=gameshop_id).one()
    gameToDelete = session.query(Game).filter_by(id=game_id).one()
    if login_session['user_id'] != gameshop.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete this game. You can delete games only from your own gameshop!');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(gameToDelete)
        session.commit()
        flash('Game Successfully Deleted')
        return redirect(url_for('showList', gameshop_id=gameshop_id))
    else:
        return render_template('deletegame.html', game=gameToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5001, threaded=False)
