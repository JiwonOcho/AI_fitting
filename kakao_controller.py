import requests
from key.kakao_key import CLIENT_ID, REDIRECT_URI


class Oauth:
    def __init__(self):
        self.auth_server = "https://kauth.kakao.com%s"
        self.api_server = "https://kapi.kakao.com%s"
        self.default_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        }

    def auth(self, code):
        return requests.post(
            url=self.auth_server % "/oauth/token",
            headers=self.default_header,
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "code": code,
            },
        ).json()

    def userinfo(self, bearer_token):
        return requests.post(
            url=self.api_server % "/v2/user/me",
            headers={
                **self.default_header,
                **{"Authorization": bearer_token}
            },
            data={
                'property_keys': '["kakao_account.profile", "kakao_account.gender"]'
            }
        ).json()

    def token(self, refresh_token):
        return requests.post(
            url=self.auth_server % "/oauth/token",
            headers=self.default_header,
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID,
                "refresh_token": refresh_token
            }
        ).json()

    def logout(self, bearer_token):
        return requests.post(
            url=self.api_server % "/v1/user/logout",
            headers={
                **self.default_header,
                **{"Authorization": bearer_token}
            }
        ).json()
