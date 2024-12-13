from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Relationships
    articles = relationship('Article', back_populates='author')

    def __repr__(self):
        return f"<Author(name='{self.name}')>"

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    magazine_id = Column(Integer, ForeignKey('magazines.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)

    # Relationships
    magazine = relationship('Magazine', back_populates='articles')
    author = relationship('Author', back_populates='articles')

    def __repr__(self):
        return f"<Article(title='{self.title}')>"

class Magazine(Base):
    __tablename__ = 'magazines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)

    # Relationships
    articles = relationship('Article', back_populates='magazine')

    def __repr__(self):
        return f"<Magazine(name='{self.name}', category='{self.category}')>"

    # Method to fetch articles directly from the magazine
    def get_articles(self, session):
        """Returns all articles associated with the magazine."""
        return session.query(Article).filter(Article.magazine_id == self.id).all()

    # Method to fetch contributors (authors)
    def get_contributors(self, session):
        """Returns all authors who have written articles for this magazine."""
        return session.query(Author).join(Article).filter(Article.magazine_id == self.id).distinct().all()

    # Method to fetch article titles
    def get_article_titles(self, session):
        """Returns a list of titles of all articles written for this magazine."""
        articles = self.get_articles(session)
        return [article.title for article in articles] if articles else []

    # Method to get contributing authors with more than 2 articles
    def get_contributing_authors(self, session):
        """Returns authors with more than 2 articles in the magazine."""
        authors = (
            session.query(Author)
            .join(Article)
            .filter(Article.magazine_id == self.id)
            .group_by(Author.id)
            .having(func.count(Article.id) > 2)
            .all()
        )
        return authors if authors else []

# Example setup and usage
if __name__ == '__main__':
    # Setup database connection and session
    engine = create_engine('sqlite:///example.db', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create example data
        author1 = Author(name="J.K. Rowling")
        author2 = Author(name="George R.R. Martin")
        magazine1 = Magazine(name="Fantasy Monthly", category="Fantasy")
        article1 = Article(title="The Wizarding World", magazine=magazine1, author=author1)
        article2 = Article(title="Game of Thrones Insights", magazine=magazine1, author=author2)
        article3 = Article(title="Fantasy Writing Tips", magazine=magazine1, author=author1)

        # Add data to the session and commit
        session.add_all([author1, author2, magazine1, article1, article2, article3])
        session.commit()

        # Fetch data and demonstrate methods
        print("Articles in the magazine:")
        for article in magazine1.articles:
            print(article.title)

        print("\nContributors to the magazine:")
        for author in magazine1.get_contributors(session):
            print(author.name)

        print("\nArticle titles in the magazine:")
        print(magazine1.get_article_titles(session))

        print("\nAuthors with more than 2 articles:")
        for author in magazine1.get_contributing_authors(session):
            print(author.name)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()
