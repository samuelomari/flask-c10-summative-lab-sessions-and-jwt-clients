from extensions import ma
from models import User, Note


class UserSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = User
        load_instance = True
        exclude = ("_password_hash",)


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class NoteSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Note
        load_instance = True
        include_fk = True

    user = ma.Nested(UserSchema, only=("id", "username"))


note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)