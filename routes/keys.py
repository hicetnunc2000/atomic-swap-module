
from flask import request, session, make_response
from flask_restx import fields, Resource, Api, Namespace
from flask_cors import CORS, cross_origin
from werkzeug import FileStorage
from werkzeug.datastructures import ImmutableMultiDict
from pytezos import Contract, Key
from pytezos import pytezos
from pytezos.operation.result import OperationResult
from ast import literal_eval
from controllers.validate import Validate
#import redis
import requests
import urllib
import json
import os
import uuid

pytezos = pytezos

api = Namespace('keys', description='generate keys, activate, reveal')

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                       type=FileStorage, required=True)
upload_parser.add_argument('network', choices=('mainnet', 'carthagenet'))                      
# POST key configuration from faucet wallet

@api.route('/faucet')
@api.expect(upload_parser)
class faucet(Resource):
    
    @api.expect(type)
    def post(self):
        try:
            args = upload_parser.parse_args()

            uploaded_faucet = json.loads(args['file'].read())

            session['auth'] = 'faucet'
            session['faucet'] = uploaded_faucet
            session['network'] = args['network']

            v = Validate() 
            p = v.read_session(session)
            
            return p.key.public_key_hash()
        except:
            return 500

@api.route('/post_secret')
@api.doc(params = { 
    'secret' : 'wallet secret key', 
    'password' : 'wallet password', 
    'network' : 'mainnet / carthagenet' 
    })
class secret_key(Resource):
    def post(self):
        try:

            if (request.data.__len__() == 0):
                req = request.args.to_dict(flat=True)
                req['auth'] = 'secret'

                session['auth'] = 'secret'
                session['secret'] = req['secret']
                session['password'] = req['password']
                session['network'] = req['network']

            else:
                req = json.loads(request.data)
                session['auth'] = 'secret'
                session['secret'] = req['secret']
                session['password'] = req['password']
                session['network'] = req['network']
            
            v = Validate()
            p = v.read_session(session)
            
            return p.key.public_key_hash()
        except:
            return 500

@api.route('/test_session')
class test_session(Resource):
    def get(self):
        return session['secret']
