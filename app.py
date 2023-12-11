from flask import Flask, Blueprint, render_template, request, abort, jsonify, redirect, url_for
import db

bp = Blueprint("glowing-eureka", __name__)

def getAuthFromRequest() -> db.token | None:
    if "auth" not in request.cookies:
        return None
    tok = db.validateToken(request.cookies["auth"])
    return tok

def getUserFromRequest() -> db.user | None:
    if "auth" not in request.cookies:
        return None
    usr = db.getUserFromAuth(request.cookies["auth"])
    if usr is None:
        return None
    return usr

def getPageFromRequest() -> int:
    if "page" not in request.args:
        return 0
    else:
        return int(request.args["page"])

@bp.route("/")
def home():
    return redirect(url_for("glowing-eureka.products"))

@bp.route("/products", methods=["GET"])
def products():
    page = getPageFromRequest()
    phrase = ""
    if "search" in request.args:
        phrase = request.args["search"]
    with db.Session(db.engine) as session:
        stmt = db.select(db.product).where(db.product.isDeleted == False).where(db.product.title.like(f"%{phrase}%"))
        query = session.scalars(stmt).fetchall()
    return render_template("products.html", products=query[page * 6:(page + 1) * 6], auth=getAuthFromRequest(), page=page, next=len(query) > (page + 1) * 6, phrase=phrase)

@bp.route("/products/new", methods=["GET", "POST"])
def newProduct():
    tok = getAuthFromRequest()
    if tok is None:
        abort(401)
    if tok.level < 1:
        abort(403)
    if request.method == "GET":
        return render_template("newProduct.html", auth=getAuthFromRequest())
    else:
        if request.form["productId"] != "" and request.form["productId"].isnumeric():
            id = int(request.form["productId"])
            with db.Session(db.engine) as session:
                stmt = db.select(db.product).where(db.product.id == id)
                product = session.scalars(stmt).first()
                product.title = request.form["productName"]
                product.description = request.form["productDescription"]
                if len(request.form["productImageUrl"]) > 0:
                    product.imageURL = request.form["productImageUrl"]
                session.commit()
            return redirect(url_for("glowing-eureka.singleProduct", id=id))
        else:
            with db.Session(db.engine) as session:
                product = db.product(request.form["productName"], request.form["productDescription"], request.form["productImageUrl"])
                session.add(product)
                session.commit()
            return redirect(url_for("glowing-eureka.products"))

@bp.route("/products/<id>", methods=["GET"])
def singleProduct(id:int):
    if not id.isnumeric():
        abort(400)
    page = getPageFromRequest()
    id = int(id)
    with db.Session(db.engine) as session:
        stmt = db.select(db.product).where(db.product.id == id)
        product = [r for r in session.scalars(stmt)][0]
        stmt = db.select(db.comment).where(db.comment.productId == product.id).where(db.comment.isDeleted == False)
        comments = [r for r in session.scalars(stmt)]
    return render_template("product.html", product=product, comments=comments[page * 5:(page + 1) * 5], page=page, next=len(comments) > (page + 1) * 5, auth=getAuthFromRequest(), user=getUserFromRequest())

@bp.route("/products/<id>/edit", methods=["GET"])
def editProduct(id:int):
    auth = getAuthFromRequest()
    if auth is None or auth.level < 1:
        abort(401)
    id = int(id)
    with db.Session(db.engine) as session:
        stmt = db.select(db.product).where(db.product.id == id)
        product = session.scalars(stmt).first()
    if product.imageURL is None:
        product.imageURL = ""
    return render_template("newProduct.html", id=product.id, name=product.title, description=product.description, url=product.imageURL, auth=getAuthFromRequest())

@bp.route("/products/<id>/delete", methods=["POST"])
def deleteProduct(id:int):
    auth = getAuthFromRequest()
    if auth is None or auth.level < 1:
        abort(401)
    id = int(id)
    with db.Session(db.engine) as session:
        stmt = db.select(db.product).where(db.product.id == id)
        product = session.scalars(stmt).first()
        product.isDeleted = True
        session.commit()
    return redirect(url_for("glowing-eureka.products"))

@bp.route("/products/<id>/comment", methods=["POST"])
def addComment(id:int):
    tok = getAuthFromRequest()
    if tok is None:
        abort(401)
    id = int(id)
    text = request.form["commentInput"]
    with db.Session(db.engine) as session:
        check = db.select(db.exists(db.product).where(db.product.id == id))
        b = session.scalars(check).fetchall()
        if not b:
            abort(400)
        if "commentId" in request.form.keys():
            existing = session.query(db.comment).where(db.comment.id == request.form["commentId"]).first()
            existing.description = text
        else:
            comment = db.comment(id, text, tok.user)
            session.add(comment)
        session.commit()
    return redirect(url_for("glowing-eureka.singleProduct", id=id))

@bp.route("/products/<id>/comment/delete", methods=["POST"])
def deleteComment(id:int):
    id = int(id)
    if getAuthFromRequest() is None:
        abort(401)
    usr = getUserFromRequest()
    commentId = request.form["commentId"]
    with db.Session(db.engine) as session:
        comment = session.query(db.comment).where(db.comment.id == commentId).first()
        if comment.userId != usr.id:
            abort(401)
        comment.isDeleted = True
        session.commit()
    page = getPageFromRequest()
    return redirect(url_for("glowing-eureka.singleProduct", id=id, page=page))

@bp.route("/products/<id>/comment/edit", methods=["POST"])
def editComment(id:int):
    id = int(id)
    if getAuthFromRequest() is None:
        abort(401)
    usr = getUserFromRequest()
    data = request.json
    with db.Session(db.engine) as session:
        comment = session.query(db.comment).where(db.comment.id == data["commentId"]).first()
        if comment.userId != usr.id:
            abort(401)
        comment.description = data["description"]
        session.commit()
    page = getPageFromRequest()
    return redirect(url_for("glowing-eureka.singleProduct", id=id, page=page))

@bp.route("/users", methods=["GET"])
def users():
    auth = getAuthFromRequest()
    if auth == None or auth.level < 1:
        abort(401)
    with db.Session(db.engine) as session:
        users = session.query(db.user).all()
    return render_template("users.html", users=users, auth=auth)

@bp.route("/users/delete", methods=["POST"])
def deleteUsers():
    auth = getAuthFromRequest()
    if auth == None or auth.level < 1:
        abort(401)
    id = int(request.json["id"])
    with db.Session(db.engine) as session:
        user = session.query(db.user).where(db.user.id == id).first()
        if user.auth >= auth.level:
            abort(403)
        session.delete(user)
        session.commit()
    return redirect(url_for("glowing-eureka.users"))

@bp.route("/users/edit", methods=["POST"])
def editUser():
    auth = getAuthFromRequest()
    if auth == None or auth.level < 1:
        abort(401)
    with db.Session(db.engine) as session:
        user = session.query(db.user).where(db.user.id == request.json["id"]).first()
        if user.auth >= auth.level:
            abort(403)
        user.auth = request.json["level"]
        session.commit()
    return redirect(url_for("glowing-eureka.users"))

@bp.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@bp.route("/logout", methods=["GET", "POST"])
def logout():
    with db.Session(db.engine) as session:
        stmt = db.delete(db.token).where(db.token.hash == request.cookies.get("auth"))
        session.execute(stmt)
        session.commit()
    return redirect(url_for("glowing-eureka.products"))

@bp.route("/login", methods=["POST"])
def loginValidate():
    j = request.json
    if not isinstance(j, dict):
        abort(400)
    if "username" not in j.keys() or "password" not in j.keys():
        abort(400)
    level = db.logIn(j["username"], j["password"])
    if level == None:
        abort(401)
    with db.Session(db.engine) as session:
        user = session.query(db.user).where(db.user.username == j["username"]).first()
        token = db.token(level, 86400, user)
        session.add(token)
        session.commit()
        return jsonify(token.hash)

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run()