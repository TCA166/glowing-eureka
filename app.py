from flask import Flask, Blueprint, render_template, request, abort, jsonify, redirect, url_for
import db

bp = Blueprint("glowing-eureka", __name__)

def getAuthFromRequest() -> int:
    if "auth" not in request.cookies:
        return 0
    lvl = db.validateToken(request.cookies["auth"])
    if lvl == None:
        return 0
    return lvl

def getUserFromRequest() -> db.user | None:
    if "auth" not in request.cookies:
        return None
    usr = db.getUserFromAuth(request.cookies["auth"])
    if usr is None:
        return None
    return usr

@bp.route("/")
@bp.route("/products/", methods=["GET"])
def products():
    with db.Session(db.engine) as session:
        stmt = db.select(db.product).where(db.product.isDeleted != True)
        query = [r for r in session.scalars(stmt) if not r.isDeleted]
    return render_template("products.html", products=query, auth=getAuthFromRequest())

@bp.route("/<id>", methods=["GET"])
@bp.route("/products/<id>", methods=["GET"])
def singleProduct(id:int):
    id = int(id)
    with db.Session(db.engine) as session:
        stmt = db.select(db.product).where(db.product.id == id)
        product = [r for r in session.scalars(stmt)][0]
        stmt = db.select(db.comment).where(db.comment.productId == product.id)
        comments = [r for r in session.scalars(stmt)]
    auth = getAuthFromRequest()
    usr = getUserFromRequest()
    return render_template("product.html", product=product, comments=comments, auth=auth, user=usr)

@bp.route("/<id>/comment", methods=["POST"])
@bp.route("/products/<id>/comment", methods=["POST"])
def addComment(id:int):
    if getAuthFromRequest() == 0:
        abort(401)
    id = int(id)
    text = request.form["commentInput"]
    with db.Session(db.engine) as session:
        check = db.select(db.exists(db.product).where(db.product.id == id))
        b = session.scalars(check).fetchall()
        if not b:
            abort(400)
        comment = db.comment(id, text)
        session.add(comment)
        session.commit()
    return redirect(url_for("glowing-eureka.singleProduct", id=id))

@bp.route("/<id>/comment", methods=["DELETE"])
@bp.route("/products/<id>/comment", methods=["DELETE"])
def deleteComment(id:int):
    id = int(id)
    if getAuthFromRequest() == 0:
        abort(401)
    usr = getUserFromRequest()
    comment = request.form["commentId"]
    with db.Session(db.engine) as session:
        pass

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
        token = db.token(level, 86400)
        session.add(token)
        session.commit()
        return jsonify(token.hash)

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run()