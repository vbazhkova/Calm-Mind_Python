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

# Регистриуем нового юзера
@app.route("/register", methods=['POST'])
def register():
    # Генерируем user_id
    userId = generateUserId()
    while isUserExists(userId) == True:
        userId = generateUserId()
        
    # Создаём модели для записи в БД    
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

# Проверяем существует ли пользователь    
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

# Авторизуемся и получаем данные юзера
@app.route("/login", methods=['POST'])
def login():
    # На входе поулчам логин и пароль
    login = request.form.get("login")
    password = request.form.get("password")
    
    response = {}
    userId = 0
    
    # Находим пользователя в БД
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
    
    # Возвращаем ответ
    if response != {}:
        launchTime = time.time()
        User.objects(userId=userId).update_one(set__launchTime = launchTime)
        return response
    else:
        return "Wrong login or password. Please, try again"
    
# Восстановить пароль
@app.route("/reset/password", methods=['POST'])
def resetPassword():
    # Для восстановления пароля можно ввести логин или почту
    email = request.form.get("email")
    login = request.form.get("login")
    
    emailToSend = None
    
    # Находим есть ли логин или пароль в БД
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

# Отправляем ссылку для восстановления пароля                
def sendEmail(email):
    return "Email send!"
                
### 1 ЭКРАН    
# Получаем данные для экрана активностей
@app.route('/activities', methods=['GET'])
def sendActivities():
    # Достаём из БД категории продуктов и продукты
    categoryTypes = CategoryTypes.objects
    products = Product.objects   
    
    response = {}
    response["categoryTypes"] = []
    
    # Циклом находим все активности и возвращаем их для отображения
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
    
# Получаем данные для перехода в любую из возможных активностей
@app.route('/activities/types', methods=['POST']) 
def getAndSendActivity():
    # На вход ожидаем категорию, id пользователя и id продукта
    categoryType = request.form.get("categoryType")
    prodId = request.form.get("prod_id")
    
    productToReturn = None
    techniques = []
    
    # Находим выбранную активность в БД и возвращаем её
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
    
    # Проверяем что нашли активность и возвращаем её    
    if productToReturn != None:
        # Если имя продукта сходится с заготовленными, то добавляем варинаты взаимодействия с сервисом, иначе, возвращаем заглушку
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

# Находим рейтинг активности 
def findRatingForActivity(techId, userId):
    ratings = []
    for item in Statistics.objects:
        if item.user_id == int(userId):
            ratings = item.ratings
            break
    
    # Сопоставляем techId        
    result = 0
    for rate in ratings:
        if rate['tech_id'] == int(techId):
           result = rate['rating']
           break
    
    return result       

# Запускаем технику и получаем для нее пользовaтельский рейтинг
@app.route('/activities/techniques/start', methods=['GET'])
def startTechnic():
    # На вход ожидаем id техники
    techId = request.args.get("tech_id")
    userId = request.args.get("user_id")
    technic = {}

    # Находим технику в БД
    for item in Techniques.objects:
        if int(techId) ==  item.tech_id:
            technic = item.to_json()
            break
        
    return {
        'technic' : technic,
        'rating' : findRatingForActivity(techId, userId)
    }
    
# Оцениваем технику активности
@app.route('/activities/techniques/rate', methods=['POST'])
def rateTechic():
    # На вход ожидаем tech_id, user_id и новый рейтинг
    techId = request.form.get("tech_id")
    userId = request.form.get("user_id")
    rate = request.form.get("rating")
    
    statItem = {}
    ratings = []
    
    # Находим рейтинги пользователя
    for item in Statistics.objects:
        if item.user_id == int(userId):
            ratings = item.ratings
            break
    
    # Находим оценку техники, если она уже есть
    selectedTechRating = 0
    for item in ratings:
        if item['tech_id'] == int(techId):
           selectedTechRating = item['rating']
           statItem = item
           break
    
    # Создаем новую модель рейтинга
    newRating = {
        'rating' : int(rate),
        'tech_id' : int(techId)
    }
    
    # Если оценки техники ещё не было, то добавляем новую, иначе перезаписываем старую
    userId = int(userId)
    if selectedTechRating == 0:
        Statistics.objects(user_id=userId).update_one(push__ratings = newRating)
        return "New rating was added"
    else:
        Statistics.objects(user_id=userId).update_one(pull__ratings = statItem)
        Statistics.objects(user_id=userId).update_one(push__ratings = newRating)
        return "Your old rating was overwriten"
    
### 2 ЭКРАН
# Получаем имя юзера (вообще мы его уже вернули при логине, но на случай если программистам снова понадобятся данные)
@app.route('/user', methods=['GET']) 
def sendUser():
    response = {}
    # На вход ожидаем user id
    userId = request.args.get("user_id")
    
    # Находим юзера и возвращаем его
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

# Получаем совет дня из стороннего API
@app.route('/advice', methods=['GET']) 
def getAndSendAdvice():
    advice = requests.get('https://api.adviceslip.com/advice')
    return advice.json()['slip']['advice']

# Пользователь оценивает своё текущее настроение по шкале 1-5 с помощью эмодзи, где 1 -- очень плохо, а 5 -- очень хорошо
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

# Создаём файл prod.csv для датасета аналогично recomendation.csv
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

# Получить список рекомендаций на основе отзывов пользователя
@app.route('/recomendations', methods=['GET']) 
def getRecomendations():
    # На вход ожидаем userId
    userId = request.args.get("user_id")
    
    # Создаём файл recomendation.csv для датасета
    file = 'recomendation.csv'
    # Удаляем старый если он уже был создан ранее
    if(os.path.exists(file) and os.path.isfile(file)):
        os.remove(file)
    
    # Открываем файл и заполняем хедер таблицы
    filecsv = open(file, 'a+')
    writer = csv.writer(filecsv)
    header = ["userId", "productId", "rating"]
    writer.writerow(header)
    
    statRatings = []
    ids = []
    
    # Находим данные из таблицы со статистикой
    for item in Statistics.objects:
        statRatings.append(item.ratings)
        ids.append(item.user_id)  
        # Возвращаем сообщение о необходимости оставить больше оценок, чтобы мы могли создать подборку для пользователя
        if int(userId) == item.user_id and len(item.ratings) < 11:
            print(userId, item.user_id)
            return "Please, set more ratings for techniques to allow us make recommendations to you"    

    # Находим рейтинги активностей
    techIds = []
    ratingsValues = []
    userIds = []  
    for index, item in enumerate(statRatings):  
        for i in item:
            techIds.append(i['tech_id']) 
            ratingsValues.append(i['rating'])
            userIds.append(ids[index])  
    
    fullData = []
    
    # Заполняем данные для датасета
    for index, item in enumerate(techIds):
        smallData = []
        smallData.append(userIds[index])
        smallData.append(item)
        smallData.append(ratingsValues[index])
        fullData.append(smallData)
    
    # Записываем данные в файл 
    writer.writerows(fullData)
    
    # Создаём второй датасет
    prodcsv = createProdsDF() 
    
    # После изменений в датасетах подготавливаем их к работе
    filecsv.seek(0)
    prodcsv.seek(0)
    
    # Загружаем датасеты
    prod = pd.read_csv(prodcsv)
    rat = pd.read_csv(filecsv)

    # Делаем копии
    recProd = prod.copy(deep=True)
    recRat = rat.copy(deep=True)
    
    # Объединяем в одну таблицу
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

### 3 ЭКРАН
# Получаем статистику пользователя, отображаем html страницу с помощью jinja2
@app.route('/user/statistics', methods=['GET']) 
def sendStatistics():
    response = {}
    # На вход ожидаем user id
    userId = request.args.get("user_id")
    
    # Находим данные из таблицы со статистикой
    for item in Statistics.objects:
        if item.user_id == int(userId):
            response = {
            "user_id" : item.user_id,
            "calm_mins" : item.calm_mins
            }
            
    # Нахоодим данные о пользователе
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

    # Собираем итоговый JSON для отображения на странице
    if response != {}:        
        modelEx = {'name':  userModel['name'], 
                   'email': userModel['email'],
                   'calm_mins' : response['calm_mins'],
                   'dateReg' : userModel['dateReg'],
                   'login' : userModel['login']
                    }
        # Отрисовываем страницу
        j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'),trim_blocks=True)
        return j2_env.get_template('userInfo.html').render(modelEx)
  
    else: 
        return "User not found"

# Получаем оценки пользователя
@app.route('/user/ratings', methods=['GET'])
def sendRatings():
    # На вход ожидаем user id
    userId = request.args.get("user_id")
    
    statRatings = {}
    
    # Находим данные из таблицы со статистикой
    for item in Statistics.objects:
        if item.user_id == int(userId):
            statRatings = {
            "ratings" : item.ratings
            }

    # Находим рейтинги активностей
    techIds = []
    ratingsValues = []  
    for item in statRatings['ratings']:  
        techIds.append(item['tech_id']) 
        ratingsValues.append(item['rating'])  
    
    # По id рейтинов находим их названия
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
    
# При закрытии приложения
@app.route('/end', methods=['GET'])
def onEnd():
    # На вход ожидаем user id
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