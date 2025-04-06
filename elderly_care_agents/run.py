from flask import Flask
from dashboard.routes import dashboard_bp

app = Flask(__name__)

app.register_blueprint(dashboard_bp, url_prefix='/')

if __name__ == "__main__":
    app.run(debug=True)
