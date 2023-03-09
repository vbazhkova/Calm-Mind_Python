import time
from mongoengine import *
from flask import Flask, request
from flask_ngrok import run_with_ngrok
from datetime import datetime
import numpy as np # работа с векторами
import matplotlib.pyplot as plt # рисовать графики
import pandas as pd
from prompt_toolkit import HTML # для работы с матрицами
import sklearn # машинное обучение на python
import csv
import os
from sklearn.decomposition import TruncatedSVD
import requests
import jinja2 
from random import random, randint

### Setup

app = Flask("LERAAPP")
run_with_ngrok(app)   

con = connect(host="mongodb+srv://cluster0.oqiy1.mongodb.net",
                 username = "hcistudents",
                 password="2sRC61jSojJ5KG62",
                 db = "valeriia_baz_db")

### Models
   
class User(DynamicDocument):
    userId: IntField(required=True)
    name: StringField()
    email: StringField()
    login: StringField()
    dateReg: DateField()
    launchTime: FloatField()
    
class UserPassword(DynamicDocument):
    userId: IntField(required=True)
    password: StringField()
    login: StringField()
    
class CategoryTypes(DynamicDocument):
    type: StringField()
    typeId: IntField()

class Product(DynamicDocument):
    prod_id: IntField()
    prod_name: StringField()   
    categoryType: IntField() 
    techniques: ListField(StringField())
    
class Rating(DynamicDocument):
    tech_id: IntField()
    rating: FloatField()       
    
class Statistics(DynamicDocument):
    user_id: IntField()
    calm_mins: IntField()
    ratings: ListField(Rating)
    
class UserDayMood(DynamicDocument):
    user_id: IntField()
    date: DateField()  
    mood: IntField()  
    
class Techniques(DynamicDocument):
    name: StringField()
    description: StringField()
    effect: StringField()
    example: StringField()  
    tech_id: IntField() 
    
collections=con['valeriia_baz_db'].list_collection_names()
for collection in collections:
   print(collection)    
    
### API Methods     

# Register new user
@app.route("/register", methods=['POST'])
def register():
    # Generate user_id
    userId = generateUserId()
    while isUserExists(userId) == True:
        userId = generateUserId()
        
    # Creating models to be written to the database    
    newUser = User(name = request.form.get("name"),
                   email = request.form.get("email"),
                   login = request.form.get("login"),
                   dateReg = datetime.now(),
                   userId = userId
                   )
    pasUser = UserPassword(userId = userId,
                           password = request.form.get("password"),
                           login = request.form.get("login")
                           )
    statistics = Statistics(user_id = userId,
                            calm_mins = 0,
                            ratings = []
                            )
    
    newUser.save()
    pasUser.save()
    statistics.save()
    
    return {
        "title" : "Success registration",
        "userId" : userId
    }

# Check if the user exists    
def isUserExists(userId):
    isExists = False
    for item in UserPassword.objects:
        if item.userId == userId:
            isExists = True
            return isExists 
        else:
            isExists = False
    return isExists        
    
def generateUserId():
    return randint(1, 1_000_000)    

# Log in and get the user's data
@app.route("/login", methods=['POST'])
def login():
    # At the login we get a username and password
    login = request.form.get("login")
    password = request.form.get("password")
    
    response = {}
    userId = 0
    
    # Find a user in the database
    for item in UserPassword.objects:
        if item.login == login and item.password == password:
            userId = item.userId
            for user in User.objects:
                if user.userId == userId:
                    response = {
                        "userId" : user.userId,
                        "name" : user.name,
                        "email" : user.email
                        }
    
    # Returning the answer
    if response != {}:
        launchTime = time.time()
        User.objects(userId=userId).update_one(set__launchTime = launchTime)
        return response
    else:
        return "Wrong login or password. Please, try again"
    
# Recover password
@app.route("/reset/password", methods=['POST'])
def resetPassword():
    # You can enter your login or email to recover your password
    email = request.form.get("email")
    login = request.form.get("login")
    
    emailToSend = None
    
    # Find out if there is a login or password in the database
    if email != None:
        for user in User.objects:
            if user.email == email:
                emailToSend = email 
                break
    elif login != None:
        for user in User.objects:
            if user.login == login:
                emailToSend = user.email 
                break
    
    if emailToSend != None:
        return sendEmail(emailToSend)
    else:
        return "The user with the specified username/password does not exist"

# Send a link to recover your password    
def sendEmail(email):
    return "Email send!"
                
### 1 Screen    
# Getting data for the activity screen
@app.route('/activities', methods=['GET'])
def sendActivities():
    # Retrieve product categories and products from the database
    categoryTypes = CategoryTypes.objects
    products = Product.objects   
    
    response = {}
    response["categoryTypes"] = []
    
    # Cycle to find all activities and return them for display
    for type in categoryTypes:
        categoriesOfType = []
        
        for prod in products:
            if prod.categoryType == type.typeId:
                categoriesOfType.append({
                    "name" : prod.prod_name,
                    "categoryId" : prod.prod_id
                })
        
        resp = {
            "typeId" : type.typeId,
            "type" : type.type,
            "categories" : categoriesOfType
        }
        response["categoryTypes"].append(resp)    
 
    return response                     
    
# We get the data for switching to any of the possible activities
@app.route('/activities/types', methods=['POST']) 
def getAndSendActivity():
    # For input we expect category, user id and product id
    categoryType = request.form.get("categoryType")
    prodId = request.form.get("prod_id")
    
    productToReturn = None
    techniques = []
    
    # Find the selected activity in the database and return it
    products = Product.objects 
    for prod in products:
        if prod.prod_id == int(prodId) and prod.categoryType == int(categoryType):
            productToReturn = Product()
            productToReturn.prod_id = prod.prod_id
            productToReturn.prod_name = prod.prod_name
            productToReturn.categoryType = prod.categoryType
            techniques = prod.techniques
            
    productTechs = {}
    for tech in techniques:
        for item in Techniques.objects:
            if item.name == tech:
                productTechs[tech] = item.to_json()                            
    
    # Check that we found the activity and return it  
    if productToReturn != None:
        # If the name of the product matches the prepared ones, then we add variants of interaction with the service, otherwise, we return the stub
        match productToReturn.prod_name:
            case "Pomodoro":
                return {
                    "product" : productToReturn.to_json(),
                    "techniques" : productTechs
                }
            case "Mnemonics":
                return {
                    "product" : productToReturn.to_json(),
                    "techniques" : productTechs
                }
            case "Breathe focus":
                return {
                    "product" : productToReturn.to_json(),
                    "techniques" : productTechs
                }
            case "Activities":
                return {
                    "product" : productToReturn.to_json(),
                    "techniques" : productTechs
                }   
            case default:
                return {
                    "title" : "Section is in progress",
                    "product" : productToReturn.to_json()
                }
    else:
        return "None"   

# Find the activity rating 
def findRatingForActivity(techId, userId):
    ratings = []
    for item in Statistics.objects:
        if item.user_id == int(userId):
            ratings = item.ratings
            break
    
    # Matching techId        
    result = 0
    for rate in ratings:
        if rate['tech_id'] == int(techId):
           result = rate['rating']
           break
    
    return result       

# Launch a technique and get a user rating for it
@app.route('/activities/techniques/start', methods=['GET'])
def startTechnic():
    # To enter, expect a technique id
    techId = request.args.get("tech_id")
    userId = request.args.get("user_id")
    technic = {}

    # Find a technique in the database
    for item in Techniques.objects:
        if int(techId) ==  item.tech_id:
            technic = item.to_json()
            break
        
    return {
        'technic' : technic,
        'rating' : findRatingForActivity(techId, userId)
    }
    
# Evaluating activity techniques
@app.route('/activities/techniques/rate', methods=['POST'])
def rateTechic():
    # For input we expect tech_id, user_id and new rating
    techId = request.form.get("tech_id")
    userId = request.form.get("user_id")
    rate = request.form.get("rating")
    
    statItem = {}
    ratings = []
    
    # Find user ratings
    for item in Statistics.objects:
        if item.user_id == int(userId):
            ratings = item.ratings
            break
    
    # Find an estimate of the technique, if it already exists
    selectedTechRating = 0
    for item in ratings:
        if item['tech_id'] == int(techId):
           selectedTechRating = item['rating']
           statItem = item
           break
    
    # Creating a new rating model
    newRating = {
        'rating' : int(rate),
        'tech_id' : int(techId)
    }
    
    # If there has been no assessment of a technique, we add a new one, otherwise we overwrite the old one
    userId = int(userId)
    if selectedTechRating == 0:
        Statistics.objects(user_id=userId).update_one(push__ratings = newRating)
        return "New rating was added"
    else:
        Statistics.objects(user_id=userId).update_one(pull__ratings = statItem)
        Statistics.objects(user_id=userId).update_one(push__ratings = newRating)
        return "Your old rating was overwriten"
    
### 2 Screen
# Get the username of the user (in fact, we already returned it during login, but in case the programmers need the data again)
@app.route('/user', methods=['GET']) 
def sendUser():
    response = {}
    # We expect a user id for input
    userId = request.args.get("user_id")
    
    # Find the user and bring him back
    for user in User.objects:
        if str(user.userId) == userId:
            response = {
                "userId" : user.userId,      
                "name" : user.name,
                "email" : user.email
                }
    
    if response != {}:
        return response         
    else: 
        return "User not found"

# Getting the tip of the day from a third-party API
@app.route('/advice', methods=['GET']) 
def getAndSendAdvice():
    advice = requests.get('https://api.adviceslip.com/advice')
    return advice.json()['slip']['advice']

# The user rates his current mood on a scale of 1-5 using emoji, where 1 is very bad and 5 is very good
@app.route('/recieve/currentMood', methods=['POST']) 
def setCurrentMood():
    userId = request.form.get("user_id")
    mood = request.form.get("mood")
    
    currentMood = UserDayMood()
    currentMood.user_id = userId
    currentMood.date = datetime.now()
    currentMood.mood = mood
    
    currentMood.save()
    
    return "Mood successfully recorded!"

# Create a prod.csv file for the dataset like recomendation.csv
def createProdsDF():
    if(os.path.exists('prod.csv') and os.path.isfile('prod.csv')):
        os.remove('prod.csv')
        
    filecsv = open('prod.csv', 'a+')
    writer = csv.writer(filecsv)
    header = ["productId", "name", "desc"]
    writer.writerow(header)
    
    fullData = []
    for item in Techniques.objects:
        smallData = []
        smallData.append(item.tech_id)
        smallData.append(item.name)
        if item.description != None:
            smallData.append(item.description)
        else:
            smallData.append("")
        fullData.append(smallData)
        
    writer.writerows(fullData)
    
    return filecsv

# Get a list of recommendations based on user feedback
@app.route('/recomendations', methods=['GET']) 
def getRecomendations():
    # We expect userId as an input
    userId = request.args.get("user_id")
    
    # Create a recomendation.csv file for the dataset
    file = 'recomendation.csv'
    # Delete the old one if it was already created earlier
    if(os.path.exists(file) and os.path.isfile(file)):
        os.remove(file)
    
    # Open the file and fill in the table header
    filecsv = open(file, 'a+')
    writer = csv.writer(filecsv)
    header = ["userId", "productId", "rating"]
    writer.writerow(header)
    
    statRatings = []
    ids = []
    
    # Find the data from the table with statistics
    for item in Statistics.objects:
        statRatings.append(item.ratings)
        ids.append(item.user_id)  
        # Return a message telling us to leave more ratings so that we can create a selection for the user
        if int(userId) == item.user_id and len(item.ratings) < 11:
            print(userId, item.user_id)
            return "Please, set more ratings for techniques to allow us make recommendations to you"    

    # Finding activity ratings
    techIds = []
    ratingsValues = []
    userIds = []  
    for index, item in enumerate(statRatings):  
        for i in item:
            techIds.append(i['tech_id']) 
            ratingsValues.append(i['rating'])
            userIds.append(ids[index])  
    
    fullData = []
    
    # Filling data for the dataset
    for index, item in enumerate(techIds):
        smallData = []
        smallData.append(userIds[index])
        smallData.append(item)
        smallData.append(ratingsValues[index])
        fullData.append(smallData)
    
    # Writing data to a file 
    writer.writerows(fullData)
    
    # Create a second dataset
    prodcsv = createProdsDF() 
    
    # After changes in datasets we prepare them for work
    filecsv.seek(0)
    prodcsv.seek(0)
    
    # Loading datasets
    prod = pd.read_csv(prodcsv)
    rat = pd.read_csv(filecsv)

    # Making copies
    recProd = prod.copy(deep=True)
    recRat = rat.copy(deep=True)
    
    # Combine into one table
    user_prod = pd.merge(recRat, recProd, on = "productId")
    
    idUser = int(userId)
    user_prod.drop (user_prod[user_prod.userId != idUser].index, inplace=True)
    
    user_prod.drop('userId', inplace=True, axis=1)
    user_prod.drop('desc', inplace=True, axis=1)
    
    other_users = recRat[recRat['productId'].isin(user_prod['productId'].values)]
    
    users_mutual_prod = other_users.groupby(['userId'])
    
    from scipy.stats import pearsonr

    pearson_corr = {}

    for userId, prod in users_mutual_prod:
        prod = prod.sort_values(by='productId')
        prod_list = prod['productId'].values

        user_prod_ratings = user_prod[user_prod['productId'].isin(prod_list)]['rating'].values 
        user_ratings = prod[prod['productId'].isin(prod_list)]['rating'].values

        corr = pearsonr(user_prod_ratings, user_ratings)
        pearson_corr[int(userId)] = corr[0]
    
    pearson = pd.DataFrame(columns=['userId', 'similarity_index'], data=pearson_corr.items())
    
    users_rating = pearson.merge(recRat, on='userId')
    users_rating['weighted_rating'] = users_rating['rating'] * users_rating['similarity_index']
    
    grouped_ratings = users_rating.groupby('productId').sum()[['similarity_index', 'weighted_rating']]
    
    recommend_prod = pd.DataFrame()

    recommend_prod['avg_reccomend_score'] = grouped_ratings['weighted_rating']/grouped_ratings['similarity_index']
    recommend_prod['productId'] = grouped_ratings.index
    recommend_prod = recommend_prod.reset_index(drop=True)

    recommend_prod = recommend_prod[(recommend_prod['avg_reccomend_score'] > 3)]

    recommendation = recProd[recProd['productId'].isin(recommend_prod['productId'])][['productId']].sample(5)
    
    print(recommendation)
    recProdsIds = []
    
    for index, row in recommendation.iterrows():  
        recProdsIds.append(row['productId'])
    
    response = []
    
    for item in recProdsIds:
        response.append(Techniques.objects(tech_id=int(item)).to_json())
        
    return response

### 3 Screen
# Get user statistics, display html page with jinja2
@app.route('/user/statistics', methods=['GET']) 
def sendStatistics():
    response = {}
    # We expect a user id for input
    userId = request.args.get("user_id")
    
    # Find the data from the table with statistics
    for item in Statistics.objects:
        if item.user_id == int(userId):
            response = {
            "user_id" : item.user_id,
            "calm_mins" : item.calm_mins
            }
            
    # Find user data
    userModel = {}
    for user in User.objects:
        if str(user.userId) == userId:
            userModel = {
                "userId" : user.userId,      
                "name" : user.name,
                "email" : user.email,
                "dateReg" : user.dateReg,
                "login" : user.login
                }

    # Creating the final JSON to display on the page
    if response != {}:        
        modelEx = {'name':  userModel['name'], 
                   'email': userModel['email'],
                   'calm_mins' : response['calm_mins'],
                   'dateReg' : userModel['dateReg'],
                   'login' : userModel['login']
                    }
        # Drawing the page
        j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'),trim_blocks=True)
        return j2_env.get_template('userInfo.html').render(modelEx)
  
    else: 
        return "User not found"

# Getting user ratings
@app.route('/user/ratings', methods=['GET'])
def sendRatings():
    # We expect a user id for input
    userId = request.args.get("user_id")
    
    statRatings = {}
    
    # Find the data from the table with statistics
    for item in Statistics.objects:
        if item.user_id == int(userId):
            statRatings = {
            "ratings" : item.ratings
            }

    # Finding activity ratings
    techIds = []
    ratingsValues = []  
    for item in statRatings['ratings']:  
        techIds.append(item['tech_id']) 
        ratingsValues.append(item['rating'])  
    
    # Use the id of the ratings to find their names
    ratings = []
    for item in Techniques.objects:
        if item.tech_id in techIds:
            idx = techIds.index(item.tech_id)
            rating = {
                "name" : item.name,
                "rating" : ratingsValues[idx]
            }
            ratings.append(rating)
    
    response = {
        'ratings' : ratings
    }
    
    return response
    
# When closing the app
@app.route('/end', methods=['GET'])
def onEnd():
    # We expect a user id for input
    userId = request.args.get("user_id")
    calmMins = 0
    launchTime = 0
    
    for item in Statistics.objects:
        if item.user_id == int(userId):
            calmMins = item.calm_mins
            break
    
    for user in User.objects:
        if user.userId == int(userId):
            launchTime = user.launchTime
            break
                    
    endTime = time.time()
    totalInApp = endTime - launchTime
    calmMins = calmMins + totalInApp / 60
    Statistics.objects(user_id=int(userId)).update_one(set__calm_mins = int(calmMins))
    
    return "Success"
    
app.run()
