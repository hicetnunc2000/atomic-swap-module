import smartpy as sp
class FA12(sp.Contract):
    def __init__(self, admin):
        self.init(paused = False, balances = sp.big_map(tvalue = sp.TRecord(approvals = sp.TMap(sp.TAddress, sp.TNat), balance = sp.TNat)), administrator = admin, totalSupply = 0)

    @sp.entry_point
    def transfer(self, params):
        sp.verify((sp.sender == self.data.administrator) |
            (~self.data.paused &
                ((params.fro == sp.sender) |
                 (self.data.balances[params.fro].approvals[sp.sender] >= params.value))))
        self.addAddressIfNecessary(params.to)
        sp.verify(self.data.balances[params.fro].balance >= params.value)
        self.data.balances[params.fro].balance = sp.as_nat(self.data.balances[params.fro].balance - params.value)
        self.data.balances[params.to].balance += params.value
        sp.if (params.fro != sp.sender) & (self.data.administrator != sp.sender):
            self.data.balances[params.fro].approvals[sp.sender] = sp.as_nat(self.data.balances[params.fro].approvals[sp.sender] - params.value)

    @sp.entry_point
    def approve(self, params):
        sp.verify((sp.sender == self.data.administrator) |
                  (~self.data.paused & (params.f == sp.sender)))
        alreadyApproved = self.data.balances[params.f].approvals.get(params.t, 0)
        sp.verify((alreadyApproved == 0) | (params.amount == 0))
        self.data.balances[params.f].approvals[params.t] = params.amount

    @sp.entry_point
    def setPause(self, params):
        sp.verify(sp.sender == self.data.administrator)
        self.data.paused = params

    @sp.entry_point
    def setAdministrator(self, params):
        sp.verify(sp.sender == self.data.administrator)
        self.data.administrator = params

    @sp.entry_point
    def mint(self, params):
        sp.verify(sp.sender == self.data.administrator)
        self.addAddressIfNecessary(params.to)
        self.data.balances[params.to].balance += params.value
        self.data.totalSupply += params.value

    @sp.entry_point
    def burn(self, params):
        sp.verify(sp.sender == self.data.administrator)
        sp.verify(self.data.balances[params.address].balance >= params.amount)
        self.data.balances[params.address].balance = sp.as_nat(self.data.balances[params.address].balance - params.amount)
        self.data.totalSupply = sp.as_nat(self.data.totalSupply - params.amount)

    def addAddressIfNecessary(self, address):
        sp.if ~ self.data.balances.contains(address):
            self.data.balances[address] = sp.record(balance = 0, approvals = {})

    @sp.entry_point
    def getBalance(self, params):
        sp.transfer(self.data.balances[params.owner].balance, sp.tez(0), sp.contract(sp.TNat, params.target).open_some())

    @sp.entry_point
    def getAllowance(self, params):
        sp.transfer(self.data.balances[params.arg.owner].approvals[params.arg.spender], sp.tez(0), sp.contract(sp.TNat, params.target).open_some())

    @sp.entry_point
    def getTotalSupply(self, params):
        sp.transfer(self.data.totalSupply, sp.tez(0), sp.contract(sp.TNat, params.target).open_some())

    @sp.entry_point
    def getAdministrator(self, params):
        sp.transfer(self.data.administrator, sp.tez(0), sp.contract(sp.TAddress, params.target).open_some())
    
    @sp.entry_point
    def crzy(self, params):
        sp.verify (sp.amount >= sp.tez(5))
        sp.verify (sp.tez(sp.nat(params)) == sp.amount)


class SWAP(sp.Contract):
    def __init__(self, admin, interested_party, fa12, tk_amount, tz_amount):
        self.init(
            admin = admin,
            fa12 = fa12,
            interested_party = interested_party,
            tz_amount = sp.mutez(tz_amount),
            tk_amount = sp.nat(tk_amount),
            immutable = sp.bool(False)
            )
            
    @sp.entry_point
    def delegate(self, params):
        sp.verify(sp.sender == self.data.admin)
        sp.set_delegate(params.addr)
        
    @sp.entry_point
    def claim(self, params):
        sp.verify(sp.sender == self.data.interested_party)
        
        self.transfer(params)
        
    @sp.entry_point
    def retrieve(self, params):
        sp.verify((sp.balance == sp.tez(0)) & (sp.sender == self.data.admin))
        
        self.transfer(params)
        
    @sp.entry_point
    def withdraw(self, params):
        sp.verify(sp.sender == self.data.admin)
        sp.send(params.to, sp.mutez(params.amount))

    @sp.entry_point
    def interest(self, params):
        sp.verify(sp.amount >= self.data.tz_amount)
        sp.verify(sp.amount == sp.mutez(params))
        sp.verify(self.data.immutable == sp.bool(False))
        
        self.data.immutable = sp.bool(True)
        self.data.interested_party = sp.sender

    def transfer(self, params):
        arg = sp.TRecord(fro = sp.TAddress, to = sp.TAddress, value = sp.TNat)
        arg_inst = sp.record(fro = sp.to_address(sp.self), to = params, value = self.data.tk_amount)
        c = sp.contract(arg, self.data.fa12, entry_point="transfer").open_some()
        
        sp.transfer(arg_inst, sp.mutez(0), c)

@sp.add_test(name = "SWAP Tests")
def test():
    
    scenario = sp.test_scenario()
    scenario.h1("FA1.2 Atomic Swap")
    
    scenario.h3("Test wallets")
    
    addr1 = sp.test_account("test1")
    addr2 = sp.test_account("test2")
    scenario.show([addr1, addr2])
    
    scenario.h3("Initialize FA12")

    c0 = FA12(addr1.address)
    scenario.show([c0.address])
    scenario += c0

    scenario.h3("Mint")
    scenario += c0.mint(to=addr1.address, value=20000).run(sender=addr1)

    scenario.h3("Token owner initialize an atomic swap")
    c2 = SWAP(addr1.address, addr1.address, c0.address, 200, 200000000)
    
    scenario.show([c2.address])
    scenario += c2
    
    scenario.h3("Token owner gives permissions to SWAP smart contract")
    scenario += c0.transfer(fro=addr1.address, to=c2.address, value=200).run(sender=addr1)
 
    #scenario.h3("Test Retrieve")
    #scenario += c2.retrieve(addr1.address).run(sender=addr1)

    scenario.h3("An user fills the Swap Order")
    scenario += c2.interest(200000000).run(sender=addr2, amount=sp.mutez(200000000))
    
    scenario.h3("The very same user can manage those FA1.2 tokes through the Swap Contract")
    scenario += c2.claim(addr2.address).run(sender=addr2)
    scenario += c0

    scenario.h3("Initial party withdraw funds")
    scenario += c2.withdraw(to=addr1.address, amount=200000000).run(sender=addr1)
    
