import json
import sys
import sqlalchemy
from bcrypt import checkpw
from flask import jsonify, redirect, render_template, request, url_for, make_response, abort, g
from flask_login import current_user, login_required, login_user, logout_user
from app import db, login_manager, auth
from app.base import blueprint
from app.base.models import User, PodCast, Genre
from config import Config as c
from http import HTTPStatus
from flask import Blueprint
from flasgger import swag_from
from app.base.models import WelcomeModel
from app.base.schemas import WelcomeSchema
import requests
import inspect as s_inspect
from datetime import date, datetime, timedelta
import jsonpickle
from sqlalchemy import desc


class JsonTransformer(object):
    """
    Transform a python list object into a JSON string
    """
    def transform(self, myObject):
        jsonpickle.set_preferred_backend('json')
        jsonpickle.set_encoder_options('json', ensure_ascii=False)
        return jsonpickle.encode(myObject, unpicklable=False)


class PodCastsToExport:

    def __init__(self, f_artist_name, f_pod_cast_id,
                 f_release_date,
                 f_name,
                 f_kind,
                 f_copyright,
                 f_artist_id,
                 f_content_advisory_rating,
                 f_artist_url,
                 f_art_work_url100):
        # self.id = f_id
        self.artistName = f_artist_name
        self.id = f_pod_cast_id
        self.releaseDate = f_release_date
        self.name = f_name
        self.kind = f_kind
        self.copyright = f_copyright
        self.artistId = f_artist_id
        self.contentAdvisoryRating = f_content_advisory_rating
        self.artistUrl = f_artist_url
        self.artWorkUrl100 = f_art_work_url100
        self.genres = []


class GenreToExport:
    def __init__(self, f_genre_id,
                 f_name,
                 f_url):
        # self.id = f_id
        self.genreId = f_genre_id
        self.name = f_name
        self.url = f_url
        # self.podCastId = f_pod_cast_id


def try_or(fn, default):
    try:
        return fn()
    except:
        return default


@blueprint.route('/welcome')
@auth.login_required()
@swag_from('welcome.yml')
def welcome():
    """
    A simple welcome message (Test the basic Authentication method)
    ---
    """
    result = WelcomeModel()
    return WelcomeSchema().dump(result), 200


@blueprint.route('/getPodCasts')
@swag_from('getPodCasts.yml')
def get_pod_casts():
    """
    Get Top 100 iTunes PodCasts and store the JSON data in a SQLite database
    ---
    """
    # iTunes top 100 PodCasts URL
    itunes_url = "https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/100/explicit.json"
    response = requests.get(itunes_url)
    json_data = json.loads(response.content)
    # Clean the entities before every request
    db.session.query(Genre).delete()
    db.session.query(PodCast).delete()
    db.session.commit()
    # Store index loop
    index = 1
    for result in json_data['feed']['results']:
        try:
            print(result)
            # Create a new PodCast entity
            o = PodCast()
            # Assign the fields
            o.podCastId = try_or(lambda: int(result['id']), 0)
            o.artistName = try_or(lambda: result['artistName'], '')
            o.releaseDate = try_or(lambda: datetime.strptime(result['releaseDate'], '%Y-%m-%d'), datetime.now())
            o.name = try_or(lambda: result['name'], '')
            o.kind = try_or(lambda: result['kind'], '')
            o.copyright = try_or(lambda: result['copyright'], '')
            o.artistId = try_or(lambda: int(result['artistId']), 0)
            o.contentAdvisoryRating = try_or(lambda: result['contentAdvisoryRating'], '')
            o.artistUrl = try_or(lambda: result['artistUrl'], '')
            o.artworkUrl100 = try_or(lambda: result['artworkUrl100'], '')
            # if o.podCastId != 0:
            db.session.add(o)
            db.session.flush()
            podcast_id = o.id
            db.session.commit()
            # Loop through PodCasts gender
            for gen in result['genres']:
                d = Genre()
                d.genreId = try_or(lambda: int(gen['genreId']), 0)
                d.name = try_or(lambda: gen['name'], '')
                d.url = try_or(lambda: gen['url'], '')
                d.podCast = podcast_id
                db.session.add(d)
                db.session.commit()
            index = index + 1
        except IOError as errno:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  I/O error({1})".format(function_name, errno, line_no)
            print(msg)
        except ValueError as v:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{1}]:  Could not convert data to an integer.".format(function_name, line_no)
            print(msg)
        except Exception as e:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  Unexpected error: {1}".format(function_name, sys.exc_info()[0], line_no)
            print(msg)
    result = "Total JSON records imported: {0}".format(index)
    return result, 200


@blueprint.route('/savePodCasts')
@swag_from('savePodCasts.yml')
def save_pod_casts():
    """
    Get the top 100 PodCasts stored in the local SQLite database and output the results into a new JSON file response
    ---
    """
    index = 1
    pods = PodCast.query.all()
    all_pods = []
    for pod in pods:
        try:
            print(pod)
            l_gens = []
            p = PodCastsToExport
            p = PodCastsToExport(pod.artistName,
                                 pod.podCastId,
                                 pod.releaseDate,
                                 pod.name,
                                 pod.kind,
                                 pod.copyright,
                                 pod.artistId,
                                 pod.contentAdvisoryRating,
                                 pod.artistUrl,
                                 pod.artworkUrl100)
            g = Genre.query.filter_by(podCast=pod.id).all()
            for gg in g:
                l_g = GenreToExport(gg.genreId,
                                    gg.name,
                                    gg.url)
                l_gens.append(l_g)
            p.genres.append(l_gens)
            all_pods.append(p)
            index = index + 1
        except IOError as errno:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  I/O error({1})".format(function_name, errno, line_no)
            print(msg)
        except ValueError as v:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{1}]:  Could not convert data to an integer.".format(function_name, line_no)
            print(msg)
        except Exception as e:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  Unexpected error: {1}".format(function_name, sys.exc_info()[0], line_no)
            print(msg)
    print(all_pods)
    jt = JsonTransformer()
    json_string = jt.transform(all_pods)
    result = "Total JSON records imported: {0}".format(index)
    response = make_response(json_string)
    cd = 'attachment; filename=json_response.json'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/plain'
    return response, 200


@blueprint.route('/saveTop20PodCasts')
@swag_from('saveTop20PodCasts.yml')
def save_top_20_pod_casts():
    """
    Get the top 20 stored PodCasts and output the results into a new JSON file response
    ---
    """
    index = 1
    pods = PodCast.query.limit(20).all()
    all_pods = []
    for pod in pods:
        try:
            print(pod)
            l_gens = []
            p = PodCastsToExport
            p = PodCastsToExport(pod.artistName,
                                 pod.podCastId,
                                 pod.releaseDate,
                                 pod.name,
                                 pod.kind,
                                 pod.copyright,
                                 pod.artistId,
                                 pod.contentAdvisoryRating,
                                 pod.artistUrl,
                                 pod.artworkUrl100)
            g = Genre.query.filter_by(podCast=pod.id).all()
            for gg in g:
                l_g = GenreToExport(gg.genreId,
                                    gg.name,
                                    gg.url)
                l_gens.append(l_g)
            p.genres.append(l_gens)
            all_pods.append(p)
            index = index + 1
        except IOError as errno:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  I/O error({1})".format(function_name, errno, line_no)
            print(msg)
        except ValueError as v:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{1}]:  Could not convert data to an integer.".format(function_name, line_no)
            print(msg)
        except Exception as e:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  Unexpected error: {1}".format(function_name, sys.exc_info()[0], line_no)
            print(msg)
    print(all_pods)
    jt = JsonTransformer()
    json_string = jt.transform(all_pods)
    result = "Total JSON records imported: {0}".format(index)
    response = make_response(json_string)
    cd = 'attachment; filename=json_top_20_podcasts_response.json'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/plain'
    return response, 200


@blueprint.route('/replaceTop20PodCastsWithBottom20')
@swag_from('replaceTop20PodCastsWithBottom20.yml')
def replace_top_20_pod_casts_with_bottom_20():
    """
    Switch top and bottom 20 PodCasts in the new Json File to create
    ---
    """
    index = 1
    pods = PodCast.query.order_by(desc(PodCast.id)).limit(20).all()
    all_pods = []
    for pod in pods:
        try:
            print(pod)
            l_gens = []
            p = PodCastsToExport
            p = PodCastsToExport(pod.artistName,
                                 pod.podCastId,
                                 pod.releaseDate,
                                 pod.name,
                                 pod.kind,
                                 pod.copyright,
                                 pod.artistId,
                                 pod.contentAdvisoryRating,
                                 pod.artistUrl,
                                 pod.artworkUrl100)
            g = Genre.query.filter_by(podCast=pod.id).all()
            for gg in g:
                l_g = GenreToExport(gg.genreId,
                                    gg.name,
                                    gg.url)
                l_gens.append(l_g)
            p.genres.append(l_gens)
            all_pods.append(p)
            index = index + 1
        except IOError as errno:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  I/O error({1})".format(function_name, errno, line_no)
            print(msg)
        except ValueError as v:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{1}]:  Could not convert data to an integer.".format(function_name, line_no)
            print(msg)
        except Exception as e:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  Unexpected error: {1}".format(function_name, sys.exc_info()[0], line_no)
            print(msg)
    print(all_pods)
    jt = JsonTransformer()
    json_string = jt.transform(all_pods)
    result = "Total JSON records imported: {0}".format(index)
    response = make_response(json_string)
    cd = 'attachment; filename=json_switch_top_and_bottom_20_podcasts_response.json'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/plain'
    return response, 200


@blueprint.route('/getPodCastByName/<string:name>')
@swag_from('getPodCastByName.yml')
def get_pod_cast_by_name(name):
    """
    Get PodCast by name
    ---
    """
    index = 1
    pods = PodCast.query.filter_by(name=name).all()
    all_pods = []
    for pod in pods:
        try:
            print(pod)
            l_gens = []
            p = PodCastsToExport
            p = PodCastsToExport(pod.artistName,
                                 pod.podCastId,
                                 pod.releaseDate,
                                 pod.name,
                                 pod.kind,
                                 pod.copyright,
                                 pod.artistId,
                                 pod.contentAdvisoryRating,
                                 pod.artistUrl,
                                 pod.artworkUrl100)
            g = Genre.query.filter_by(podCast=pod.id).all()
            for gg in g:
                l_g = GenreToExport(gg.genreId,
                                    gg.name,
                                    gg.url)
                l_gens.append(l_g)
            p.genres.append(l_gens)
            all_pods.append(p)
            index = index + 1
        except IOError as errno:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  I/O error({1})".format(function_name, errno, line_no)
            print(msg)
        except ValueError as v:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{1}]:  Could not convert data to an integer.".format(function_name, line_no)
            print(msg)
        except Exception as e:
            function_name = s_inspect.currentframe().f_code.co_name
            line_no = sys.exc_info()[-1].tb_lineno
            msg = "[{0} Line#{2}]:  Unexpected error: {1}".format(function_name, sys.exc_info()[0], line_no)
            print(msg)
    print(all_pods)
    jt = JsonTransformer()
    json_string = jt.transform(all_pods)
    return json_string, 200


@blueprint.route('/deletePodCastByName/<string:name>')
@swag_from('deletePodCastByName.yml')
def delete_pod_cast_by_name(name):
    """
    Delete PodCast by name
    ---
    """
    index = 1
    pods = PodCast.query.filter_by(name=name).first()
    db.session.delete(pods)
    db.session.commit()

    json_string = "{'Message': 'Record deleted'}"
    return json_string, 200


@blueprint.route('/deletePodCastById/<string:record_id>')
@swag_from('deletePodCastById.yml')
def delete_pod_cast_by_id(record_id):
    """
    Delete PodCast by id
    ---
    """
    index = 1
    record_id = int(record_id)
    pods = PodCast.query.filter_by(id=record_id).first()
    db.session.delete(pods)
    db.session.commit()

    json_string = "{'Message': 'Record deleted'}"
    return json_string, 200


@blueprint.route('/AddUser', methods=['POST'])
@swag_from('AddUser.yml')
def new_user():
    try:
        username = request.json[0]['username']
        password = request.json[0]['password']
        email = request.json[0]['email']
        access = request.json[0]['access']
        if username is None or password is None:
            abort(400)  # missing arguments
        if User.query.filter_by(username=username).first() is not None:
            abort(400)  # existing user
        user = User(username=username, email=email, password=password, access=access)
        user.get_hash_password(password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'username': user.username}), 201
    except IOError as errno:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{2}]:  I/O error({1})".format(function_name, errno, line_no)
        print(msg)
        return jsonify({'error_message': msg}), 201
    except ValueError as v:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{1}]:  Could not convert data to an integer.".format(function_name, line_no)
        print(msg)
        return jsonify({'error_message': msg}), 201
    except Exception as e:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{2}]:  Unexpected error: {1}".format(function_name, sys.exc_info()[0], line_no)
        return jsonify({'error_message': msg}), 201


@auth.verify_password
def verify_password(username_or_token, password):
    """
    Verify user password
    :param username_or_token: Set the username or token to validate
    :param password: Set the password to validate
    :return: True/False
    """
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# @auth.verify_token
# def verify_token(username_or_token, password):
#     # first try to authenticate by token
#     user = User.verify_auth_token(username_or_token)
#     if not user:
#         # try to authenticate with username/password
#         user = User.query.filter_by(username=username_or_token).first()
#         if not user or not user.verify_password(password):
#             return False
#     g.user = user
#     return True


@blueprint.route('/login', methods=['POST'])
@swag_from('login.yml')
def login():
    """
    Test the login method and generate a token for the user
    Currently I'm not using the Bearer token authentication method, it is just for test purposes.
    :return:
    """
    try:
        username = request.json[0]['username']
        password = request.json[0]['password']

        if username is None or password is None:
            abort(400)  # missing arguments
        if User.query.filter_by(username=username).first() is None:
            abort(400)  # not existing user
        auth_correct = verify_password(username, password)
        if auth_correct:
            token = g.user.generate_auth_token(600)
            return jsonify({'token': token.decode('ascii'), 'duration': 600})
        else:
            token = "User is not authenticated - Token generation error"
            return jsonify({'error_msg': token}), 201
    except IOError as errno:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{2}]:  I/O error({1})".format(function_name, errno, line_no)
        print(msg)
        return jsonify({'error_msg': msg}), 201
    except ValueError as v:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{1}]:  Could not convert data to an integer.".format(function_name, line_no)
        print(msg)
        return jsonify({'error_msg': msg}), 201
    except Exception as e:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{2}]:  Unexpected error: {1}".format(function_name, sys.exc_info()[0], line_no)
        return jsonify({'error_msg': msg}), 201


@blueprint.route('/getUserById/<string:id>')
@swag_from('getUserById.yml')
def get_user(user_id):
    """
    Return user information
    :param user_id: User id
    :return: User Jsonify information
    """
    try:
        user_id = int(user_id)
        user = User.query.get(user_id)
        if not user:
            abort(400)
        return jsonify({'username': user.username, 'email': user.email, 'access': user.access})
    except IOError as errno:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{2}]:  I/O error({1})".format(function_name, errno, line_no)
        print(msg)
        return jsonify({'error_message': msg}), 201
    except ValueError as v:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{1}]:  Could not convert data to an integer.".format(function_name, line_no)
        print(msg)
        return jsonify({'error_message': msg}), 201
    except Exception as e:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{2}]:  Unexpected error: {1}".format(function_name, sys.exc_info()[0], line_no)
        return jsonify({'error_message': msg}), 201


@blueprint.route('/token')
@auth.login_required
def get_auth_token():
    """
    Create a new user token
    :return: User Jsonify token
    """
    try:
        token = g.user.generate_auth_token(600)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})
    except IOError as errno:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{2}]:  I/O error({1})".format(function_name, errno, line_no)
        print(msg)
        return jsonify({'error_message': msg}), 201
    except ValueError as v:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{1}]:  Could not convert data to an integer.".format(function_name, line_no)
        print(msg)
        return jsonify({'error_message': msg}), 201
    except Exception as e:
        function_name = s_inspect.currentframe().f_code.co_name
        line_no = sys.exc_info()[-1].tb_lineno
        msg = "[{0} Line#{2}]:  Unexpected error: {1}".format(function_name, sys.exc_info()[0], line_no)
        return jsonify({'error_message': msg}), 201



