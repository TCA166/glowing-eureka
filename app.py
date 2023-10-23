from flask import Flask, Blueprint, render_template, request, abort, jsonify
import db

bp = Blueprint("glowing-eureka", __name__)

def getAuthFromRequest() -> int:
    if "auth" not in request.cookies:
        return 0
    lvl = db.validateToken(request.cookies["auth"])
    if lvl == None:
        return 0
    return lvl

@bp.route("/")
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
    return render_template("product.html", product=product, auth=getAuthFromRequest())

@bp.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@bp.route("/logout", methods=["GET", "POST"])
def logout():
    request.cookies.pop("auth")
    

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
        return jsonify(token.token)

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run()