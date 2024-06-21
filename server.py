import flask_bcrypt
import pydantic
from flask import Flask, Response, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from models import Session, User, Advertisement
from schema import CreateUser, Schema, UpdateUser, CreateAd, UpdateAd

app = Flask("app")
bcrypt = flask_bcrypt.Bcrypt(app)


def hash_password(password: str) -> str:
    password = password.encode()
    password = bcrypt.generate_password_hash(password)
    password = password.decode()
    return password


def check_password(hashed_password: str, password: str) -> bool:
    hashed_password = hashed_password.encode()
    password = password.encode()
    return bcrypt.check_password_hash(hashed_password, password)


class HttpError(Exception):

    def __init__(self, status_code: int, error_message: str | dict):
        self.status_code = status_code
        self.error_message = error_message


def validate(schema_cls: Schema, json_data: dict):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except pydantic.ValidationError as err:
        error = err.errors()[0]
        error.pop("ctx", None)
        raise HttpError(409, error)


@app.errorhandler(HttpError)
def error_handler(err: HttpError):
    json_response = jsonify({"error": err.error_message})
    json_response.status_code = err.status_code
    return json_response


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response: Response):
    request.session.close()
    return response


def get_user(user_id):
    user = request.session.get(User, user_id)
    if user is None:
        raise HttpError(404, "user not found")
    return user


def get_ad(ad_id):
    ad = request.session.get(Advertisement, ad_id)
    if ad is None:
        raise HttpError(404, "ad not found")
    return ad


def add_user(user: User):
    request.session.add(user)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError(400, "user already exists")
    return user


def create_ad(ad: Advertisement):
    request.session.add(ad)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError(400, "ad already exists")
    return ad

class UserView(MethodView):

    @property
    def session(self) -> Session:
        return request.session

    def get(self, user_id):
        user = get_user(user_id)
        return jsonify(user.json)

    def post(self):
        json_data = validate(CreateUser, request.json)
        json_data["password"] = hash_password(json_data["password"])
        user = add_user(User(**json_data))
        return jsonify(user.json)

    def patch(self, user_id):
        json_data = validate(UpdateUser, request.json)
        if "password" in json_data:
            json_data["password"] = hash_password(json_data["password"])
        user = get_user(user_id)
        for field, value in json_data.items():
            setattr(user, field, value)
        user = add_user(user)
        return jsonify(user.json)

    def delete(self, user_id):
        user = get_user(user_id)
        self.session.delete(user)
        self.session.commit()
        return jsonify({"status": "deleted"})


class AdView(MethodView):

    @property
    def session(self) -> Session:
        return request.session

    def get(self, ad_id):
        ad = get_ad(ad_id)
        return jsonify(ad.json)

    def post(self):
        json_data = validate(CreateAd, request.json)
        ad = create_ad(Advertisement(**json_data))
        return jsonify(ad.json)

    def patch(self, ad_id):
        json_data = request.json
        ad = get_ad(ad_id)
        for field, value in json_data.items():
            setattr(ad, field, value)
        print(ad)
        ad = create_ad(ad)
        return jsonify(ad.json)

    def delete(self, ad_id):
        ad = get_user(ad_id)
        self.session.delete(ad)
        self.session.commit()
        return jsonify({"status": "deleted"})


user_view = UserView.as_view("user")
ad_view = AdView.as_view("ad")

app.add_url_rule("/user/", view_func=user_view, methods=["POST"])
app.add_url_rule(
    "/user/<int:user_id>/", view_func=user_view, methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule("/ad/", view_func=ad_view, methods=["POST"])
app.add_url_rule(
    "/ad/<int:ad_id>/", view_func=ad_view, methods=["GET", "PATCH", "DELETE"]
)

app.run()
