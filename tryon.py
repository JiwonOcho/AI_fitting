from flask import Blueprint, request

tryon = Blueprint('tryon', __name__, url_prefix='/tryon')


@tryon.route('/', methods=['GET'])
def try_on():
    from model import User, MyClothes
    import shutil
    import os
    from models.dior import run

    print('Try On START!!!')

    user_id = request.args['user_id']
    top = request.args['top']
    bottom = request.args['bottom']


    # DB 조회
    # 원본이미지, 파싱이미지 복사

    user = User.query.filter(User.id == user_id).first()
    if user is None:
        return {'message': 'Authentication Failed!'}, 401

    # 상의, 하의 모두 선택하지 않은 경우
    if top == '-1' and bottom == '-1':
        return {'message': 'No Clothes Selected!',
                'output_img': 'http://210.106.99.80:5050/' + user.full_body_img_path}

    img_folder = 'models/dior/DATA_ROOT/test/'
    img_lip_folder = 'models/dior/DATA_ROOT/testM_lip/'

    user_filename = user_id + '.jpg'
    shutil.copy('static/user_fullbody/' + user_filename, img_folder + user_filename)
    shutil.copy('static/user_fullbody/' + user_id + '.png', img_lip_folder + user_id + '.png')


    if top != '-1':
        top_clothes = MyClothes.query.filter(MyClothes.id == top).first()
        
        if top_clothes is None:
            return {'message': 'No Such Clothes!'}, 400
        
        top_filename = top_clothes.origin_img_path.split('/')[-1]
        shutil.copy(top_clothes.origin_img_path, img_folder + top_filename)
        shutil.copy(top_clothes.origin_img_path.split('.')[0] + '.png', img_lip_folder + top_filename.split('.')[0] + '.png')

    if bottom != '-1':
        bottom_clothes = MyClothes.query.filter(MyClothes.id == bottom).first()

        if bottom_clothes is None:
            return {'message': 'No Such Clothes!'}, 400
    
        bottom_filename = bottom_clothes.origin_img_path.split('/')[-1]
        shutil.copy(bottom_clothes.origin_img_path, img_folder + bottom_filename)
        shutil.copy(bottom_clothes.origin_img_path.split('.')[0] + '.png', img_lip_folder + bottom_filename.split('.')[0] + '.png')
    


    # 문서에 저장
    with open('/data/seeot-server/models/dior/DATA_ROOT/standard_test_anns.txt', "a") as f:
        f.write('plain, ' + user_filename + '\n')
        if top != '-1':
            f.write('plain, ' + top_filename + '\n')
        if bottom != '-1':
            f.write('plain, ' + bottom_filename + '\n')


    # output/ 폴더 내 이미지 삭제
    if os.path.exists('static/output'):
        for file in os.scandir('static/output'):
            if os.path.isfile(file.path):
                os.remove(file.path)


    # 모델 실행
    run.load_data()

    if top == '-1':
        top_idx = -1
        if bottom == '-1':
            bottom_idx = -1
        else:
            bottom_idx = 1
    else:
        top_idx = 1
        if bottom == '-1':
            bottom_idx = -1
        else:
            bottom_idx = 2

    run.try_on(0, top_idx, bottom_idx, -1)
    print(top_idx, bottom_idx)


    # test/, testM_lip/ 이미지 삭제
    if os.path.exists(img_folder):
        for file in os.scandir(img_folder):
            if os.path.isfile(file.path):
                os.remove(file.path)
    
    if os.path.exists(img_lip_folder):
        for file in os.scandir(img_lip_folder):
            if os.path.isfile(file.path):
                os.remove(file.path)


    # os.remove(img_folder + user_filename)
    # os.remove(img_lip_folder + user_filename.split('.')[0] + '.png')

    cnt = 1
    if top != '-1':
        # os.remove(img_folder + top_filename)
        # os.remove(img_lip_folder + top_filename.split('.')[0] + '.png')
        cnt += 1

    if bottom != '-1':
        # os.remove(img_folder + bottom_filename)
        # os.remove(img_lip_folder + bottom_filename.split('.')[0] + '.png')
        cnt += 1


    # standard_test_anns.txt 이미지 리스트 삭제
    with open('/data/seeot-server/models/dior/DATA_ROOT/standard_test_anns.txt', "r") as f:
        lines = f.readlines()

    with open('/data/seeot-server/models/dior/DATA_ROOT/standard_test_anns.txt', "w") as f:
        f.writelines(lines[:-cnt])
        

    # 결과 이미지 복사
    ## 랜덤값 뒤에 붙이기
    import string
    import random

    result = ""
    for i in range(4):
        result += random.choice(string.ascii_lowercase)


    output_path = 'static/output/output_' + result + '.png'
    shutil.copy('static/output/output.png', output_path)


    return {'output_img': 'http://210.106.99.80:5050/' + output_path}

