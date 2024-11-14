from datetime import datetime, timezone
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    recipes: so.WriteOnlyMapped['Recipe'] = so.relationship(
        back_populates='creator')
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @login.user_loader
    def load_user(id):
        return db.session.get(User, int(id))
    
class Recipe(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(64))
    method: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1024))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    creator: so.Mapped[User] = so.relationship(back_populates='recipes')
    ingredients: so.WriteOnlyMapped['Ingredient'] = so.relationship(
        back_populates='recipe')

    def __repr__(self):
        return '<Reciple {}>'.format(self.title)
    
class Ingredient(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    description: so.Mapped[str] = so.mapped_column(sa.String(64))
    quantity: so.Mapped[Optional[float]] = so.mapped_column(sa.Float)
    unit: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    recipe_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Recipe.id),
                                               index=True)

    recipe: so.Mapped[Recipe] = so.relationship(back_populates='ingredients')

    def __repr__(self):
        return '<Ingredient {} - {} {}>'.format(self.description, self.quantity, self.unit)
    