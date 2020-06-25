# @crzypatchwork

from flask import Blueprint, request, session
from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult
from flask import Flask
from flask_restx import fields, Resource, Api, Namespace
from decimal import *

from controllers.validate import Validate

import requests
import urllib
import json

pytezos = pytezos
OperationResult = OperationResult
v = Validate()
api = Namespace('atomic_swap', description='publish and other entrypoints')

@api.route('/publish')
@api.doc({
    'fa12' : 'fa1.2 tokens kt address',
    'tk_amount' : 'tk amount',
    'tz_amount' : 'tz amount (mutez)'
})
class publish_swap(Resource):
    def post(self):

        #try:
        payload = v.read_requests(request)
        pytz = v.read_session(session)

        swap = Contract.from_file('./smart_contracts/atomic_swap.tz')
        op = pytz.origination(script=swap.script(storage= { 
                'admin': pytz.key.public_key_hash(), 
                "interested_party": pytz.key.public_key_hash(), 
                'fa12' : payload['fa12'], 
                'immutable': False, 
                'tk_amount' : payload['tk_amount'], 
                'tz_amount' : payload['tz_amount']})).fill().sign().inject(_async=False, num_blocks_wait=2)

        swapkt = OperationResult.originated_contracts(op)
        fa12 = pytz.contract(payload['fa12'])
        print([pytz.key.public_key_hash(), swapkt[0]])
        r = fa12.transfer({"from" : pytz.key.public_key_hash(), "to" : swapkt[0], 'value' : payload['tk_amount']}).inject()
            
        return [v.filter_response(op), r]


@api.route('/interest')
@api.doc({
    'swap' : 'swap kt address',
    'tz_amount' : 'tz amount (mutez)'
})
class interest(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            swap = pytz.contract(payload['swap_contract'])
            r = swap.interest(int(payload['tz_amount'])).with_amount(int(payload['tz_amount'])).inject()
            return r
        except:
            return 500

@api.route('/open_offers')
@api.doc({
    'fa12' : 'fa12 kt address'
})
class open_offers(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)

            atomic_sample = "KT1F67TPB9fa2LHo7Lipt21oztybXWT8D4W8"

            r_cartha = requests.get("https://api.better-call.dev/v1/contract/carthagenet/{}/same".format(atomic_sample))
            #r_main = requests.get("https://api.better-call.dev/v1/contract/mainnet/{}/same".format(atomic_sample))
            #print(r_cartha.content)   
            l = lambda e : {'address' : e['address'], 'network' : e['network']}
                
            r_cartha = json.loads(r_cartha.content)['contracts']
            #r_main = json.loads(r_main.content)['contracts']

            contracts = r_cartha
            #print(contracts.__len__())
            aux_arr = []
            for e in contracts:
                aux_obj = {}
                s = pytz.contract(e['address'])
                aux_obj = s.storage()
                #print(aux_obj['fa12'])

                if aux_obj['fa12'] == payload['fa12'] and aux_obj['immutable'] == False:
                    aux_obj['kt_address'] = e['address']
                    aux_obj['network'] = e['network']          
                    aux_arr.append(aux_obj)
            return aux_arr
        except:
            return 500

@api.route('/claim')
@api.doc({
    'swap' : 'fa12 kt address',
    'to' : 'tz or kt destination'
})
class claim(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)
            ci = pytz.contract(payload['swap'])
            r = ci.claim(payload['to']).inject()
            return r
        except:
            return 500


@api.route('/withdraw')
@api.doc({
    'swap' : 'swap kt address',
    'to' : 'tz or kt destination',
    'amount' : 'mutez amount'
})
class withdraw(Resource):
    def post(self):  
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)
            ci = pytz.contract(payload['swap'])
            r = ci.withdraw({"to" : payload['to'], "amount" : payload['amount']}).inject()
            return r
        except:
            return 500

@api.route('/retrieve')
@api.doc({
    'swap' : 'swap kt address',
    'to' : 'tz or kt destination'
})
class retrieve(Resource):
    def post(self):  
        try:   
            payload = v.read_requests(request)
            pytz = v.read_session(session)
            ci = pytz.contract(payload['swap'])
            r = ci.retrieve(payload['to']).inject()
            return r
        except:
            return 500

@api.route('/delegate')
@api.doc({
    'swap' : 'swap kt address',
    'to' : 'tz or kt destination'
})
class delegate(Resource):
    def post(self):
        try:
            payload = v.read_requests(request)
            pytz = v.read_session(session)
            ci = pytz.contract(payload['swap'])
            r = ci.delegate(payload['to']).inject()
            return r           
        except:
            return 500