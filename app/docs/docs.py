from flask import Blueprint, redirect

docs = Blueprint('docs', __name__, static_folder='None')


@docs.route('/docs')
def api_docs():
    return redirect("https://studyhubapi.docs.apiary.io/", code=302)
