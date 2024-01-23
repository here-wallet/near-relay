
# Relay for NEAR Protocol

Microservice to execute delegated transactions on NEAR Protocol.


1. Create file `config.yml` with content:

```yaml
replay_account:
  rpc_addr: "https://rpc.near.org"
  account_id: "bob.near"
  private_key:
    - "ed25519:...."
    - "ed25519:...."

auth_key: "notsecret"
```
2. Run in docker

```bash
docker run -d -v ./config.yml:/workdir/config.yml -p 7001:7001 neafiol2/near-relay:latest
```

3. Create transaction and sign with `auth_key`