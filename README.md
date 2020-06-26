# atomic-swap module

Atomic Swap Module deploys and allows you to search for Atomic Swap Offerings related to FA1.2 tokens. Tezos and CoinList Hackaton.

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

access: https://localhost:5001/
you'll find routes documented

# next updates

- interoperability between different assets
- FA2 atomic swaps

# smart contracts
https://better-call.dev/carthagenet/KT1HnvCK8CvUDEzhozQzR5oX5WACEj2D254m/operations


