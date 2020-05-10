"""
Serves temperature and humidity time series.
"""

from flask import Blueprint, current_app, g, jsonify

from temphumi.tseries import seriesstorage

bp = Blueprint('tseries', __name__)  # pylint: disable=C0103

def get_storage():
    """Checks if the global object associated with the app context
    has the storage associated with it. If it does not, the action
    creates one.
    """
    if "tseries_db" not in g:
        g.tseries_db = seriesstorage.Storage(current_app.config["DATABASE"])
    return g.tseries_db

def release_storage(e=None):  # pylint: disable=W0613,C0103
    """
    Releases the storage associated with the app context by
    the blueprint.
    """
    storage = g.pop("tseries_db", None)
    if storage is not None:
        storage.close()

def connect_to_app(app):
    """
    Connects the blueprint to the app.  It registers an appcontext
    teardown action to release the resources.
    """
    app.teardown_appcontext(release_storage)


@bp.route('/<int:tstart>,<int:tend>')
def measurements(tstart, tend):
    """
    Serve the dynamic measurement data. tstart and tend are seconds
    since 1970-01-01 00:00:00 UTC.
    """
    retlist = []
    storage = get_storage()
    has_prev = storage.has_before(tstart)
    has_more = storage.has_after(tend)
    for pstamp, data in storage.read_set(tstart, tend):
        data.update({'dt': pstamp})
        retlist.append(data)

    return jsonify(
        {
            'data': retlist,
            'has_prev': has_prev,
            'has_more': has_more
        })
