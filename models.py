from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"   # table for users

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # One-to-many: a user can have many clothing items
    items = db.relationship(
        "ClothingItem",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def set_password(self, password: str) -> None:
        """Store a hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plain password against the hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username!r}>"


class ClothingItem(db.Model):
    __tablename__ = "clothing_items"  # explicit table name (optional but nice)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_filename = db.Column(db.String(200), nullable=False)
    tags = db.Column(Text)  # store as JSON string

    # NEW: link each item to a user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relationship back to User
    user = db.relationship("User", back_populates="items")

    def __repr__(self):
        return f"<ClothingItem {self.name!r} (user_id={self.user_id})>"
