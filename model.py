import app

db = app.db


class User(db.Model):
    __tablename__ = 'SEEOT_USER'

    id = db.Column(db.String(50), primary_key=True)
    nickname = db.Column(db.String(30), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    full_body_img_path = db.Column(db.String(255), nullable=True)
    access_token = db.Column(db.String(200), nullable=False)
    refresh_token = db.Column(db.String(200))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return str(self.as_dict())


class MyClothes(db.Model):
    __tablename__ = 'MY_CLOTHES'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), db.ForeignKey('SEEOT_USER.id'), nullable=False)
    origin_img_path = db.Column(db.String(255), nullable=True)
    season = db.Column(db.String(30), nullable=True)
    is_user_img = db.Column(db.Boolean, nullable=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return str(self.as_dict())
