# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'sort_keys': False, 'indent': 4}
db = SQLAlchemy(app)
api = Api(app)
movie_ns = api.namespace("movies")
director_ns = api.namespace("directors")
genre_ns = api.namespace("genres")


class Movie(db.Model):
    """Модель фильма"""
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    """Модель Режиссёра"""
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    """Модель Жанра"""
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    """Схема сериализации фильмов"""
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class GenreSchema(Schema):
    """Схема сериализации жанров"""
    id = fields.Int(dump_only=True)
    name = fields.Str()


class DirectorSchema(Schema):
    """Схема сериализации режиссёров"""
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


@movie_ns.route("/")
class MoviesView(Resource):
    """Страничка всех фильмов"""

    def get(self):
        """Просмотр всех фильмов"""
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        movies = Movie.query
        if director_id:
            movies = movies.filter(Movie.director_id == director_id)

        if genre_id:
            movies = movies.filter(Movie.genre_id == genre_id)

        result = movies_schema.dump(movies.all())
        if not result:
            return "", 404
        return result, 200

    def post(self):
        """Добавление нового фильма"""
        json_movie = request.json
        result = Movie(**json_movie)

        with db.session.begin():
            db.session.add(result)
            db.session.commit()
        return "", 201, {"movie_id": result.id}


@movie_ns.route("/<int:uid>")
class MovieView(Resource):
    def get(self, uid):
        """Получение фильма по его id"""
        movie = Movie.query.get(uid)
        if not movie:
            return "PageNotFound", 404
        return movie_schema.dump(movie), 200

    def put(self, uid):
        """Редактирование фильма по его id"""
        movie = Movie.query.get(uid)
        json_movie = request.json
        if not movie:
            return "PageNotFound", 404
        movie.title = json_movie['title']
        movie.description = json_movie['description']
        movie.trailer = json_movie['trailer']
        movie.year = json_movie['year']
        movie.rating = json_movie['rating']
        movie.genre_id = json_movie['genre_id']
        movie.director_id = json_movie['director_id']
        db.session.add(movie)
        db.session.commit()
        return "", 200

    def delete(self, uid):
        """Удаление фильма по id"""
        movie = Movie.query.get(uid)
        if not movie:
            return "PageNotFound", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


@director_ns.route("/")
class DirectorsView(Resource):
    """Режиссёры"""

    def get(self):
        """Получение списка всех режиссёров"""
        directors = Director.query.all()
        result = directors_schema.dump(directors)
        if not result:
            return "", 404
        return result, 200

    def post(self):
        """Добавление нового режиссёра"""
        json_director = request.json
        result = Director(**json_director)

        with db.session.begin():
            db.session.add(result)
            db.session.commit()
        return "", 201, {"id": result.id}


@director_ns.route("/<int:uid>")
class DirectorView(Resource):
    """Получение режиссёра по его id"""

    def get(self, uid):
        """Получение режиссёра"""
        director = Director.query.get(uid)
        if not director:
            return "PageNotFound", 404
        return director_schema.dump(director), 200

    def put(self, uid):
        """Редактирование данных режиссёра"""
        director = Director.query.get(uid)
        json_director = request.json
        if not director:
            return "PageNotFound", 404
        director.name = json_director['name']
        db.session.add(director)
        db.session.commit()
        return "", 200

    def delete(self, uid):
        """Удаление режиссёра"""
        director = Director.query.get(uid)
        if not director:
            return "PageNotFound", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genre_ns.route("/")
class GenresView(Resource):
    """Все жанры"""

    def get(self):
        """Получение списка всех жанров"""
        genres = Genre.query.all()
        result = genres_schema.dump(genres)
        if not result:
            return "", 404
        return result, 200

    def post(self):
        """Добавление нового жанра"""
        json_genre = request.json
        result = Genre(**json_genre)

        with db.session.begin():
            db.session.add(result)
            db.session.commit()
        return "", 201, {"id": result.id}


@genre_ns.route("/<int:uid>")
class GenreView(Resource):
    """Получение жанра по его id"""

    def get(self, uid):
        """Получение жанра"""
        genre = Genre.query.get(uid)
        if not genre:
            return "PageNotFound", 404
        return genre_schema.dump(genre), 200

    def put(self, uid):
        """Обновление жанра"""
        genre = Genre.query.get(uid)
        json_genre = request.json
        if not genre:
            return "PageNotFound", 404
        genre.name = json_genre['name']
        db.session.add(genre)
        db.session.commit()
        return "", 200

    def delete(self, uid):
        """Удаление жанра"""
        genre = Genre.query.get(uid)
        if not genre:
            return "PageNotFound", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=False)
