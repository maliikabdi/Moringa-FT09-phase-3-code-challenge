from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm import declarative_base


Base = declarative_base()

# Association table for many-to-many relationship between Author and Magazine
author_magazine = Table(
    'author_magazine', Base.metadata,
    Column('author_id', Integer, ForeignKey('authors.id')),
    Column('magazine_id', Integer, ForeignKey('magazines.id'))
)

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id'))

    author = relationship('Author', back_populates='articles')

class Magazine(Base):
    __tablename__ = 'magazines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    authors = relationship('Author', secondary=author_magazine, back_populates='magazines')

class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Relationships
    articles = relationship('Article', back_populates='author')
    magazines = relationship('Magazine', secondary=author_magazine, back_populates='authors')

    def __init__(self, name):
        if not isinstance(name, str) or len(name) == 0:
            raise ValueError("Name must be a non-empty string.")
        self.name = name

    def __repr__(self):
        return f'<Author {self.name}>'

# Example setup and usage
if __name__ == '_main_':
    # Setup database connection and session
    engine = create_engine('sqlite:///example.db', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a new author
    try:
        new_author = Author(name="J.K. Rowling")
        session.add(new_author)
        session.commit()
        session.refresh(new_author)
        print(f"New Author ID: {new_author.id}, Name: {new_author.name}")

        # Create some magazines and articles for the author
        magazine1 = Magazine(name="Fantasy Monthly")
        magazine2 = Magazine(name="Literary Digest")
        article1 = Article(title="The Wizarding World", author=new_author)
        article2 = Article(title="Harry Potter's Legacy", author=new_author)

        # Associate the magazines with the author
        new_author.magazines.extend([magazine1, magazine2])

        session.add_all([magazine1, magazine2, article1, article2])
        session.commit()

        # Fetch and display associated articles and magazines
        print("Articles written by the author:")
        for article in new_author.articles:
            print(article.title)

        print("Magazines associated with the author:")
        for magazine in new_author.magazines:
            print(magazine.name)

    except Exception as e:
        print(f"Error: {e}")