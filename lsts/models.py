from lsts import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    hs_password = db.Column(db.String(60), nullable=False)
    lists = db.relationship(
        "ItemList",
        order_by="asc(func.lower(ItemList.name))",
        cascade="all,delete-orphan",
    )

    def __repr__(self):
        return f"<id:{self.id}, username:{self.username}>"


class ItemList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    items = db.relationship(
        "Item",
        order_by="asc(func.lower(Item.category))",
        cascade="all,delete-orphan",
    )

    def __repr__(self):
        return f"<name:{self.name}, id:{self.id}>"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    category = db.Column(db.String(60))
    note = db.Column(db.String(120))
    list_id = db.Column(
        db.Integer, db.ForeignKey("item_list.id", ondelete="CASCADE"), nullable=False
    )

    def __repr__(self):
        return f"<name:{self.name}, id:{self.id}>"
