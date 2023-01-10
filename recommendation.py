from flask import Blueprint, request

from key.file_path import USER_CLOTHES_DIR

recommendation = Blueprint('recommendation', __name__, url_prefix='/recommendation')


def forecast(date, cityName):
    import requests
    import json

    # API 불러오기
    response = requests.get(
        'http://api.weatherapi.com/v1/forecast.json?key=00dbb30dbbb6417aa4a12016221909&q=' + cityName +
        '&days=14&aqi=no&alerts=no' + '&lang=ko')
    
    jsonObj = json.loads(response.text)


    data = jsonObj['forecast']["forecastday"]
    target = data[0]
    for i in data:
        if i["date"] == date:
            target = i


    # 변수에 담기
    temp = target["day"]["avgtemp_c"]
    max_tem_searched = target["day"]["maxtemp_c"]
    min_tem_searched = target["day"]["mintemp_c"]
    text = target["day"]["condition"]["text"]

    return temp, text, max_tem_searched, min_tem_searched


def User_clothes(userId, temp):
    from model import MyClothes

    temper = temp
    
    if temper <= 8.9:
        weather_ = 'Winter'
    elif 9.0 <= temper <= 22.9:
        weather_ = 'Spring_fall'
    elif 23.0 <= temper:
        weather_ = 'Summer'

    return_list = []
    lists = MyClothes.query.filter(MyClothes.user_id == userId, MyClothes.season == weather_).with_entities(MyClothes.origin_img_path).all()
    
    for i in lists:
        return_list.append(i[0])

    return tuple(return_list)

def remove_list(rist):
    return_rist = []
    for i in rist:
        if i.split(".")[-1] == "jpg":
            return_rist.append(i)
    
    return return_rist
        

@recommendation.route('/', methods=['GET'])
def get_recommendations():
    from model import User
    import random
    import glob
    
    cityName = request.args['city']
    date = request.args['date']
    temp, text, max, min = forecast(date, cityName)
    
    user_id = request.args['user_id']
    user = User.query.filter(User.id == user_id).first()
    user_path = []

    if user is None:
        # return {'message': 'Authentication Failed!'}, 401
        gender = 'male'
    else:
        user_path = list(User_clothes(user_id, temp))
        gender = user.gender
        
    if temp <= 8.9:
        weather = 'Winter'
    elif 9.0 <= temp <= 22.9:
        weather = 'Spring_fall'
    elif 23.0 <= temp:
        weather = 'Summer'

    if gender == 'female':
        seeot_path = 'static/clothes/female'
    else:
        seeot_path = 'static/clothes/male'
    
    seeot_springfall_list = glob.glob(seeot_path + "/Spring_fall" + '/*')
    seeot_summer_list = glob.glob(seeot_path + "/Summer" + '/*')
    seeot_winter_list = glob.glob(seeot_path + "/Winter" + '/*')
    
    pics = []

    if weather == 'Spring_fall':
        if len(user_path) > 0:
            seeot_springfall_list.extend(list(user_path))
            seeot_springfall_list = remove_list(seeot_springfall_list)
            pics.append(random.sample(seeot_springfall_list,6))
        else:
            seeot_springfall_list = remove_list(seeot_springfall_list)
            pics.append(random.sample(seeot_springfall_list,6))

    elif weather == 'Summer':
        if len(user_path) > 0:
            seeot_summer_list.extend(list(user_path))
            seeot_springfall_list = remove_list(seeot_summer_list)
            pics.append(random.sample(seeot_summer_list,6))
        else:
            seeot_springfall_list = remove_list(seeot_summer_list)
            pics.append(random.sample(seeot_summer_list,6))

    elif weather == 'Winter':
        if len(user_path) > 0:
            seeot_winter_list.extend(list(user_path))
            seeot_springfall_list = remove_list(seeot_winter_list)
            pics.append(random.sample(seeot_winter_list,6))
        else:
            seeot_springfall_list = remove_list(seeot_winter_list)
            pics.append(random.sample(seeot_winter_list,6))
    
    return_pics = []
    for i in pics[0]:
        return_pics.append("http://210.106.99.80:5050/" + "/".join(i.split("\\")))

    return {'gender': gender,
            'clothes': return_pics,
            'season': weather,
            'forecast': text,
            'max_temp': max,
            'min_temp': min,
            'avg_temp': temp}


def get_recommendations_temp():
    from model import User
    import app
    db = app.db

    user_id = request.args['user_id']
    if user_id == 'null':
        gender = 'male'
    else:
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            return {'message': 'Authentication Failed!'}, 401
        gender = user.gender

    if gender == 'female':
        print('여자 옷 추천')
    else:
        print('male이거나 성별이 없으면 남자 옷 추천')

    return {'gender': gender,
            'clothes': ['http://210.106.99.80:5050/static/reco1.jpg',
                        'http://210.106.99.80:5050/static/reco2.jpg',
                        'http://210.106.99.80:5050/static/reco3.jpg']}


@recommendation.route('/save', methods=['GET'])
def save_recommendation():
    from model import MyClothes
    import app
    db = app.db

    user_id = request.args['user_id']
    img_path = request.args['img_path']
    img_path = img_path[img_path.find('static'):]
    season = request.args['season']

    # user_id 예외처리: 해당 user가 DB에 없는 경우
    # img_path 예외처리: 해당 파일이 없는 경우

    ### DB에 저장 ###
    clothes = MyClothes(user_id=user_id,
                        origin_img_path=img_path,
                        season=season,
                        is_user_img=0)
    db.session.add(clothes)
    db.session.commit()
    db.session.flush()
    db.session.remove()


    return {'message': 'Image Save Success!',
            'user_id': user_id,
            'file_path': img_path,
            'season': season}


@recommendation.route('/test', methods=['GET'])
def test():


    return '여기는 추천 api'