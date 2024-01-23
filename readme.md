
# Relay for NEAR Protocol

Microservice to execute delegated transactions on NEAR Protocol.


Run in docker

```bash
docker run -d -v ./config.yml:/workdir/config.yml -p 7001:7001 neafiol2/near-relay:latest
```