from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Gameshop, Base, Game, User
 
engine = create_engine('sqlite:///gameshopwusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
session = DBSession()

#Fake user creation
user1 = User(name="Example User", email="euser@ema.il", picture='https://upload.wikimedia.org/wikipedia/commons/d/d3/User_Circle.png')
session.add(user1)
session.commit()


#List of games for Best Games
gameshop1 = Gameshop(user_id=1, name = "Best Games")

session.add(gameshop1)
session.commit()


game1 = Game(user_id=1, name = "Kill'em all", description = "Shoot all the enemies", price = "$2.99", genre = "Action", gameshop = gameshop1)

session.add(game1)
session.commit()

game2 = Game(user_id=1, name = "Lost in an island", description = "Survivive after a shipwreck", price = "$3.99", genre = "Survival", gameshop = gameshop1)

session.add(game2)
session.commit()

game3 = Game(user_id=1, name = "Beware of dragons", description = "Fantasy adventures in a mystic land", price = "$3.99", genre = "RPG", gameshop = gameshop1)

session.add(game3)
session.commit()

game4 = Game(user_id=1, name = "Faster", description = "Win all the races", price = "$5.99", genre = "Simulator", gameshop = gameshop1)

session.add(game4)
session.commit()

game5 = Game(user_id=1, name = "Jump over!", description = "Jump over the pits and traps", price = "$1.99", genre = "Platform", gameshop = gameshop1)

session.add(game5)
session.commit()



#List of games for Awsome Games
gameshop1 = Gameshop(user_id=1, name = "Awesome Games")

session.add(gameshop1)
session.commit()


game1 = Game(user_id=1, name = "Bouncing Ball", description = "Bounce and bounce", price = "$2.99", genre = "Platform", gameshop = gameshop1)

session.add(game1)
session.commit()

game2 = Game(user_id=1, name = "The lost scroll", description = "Find the lost ancient scroll of knowledge", price = "$4.99", genre = "RPG", gameshop = gameshop1)

session.add(game2)
session.commit()

game3 = Game(user_id=1, name = "Crazy fishing", description = "Catch crazy fishes", price = "$3,99", genre = "Simulator", gameshop = gameshop1)

session.add(game3)
session.commit()

game4 = Game(user_id=1, name = "Chinese food tycoon ", description = "Manage your restaurant", price = "4.99", genre = "Simulator", gameshop = gameshop1)

session.add(game4)
session.commit()




#List of games for Cool Games
gameshop1 = Gameshop(user_id=1, name = "Cool Games")

session.add(gameshop1)
session.commit()


game1 = Game(user_id=1, name = "Legs of fury", description = "Fight against the evil ninjas", price = "$2.99", genre = "Action", gameshop = gameshop1)

session.add(game1)
session.commit()

game2 = Game(user_id=1, name = "Fast chase", description = "Chase the criminals with your polica car", price = "$3.99", genre = "Simulator", gameshop = gameshop1)

session.add(game2)
session.commit()

game3 = Game(user_id=1, name = "Flying Aces", description = "Dogfight with various airplanes", price = "$4.99", genre = "Simulator", gameshop = gameshop1)

session.add(game3)
session.commit()

game4 = Game(user_id=1, name = "Under 30 minutes", description = "Deliver pizza to customers as fast you can", price = "$3.99", genre = "Simulator", gameshop = gameshop1)

session.add(game4)
session.commit()



#List of games for Gamers Paradise
gameshop1 = Gameshop(user_id=1, name = "Gamers Paradise")

session.add(gameshop1)
session.commit()


game1 = Game(user_id=1, name = "Long vehicle", description = "Transport goods with truck", price = "$5.99", genre = "Simulator", gameshop = gameshop1)

session.add(game1)
session.commit()

game2 = Game(user_id=1, name = "Dungeon explorer", description = "Explore dungeons and loot treasurechests", price = "$4.99", genre = "RPG", gameshop = gameshop1)

session.add(game2)
session.commit()

game3 = Game(user_id=1, name = "Shawn's revenge", description = "Take revenge for your friends", price = "$4.99", genre = "Action", gameshop = gameshop1)

session.add(game3)
session.commit()

game4 = Game(user_id=1, name = "The exiled hero", description = "You are exiled to an island. Survive!", price = "$5.99", genre = "Survival", gameshop = gameshop1)

session.add(game4)
session.commit()


print "Games added!"

