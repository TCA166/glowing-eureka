from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, create_engine, select, TIMESTAMP, delete, Table, exists
from sqlalchemy.orm import relationship, backref, declarative_base, Session, joinedload
import hashlib, uuid
from datetime import datetime
from sqlalchemy.orm import Mapped
Base = declarative_base()

engine = create_engine("sqlite:///main.db")

class comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    productId = Column(Integer, ForeignKey("product.id"), nullable=False)
    description = Column(String)
    isDeleted = Column(Boolean, nullable=False)
    creationDate = Column(Date, nullable=False)
    userId = Column(Integer, ForeignKey("user.id"), nullable=False)
    def __init__(self, productId:int, description:str, user:'user'):
        super().__init__(productId=productId, description=description, isDeleted=False, creationDate=datetime.now(), user=user)

product_category = Table("product_category", Base.metadata, Column("productId", ForeignKey("product.id"), primary_key=True), Column("categoryId", ForeignKey("category.id"), primary_key=True))

class product(Base):
    """A product stored in the database, that has a title, decription, image, can have comments attached to and belongs to a category"""
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    isDeleted = Column(Boolean, nullable=False)
    creationDate = Column(Date, default="CURRENT_DATE")
    imageURL = Column(String)
    categories: Mapped[list['category']] = relationship(
        secondary=product_category, back_populates="products"
    )
    comments = relationship("comment", backref=backref("product"))
    def __init__(self, title:str, description:str, url:str, categories:list['category']=None) -> None:
        kwargs = {"title":title, "description":description, "creationDate":datetime.now(), "imageURL":url, "isDeleted":False}
        if isinstance(categories, list):
            kwargs["categories"] = categories
        super().__init__(**kwargs)

class category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    products: Mapped[list[product]] = relationship(
        secondary=product_category, back_populates="categories"
    )

class user(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    auth = Column(Integer, nullable=False)
    salt = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    tokens = relationship("token", backref=backref("user"), lazy=False)
    comments = relationship("comment", backref=backref("user"))
    def __init__(self, username:str, password:str, auth:int) -> None:
        salt = uuid.uuid4().hex
        super().__init__(username=username, auth=auth, salt=salt, hash=hashlib.sha512((password + salt).encode("utf-8")).hexdigest())

class token(Base):
    __tablename__ = "token"
    id = Column(Integer, primary_key=True)
    userId = Column(Integer, ForeignKey("user.id"))
    hash = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    created = Column(TIMESTAMP, nullable=False)
    valid = Column(Integer)
    def __init__(self, level:int, valid:int | None, user:user | None) -> None:
        token = uuid.uuid4().hex
        super().__init__(hash=token, level=level, created=datetime.now(), valid=valid, user=user)

def logIn(username:str, password:str) -> int | None:
    """Returns the user's auth level if the credentials are valid, and None if they are not"""
    with Session(engine) as session:
        stmt = select(user).where(user.username == username)
        query = [r for r in session.scalars(stmt).unique()]
        if len(query) == 0:
            return None
        u = query[0]
        hash = hashlib.sha512((password + u.salt).encode("utf-8")).hexdigest()
        if hash == u.hash:
            return u.auth
        else:
            return None

def validateToken(auth:str) -> token | None:
    """Return's the token's auth level if the token is valid"""
    with Session(engine) as session:
        stmt = select(token).where(token.hash == auth)
        query = [r for r in session.scalars(stmt)]
        if len(query) == 0:
            return None
        t = query[0]
        if t.created.timestamp() + t.valid < datetime.now().timestamp():
            stmt = delete(token).where(token.id == t.id)
            session.execute(stmt)
            session.commit()
            return None
        t.user = t.user
        return t

def getUserFromAuth(auth:str) -> user | None:
    """Return the asociated user id from the provided token"""
    with Session(engine, expire_on_commit=False) as session:
        tok = session.query(token).where(token.hash == auth).first()
        if tok is None:
            return None
        return tok.user

if __name__ == "__main__":
    with Session(engine) as session:
        Base.metadata.create_all(engine)
        session.commit()
