from flask import Blueprint, request

from key.file_path import USER_CLOTHES_DIR

clothes = Blueprint('clothes', __name__, url_prefix='/clothes')


@clothes.route('/list', methods=['GET'])
def get_clothes_list():
    from model import MyClothes

    user_id = request.args['user_id']

    user_clothes = MyClothes.query.filter(MyClothes.is_user_img == 1).filter(MyClothes.user_id == user_id).all()
    recommend_clothes = MyClothes.query.filter(MyClothes.is_user_img == 0).filter(MyClothes.user_id == user_id).all()

    return {'user_id': user_id,
            'user_clothes': [i.as_dict() for i in user_clothes],
            'recommend_clothes': [i.as_dict() for i in recommend_clothes]}


@clothes.route('/upload', methods=['POST'])
def upload_user_clothes():
    import os

    if request.method == 'POST':
        user_id = request.values['user_id']
        gender = request.values['gender']
        file = request.files['file']
        print(file)

        if len(file.filename) == 0:
            return {'message': 'No File Uploaded!'}, 400

        dirname = os.path.join(USER_CLOTHES_DIR, user_id)
        os.makedirs(dirname, exist_ok=True)
        num = 1
        filename = user_id + '_' + str(num) + '.jpg'
        while os.path.exists(os.path.join(dirname, filename)):
            num += 1
            filename = user_id + '_' + str(num) + '.jpg'

        file.save(os.path.join(dirname, filename))

        ########## openpose ##########
        from models.openpose import run as op
        op.get_keypoints(os.path.join(dirname, filename))

        ########## human parsing ##########
        from models.human_parsing import run as hp
        origin_img_path = os.path.join(dirname, filename)
        output_img_path = os.path.join(dirname, user_id + '_' + str(num) + '.png')
        hp.human_parsing(origin_img_path, output_img_path)

        ########## clothes classification ##########
        from models.efficientnet.run import efficientnet

        # 밖으로 빼고싶은거 (app.py에 적재시 코드 제거 또는 주석)
        from models.efficientnet.load_model import Load_Model
        lm = Load_Model()
        male_model, female_model = lm.set_model()

        ## 받아오는거 : 성별 / 사진이 저장되어있는 경로
        ## 나갈꺼 사진의 계절
        clothes_path = origin_img_path

        ### 옷 분류 모델 실행 ###
        cla = ""
        if gender == "male":
            # male model
            clm = efficientnet(male_model)
        else:
            # female model
            clm = efficientnet(female_model)

        cla = clm.run(clothes_path)

        return {'message': 'Image Uploaded!',
                'user_id': user_id,
                'img_path': dirname + '/' + filename,
                'season': cla}


@clothes.route('/upload/save', methods=['GET'])
def save_user_clothes():
    ########## Update DB ##########
    import app
    db = app.db
    from model import MyClothes

    user_id = request.args['user_id']
    origin_img_path = request.args['img_path']
    season = request.args['season']
    is_user_img = True

    my_clothes = MyClothes(user_id=user_id,
                           origin_img_path=origin_img_path,
                           season=season,
                           is_user_img=is_user_img)
    db.session.add(my_clothes)
    db.session.commit()
    db.session.flush()
    db.session.remove()

    return {'message': 'Clothes Saved!',
            'user_id': user_id}










# @clothes.route('openpose', methods=['GET'])
# def openpose():
#     from models.openpose import run
#     run.get_keypoints('/data/seeot-server/models/test_input_01.jpg')
#     return {'message': 'OPENPOSE SUCCESS!'}

# @clothes.route('human_parsing', methods=['GET'])
# def human_parsing():
#     from models.human_parsing import run
#     origin_img_path = 'models/img_ppt.jpg'
#     output_img_path = 'models/temp/img_ppt_full.png'
#     result = run.human_parsing(origin_img_path, output_img_path)
#     return {'message': 'HUMAN_PARSING SUCCESS!', 'result': result}

# @clothes.route('/cc', methods=['GET'])
# def Classification():
#     ### 필요한 모듈 임포트 ###
#     from models.efficientnet.run import efficientnet

#     # 밖으로 빼고싶은거 (app.py에 적재시 코드 제거 또는 주석)
#     from models.efficientnet.load_model import Load_Model
#     lm = Load_Model()
#     male_model, female_model = lm.set_model()

#     ## 받아오는거 : 성별 / 사진이 저장되어있는 경로

#     ## 나갈꺼 사진의 계절
# #     clothes_path = request.args['clothes_url']
# #     gender = request.args["gender"]
#     gender = "female"

#     ### 옷 분류 모델 실행 ###
#     cla = ""
#     if gender == "male":
#         # male model
#         clm = efficientnet(male_model)
# #         cla = clm.run(clothes_path)
#         cla = clm.run()
#     else:
#         # female model
#         clm = efficientnet(female_model)
# #         cla = clm.run(clothes_path)
#         cla = clm.run()

#     return cla
