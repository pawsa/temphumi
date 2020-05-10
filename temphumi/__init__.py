"""
Main flask application code. The file provides the glue code expected
by the `flask` command.
"""

import os

from flask import Flask

def create_app(test_config=None):
    """Creates the app."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "measurements.sqlite")
    )

    if test_config is not None:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from temphumi.tseries import tseries  # pylint: disable=import-outside-toplevel
    from temphumi import static # pylint: disable=import-outside-toplevel

    tseries.connect_to_app(app)
    app.register_blueprint(static.bp)
    app.register_blueprint(tseries.bp, url_prefix='/measurements')
    return app
