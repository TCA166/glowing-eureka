from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, create_engine, select, TIMESTAMP
from sqlalchemy.orm import relationship, backref, declarative_base, Session
import hashlib, uuid
from datetime import datetime

Base = declarative_base()

engine = create_engine("sqlite:///main.db")

class product(Base):
    """A product stored in the database, that has a title, decription, image, can have comments attached to and belongs to a category"""
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    isDeleted = Column(Boolean, nullable=False)
    creationDate = Column(Date, default="CURRENT_DATE")
    imageURL = Column(String)
    categoryId = Column(Integer, ForeignKey("category.id"))
    comments = relationship("comment", backref=backref("comment"))

class comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    productId = Column(Integer, ForeignKey("product.id"), nullable=False)
    description = Column(String)
    isDeleted = Column(Boolean, nullable=False)
    creationDate = Column(Date, nullable=False)

class category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    products = relationship("product", backref=backref("product"))

class user(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    auth = Column(Integer, nullable=False)
    salt = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    def __init__(self, username:str, password:str, auth:int) -> None:
        salt = uuid.uuid4().hex
        super().__init__(username=username, auth=auth, salt=salt, hash=hashlib.sha512((password + salt).encode("utf-8")).hexdigest())

class token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    valid = Column(Integer)
    def __init__(self, level:int, valid:int | None) -> None:
        token = uuid.uuid4().hex
        super().__init__(token=token, level=level, created=datetime.now().timestamp(), valid=valid)

def logIn(username:str, password:str) -> int:
    """Returns the user's auth level if the credentials are valid, and None if they are not"""
    with Session(engine) as session:
        stmt = select(user).where(user.username == username)
        query = [r for r in session.scalars(stmt)]
        if len(query) == 0:
            return None
        u = query[0]
        hash = hashlib.sha512((password + u.salt).encode("utf-8")).hexdigest()
        if hash == u.hash:
            return u.auth
        else:
            return None

if __name__ == "__main__":
    with Session(engine) as session:
        Base.metadata.create_all(engine)
        session.commit()
