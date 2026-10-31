from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from extensions import db, migrate, jwt, bcrypt
from models import User, Note
from schema import user_schema, note_schema, notes_schema


# Create Flask app
app = Flask(__name__)


# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-in-production"


# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
bcrypt.init_app(app)


# Enable CORS
CORS(
    app,
    origins=[
        "http://localhost:4000",
        "http://localhost:3000"
    ],
    supports_credentials=True
)


# ==========================
# Authentication Routes
# ==========================


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    # Validate input
    if not data.get("username") or not data.get("password"):
        return jsonify({
            "errors": [
                "Username and password are required"
            ]
        }), 422


    if data.get("password") != data.get("password_confirmation"):
        return jsonify({
            "errors": [
                "Passwords do not match"
            ]
        }), 422


    # Check existing username
    existing_user = User.query.filter_by(
        username=data["username"]
    ).first()

    if existing_user:
        return jsonify({
            "errors": [
                "Username already taken"
            ]
        }), 422


    # Create user
    user = User(
        username=data["username"]
    )

    # Uses password setter from model
    user.password = data["password"]


    db.session.add(user)
    db.session.commit()


    # Create JWT token
    token = create_access_token(
        identity=str(user.id)
    )


    return jsonify({
        "token": token,
        "user": user_schema.dump(user)
    }), 201



@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()


    if not data.get("username") or not data.get("password"):
        return jsonify({
            "errors": [
                "Username and password are required"
            ]
        }), 422


    # Find user
    user = User.query.filter_by(
        username=data["username"]
    ).first()


    # Validate password
    if not user or not user.authenticate(data["password"]):
        return jsonify({
            "errors": [
                "Invalid username or password"
            ]
        }), 401



    token = create_access_token(
        identity=str(user.id)
    )


    return jsonify({
        "token": token,
        "user": user_schema.dump(user)
    }), 200


# Current User Route


@app.route("/me", methods=["GET"])
@jwt_required()
def me():

    user_id = get_jwt_identity()


    user = User.query.get(
        int(user_id)
    )


    if not user:
        return jsonify({
            "errors": [
                "User not found"
            ]
        }), 404


    return jsonify(
        user_schema.dump(user)
    ), 200


# ==========================
# Custom Resource Routes (Notes)
# ==========================


@app.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Clamp per_page to reasonable bounds
    per_page = min(max(per_page, 1), 100)

    # Query notes belonging to the current user
    pagination = Note.query.filter_by(
        user_id=user_id
    ).order_by(
        Note.updated_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    notes = pagination.items

    return jsonify({
        "notes": notes_schema.dump(notes),
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200


@app.route("/notes", methods=["POST"])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Validate input
    if not data or not data.get("title"):
        return jsonify({
            "errors": ["Title is required"]
        }), 422

    note = Note(
        title=data["title"],
        content=data.get("content", ""),
        user_id=user_id
    )

    db.session.add(note)
    db.session.commit()

    return jsonify(note_schema.dump(note)), 201


@app.route("/notes/<int:id>", methods=["GET"])
@jwt_required()
def get_note(id):
    user_id = int(get_jwt_identity())

    note = Note.query.filter_by(
        id=id,
        user_id=user_id
    ).first()

    if not note:
        return jsonify({
            "errors": ["Note not found"]
        }), 404

    return jsonify(note_schema.dump(note)), 200


@app.route("/notes/<int:id>", methods=["PATCH"])
@jwt_required()
def update_note(id):
    user_id = int(get_jwt_identity())

    note = Note.query.filter_by(
        id=id,
        user_id=user_id
    ).first()

    if not note:
        return jsonify({
            "errors": ["Note not found"]
        }), 404

    data = request.get_json()

    if data.get("title") is not None:
        note.title = data["title"]
    if data.get("content") is not None:
        note.content = data["content"]

    db.session.commit()

    return jsonify(note_schema.dump(note)), 200


@app.route("/notes/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_note(id):
    user_id = int(get_jwt_identity())

    note = Note.query.filter_by(
        id=id,
        user_id=user_id
    ).first()

    if not note:
        return jsonify({
            "errors": ["Note not found"]
        }), 404

    db.session.delete(note)
    db.session.commit()

    return jsonify({
        "message": "Note deleted successfully"
    }), 200


# Run Application


if __name__ == "__main__":
    app.run(
        port=5555,
        debug=True
    )