from flask import Flask, Blueprint, render_template, request, abort, jsonify, redirect, url_for
import db

bp = Blueprint("glowing-eureka", __name__)

def getAuthFromRequest() -> db.token | None:
    if "auth" not in request.cookies:
        return 0
    tok = db.validateToken(request.cookies["auth"])
    return tok

def getUserFromRequest() -> db.user | None:
    if "auth" not in request.cookies:
        return None
    usr = db.getUserFromAuth(request.cookies["auth"])
    if usr is None:
        return None
    return usr

@bp.route("/")
def home():
    return redirect(url_for("glowing-eureka.products"))

@bp.route("/products/", methods=["GET"])
def products():
    with db.Session(db.engine) as session:
        stmt = db.select(db.product).where(db.product.isDeleted != True)
        query = [r for r in session.scalars(stmt) if not r.isDeleted]
    return render_template("products.html", products=query, auth=getAuthFromRequest())

@bp.route("/products/<id>", methods=["GET"])
def singleProduct(id:int):
    id = int(id)
    with db.Session(db.engine) as session:
        stmt = db.select(db.product).where(db.product.id == id)
        product = [r for r in session.scalars(stmt)][0]
        stmt = db.select(db.comment).where(db.comment.productId == product.id)
        comments = [r for r in session.scalars(stmt)]
    return render_template("product.html", product=product, comments=comments, auth=getAuthFromRequest(), user=getUserFromRequest())

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
    return redirect(url_for("glowing-eureka.singleProduct", id=id))

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