# -*- coding: utf-8 -*-

import os
import json

from flask import session
from pytezos import pytezos, Key

# Validate different possible ways of Sessions concerning key's configurations 
# and Requests that can be presented by users

class Validate():
    def __init__(self):
        pass
        
    # if session is not set check redis session
    # redis impementation v1.1.0

    def read_session(self, sess):

        if (sess['auth'] == 'faucet'):
            return self.read_faucet(sess)
        if (sess['auth'] == 'mnemonic'):
            return self.read_mnemonic(sess)
        if (sess['auth'] == 'secret'):
            return self.read_secret(sess)
  
        
    def read_secret(self, sess):
        k = Key.from_encoded_key(sess['secret'], passphrase = sess['password'])
        p = pytezos.using(key = k, shell = sess['network'])

        print(k.public_key_hash())

        return p
    

    def read_requests(self, request):
        if (request.data.__len__() == 0):
            return request.args.__dict__()
        else:
            return json.loads(request.data)

    # if operation is completed, returns response object with the following properties

    def filter_response(self, response):
        
        ret = {}
        #print(response)
        if (response['contents'][0]['kind'] == 'origination'):
            ret['balance_updates'] = response['contents'][0]['metadata']['operation_result']['balance_updates']
            ret['originated_kt'] = response['contents'][0]['metadata']['operation_result']['originated_contracts'][0]
        else: 
            print(response['contents'])
        
        ret['hash'] = response['hash']
        ret['protocol'] = response['protocol']
        ret['kind'] = response['contents'][0]['kind']
        ret['source'] = response['contents'][0]['source']
        ret['fee'] = response['contents'][0]['fee']
        ret['counter'] = response['contents'][0]['counter']
        ret['gas_limit'] = response['contents'][0]['gas_limit']

        return ret