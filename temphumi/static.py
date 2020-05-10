"""
A blueprint serving static files for displaying collected
temperature and humidity data. Not expected to be useful in production.
"""

from flask import Blueprint, current_app, send_from_directory

bp = Blueprint('static', __name__)  # pylint: disable=C0103

@bp.route('/')
def serve_index():
    """Serve a static index."""
    return current_app.send_static_file('index.html')

@bp.route('/js/<path:path>')
def serve_js(path):
    """Serve js files"""
    return send_from_directory('static/js', path)
