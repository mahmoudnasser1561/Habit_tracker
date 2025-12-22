from flask import Flask
from src.routes import pages
from prometheus_flask_exporter import PrometheusMetrics

def create_app():
    app = Flask(__name__)
    app.register_blueprint(pages)

    metrics = PrometheusMetrics(app)
    
    return app