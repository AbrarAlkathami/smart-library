from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table , Float
from sqlalchemy.orm import relationship , Mapped , mapped_column 
from typing import List
from datetime import datetime 
from common.database.database import Base ,engine


author_association_table = Table(
    "author_association_table",
    Base.metadata,
    Column("author_id", ForeignKey("authors.author_id"), primary_key=True),
    Column("book_id", ForeignKey("books.book_id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    password_hash = Column(String)
    role = Column(String)

    preferences = relationship("UserPreference", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")

class UserPreference(Base):
    __tablename__ = "userpreferences"

    preference_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, ForeignKey("users.username"))
    preference_type = Column(String)
    preference_value = Column(String)

    user = relationship("User", back_populates="preferences")

class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True , autoincrement=True)
    username = Column(String, ForeignKey("users.username"))
    activity = Column(String)
    timestamp = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="activities")

class Author(Base):
    __tablename__ = "authors"
    author_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    biography = Column(String)

    books = relationship(
        "Book",
        secondary=author_association_table,
        back_populates="authors"
    )

class Book(Base):
    __tablename__ = "books"
    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    subtitle = Column(String, nullable=True)
    published_year = Column(Integer, nullable=True)
    average_rating = Column(Float, nullable=True)
    num_pages = Column(Integer, nullable=True)
    ratings_count = Column(Integer, nullable=True)
    genre = Column(String, nullable=True)
    description = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)

    authors = relationship(
        "Author",
        secondary=author_association_table,
        back_populates="books"
    )

