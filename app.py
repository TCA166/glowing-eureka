from flask import Flask, Blueprint, render_template
import db

bp = Blueprint("glowing-eureka", __name__)

@bp.route("/", methods=["GET"])
def products():
    with db.Session(db.engine) as session:
        stmt = db.select(db.product)
        query = [r for r in session.scalars(stmt) if not r.isDeleted]
    return render_template("products.html", products=query)

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run()