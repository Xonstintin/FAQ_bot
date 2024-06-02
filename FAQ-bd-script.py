from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import FAQ

Base = declarative_base()
engine = create_engine('sqlite:///faq.db')
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

# Пример добавления данных
faq1 = FAQ(question="What is the capital of France?", answer="The capital of France is Paris.")
session.add(faq1)
session.commit()
