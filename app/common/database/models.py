from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
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

    author_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    biography = Column(String)

    books: Mapped[List["Book"]] = relationship(
        secondary=author_association_table,
        back_populates="authors"  # Changed from 'book' to 'books'
    )

class Book(Base):
    __tablename__ = "books"

    book_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    genre = Column(String)
    description = Column(String)

    authors: Mapped[List["Author"]] = relationship(
        secondary=author_association_table,
        back_populates="books"  # Changed from 'author' to 'authors'
    )


Base.metadata.create_all(bind=engine)

