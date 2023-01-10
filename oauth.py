from flask import Blueprint, redirect, session, request

from key.kakao_key import CLIENT_ID, REDIRECT_URI, LOGOUT_REDIRECT_URI

kakao = Blueprint('kakao', __name__, url_prefix='/kakao')


@kakao.route('/login')
def kakao_login():
    kakao_oauth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    return redirect(kakao_oauth_url)


@kakao.route('/callback')
def callback():
    print(request)
    code = request.args["code"]
    print(code)

    return redirect(LOGOUT_REDIRECT_URI)


@kakao.route('/logout')
def kakao_logout():
    kakao_oauth_url = f"https://kauth.kakao.com/oauth/logout?client_id={CLIENT_ID}&logout_redirect_uri={LOGOUT_REDIRECT_URI}"

    if session.get('email'):
        session.clear()
        value = {"status": 200, "result": "success"}
    else:
        value = {"status": 404, "result": "fail"}

    print('[Logout]', value)
    return redirect(kakao_oauth_url)
