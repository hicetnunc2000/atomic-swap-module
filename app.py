from flask import Flask, session
from flask import jsonify
from flask import request, Blueprint
from flask_restx import fields, Resource, Api
from flask_cors import CORS, cross_origin

#from pytezos.rpc import tzkt
#from conseil.api import ConseilApi
from datetime import timedelta
import requests
import json
import time
import urllib
import sys

# ROUTES

from routes.atomic_swap import api as atomic_swap
from routes.keys import api as keys

app = Flask(__name__)
app.secret_key = 'session_key'

cors = CORS(app, supports_credentials=True)

api = Api()
api = Api(version = 'v1.0.0', 
          title = 'Atomic Swap Module', 
          description= 'On-chain FA1.2:Tezos Atomic Swap',
          contact='hicetnunc2000@protonmail.com')

# NAMESPACES

api.add_namespace(atomic_swap)
api.add_namespace(keys)

api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')