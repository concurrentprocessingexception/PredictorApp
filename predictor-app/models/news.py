from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from database import Base

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    headline = Column(Text)
    url = Column(Text)
    published = Column(DateTime)
    sentiment = Column(String)

    __table_args__ = (UniqueConstraint('symbol', 'headline', 'published', name='uix_news_unique'),)
