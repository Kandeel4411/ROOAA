import os

from flask import request, abort, current_app, redirect, url_for
from flask.blueprints import Blueprint
from werkzeug.exceptions import BadRequest

from rooaa.utils import image

from rooaa.celery import celery

upload = Blueprint("upload", __name__)


@upload.route("/api/v1/image", methods=["POST"])
def upload_image():
    """ Route to upload image for the Object detection model """

    try:
        image_json = request.get_json(force=True)
    except BadRequest as err:
        abort(
            status=400,
            description="Didn't receive JSON object or received incorrectly formatted JSON.",
        )

    # Required keys for the uploaded image
    filename = image_json.get("filename", None)
    data = image_json.get("data", None)

    if filename is None or data is None:
        abort(status=400, description="Missing required keys")

    # Decoding image
    img = image.decode_image_base64(data=data)
    if img is None:
        abort(status=400, description="Received incorrectly formatted base64 image")

    # Saving image temporarily on system
    try:
        image.save_image(
            path=current_app.config["UPLOAD_PATH"], binary_data=img, filename=filename
        )
    except OSError as err:
        print(f"{err}")
        abort(status=500)

    return redirect(
        url_for(endpoint="predict.detect_object", filename=filename), code=303
    )
