from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    _id = Column("id", Integer, primary_key=True, autoincrement=True)
    _title = Column("title", String, nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    magazine_id = Column(Integer, ForeignKey('magazines.id'), nullable=False)

    # Relationships
    author = relationship("Author", back_populates="articles")
    magazine = relationship("Magazine", back_populates="articles")

    def __init__(self, author, magazine, title, session):
        # Validate title
        if not isinstance(title, str) or not (5 <= len(title) <= 50):
            raise ValueError("Title must be a string between 5 and 50 characters, inclusive.")

        # Check if title is already set
        if hasattr(self, "_title"):
            raise AttributeError("Title cannot be changed after initialization.")

        # Set the title and retrieve foreign keys
        self._title = title
        self.author_id = author.id
        self.magazine_id = magazine.id

        # Add the new Article to the database
        session.add(self)
        session.commit()
        # Ensure the ID is populated after commit
        session.refresh(self)

    @property
    def id(self):
        """Returns the ID of the newly created Article."""
        return self._id

    @property
    def title(self):
        """Returns the article's title."""
        return self._title

    @title.setter
    def title(self, value):
        raise AttributeError("Title cannot be changed after initialization.")

    @property
    def get_author(self):
        """Returns the author of the article."""
        return self.author

    @property
    def get_magazine(self):
        """Returns the magazine of the article."""
        return self.magazine

    def __repr__(self):
        return f'<Article {self.title}>'

# Example setup for related models (Author and Magazine)

class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    articles = relationship("Article", back_populates="author")

    def __init__(self, name, session):
        self.name = name
        session.add(self)
        session.commit()
        session.refresh(self)

class Magazine(Base):
    __tablename__ = 'magazines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    articles = relationship("Article", back_populates="magazine")

# Example usage
if __name__ == '_main_':
    # Setup database connection and session
    engine = create_engine('sqlite:///example.db', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Create an author and a magazine
    author = Author(name="J.K. Rowling", session=session)
    magazine = Magazine(name="Fantasy Times", category="Fantasy", session=session)

    # Create an article
    try:
        new_article = Article(author=author, magazine=magazine, title="The Magic of Writing", session=session)
        print(f"New Article ID: {new_article.id}, Title: {new_article.title}")
        print(f"Author: {new_article.get_author.name}")
        print(f"Magazine: {new_article.get_magazine.name}")
    except Exception as e:
        print(f"Error: {e}")