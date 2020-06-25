# atomic-swap module

Ungrund Oracle v1.0.0 enables you to make HTTP Requests for a microsservice which interacts with the Tezos Blockchain. It provides you multiple routes in which you can configure it's sessions, making possible user's interactions to happen with FA1.2 Standard Tokens and other Smart Contracts.

requirements
```
Docker version 19.03.9 and Docker Machine version 0.16.2
```

build
```
docker image build -t atomic-swap:1.0 .
docker container run --publish 5001:5000 --detach --name atomic atomic-swap:1.0
```

delete container:
```
docker container rm --force atomic
```

# routes

access: https://localhost:5000/
you'll find routes documented

# next updates

- forge operations
- FA2
- modules fabric
- cryptographed requests/responses

# references

https://gitlab.com/tzip/tzip/-/blob/master/proposals/tzip-7/ManagedLedger.tz (FA1.2)
https://medium.com/@hicetnunc2000/ungrund-oracle-34d1fe0659a3

# donate
eth: 0xa0290385540aB98222d00547cb59a9E72A788Bf3
tz: tz1L6qEvhRFufA5KES6QJ48pvgvTrLcGUoLb
