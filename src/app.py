#!/usr/bin/env python3
import asyncio
import base64
import json
import time
from hashlib import sha256
from typing import List

import base58
import ed25519
import uvicorn
from fastapi import FastAPI, HTTPException
from loguru import logger
from py_near.account import Account
from py_near.exceptions.provider import NotEnoughBalance
from py_near.models import DelegateActionModel
import yaml
from py_near_primitives import SignedDelegateAction
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

logger.add(
    "logs/replay_info.log",
    level="INFO",
    rotation="3 days",
    retention="15 days",
    compression="zip",
    enqueue=True,
)

with open("config.yml", "r") as f:
    CONFIG = yaml.safe_load(f)

app = FastAPI(title="NEAR Protocol relay service", version="0.1.1")
_relay_nc = Account(**CONFIG["replay_account"])


class RelayActionInModel(BaseModel):
    signature: str
    transaction: str

    def __str__(self):
        return f"{self.signature}.{self.transaction}"


class RelayInModel(BaseModel):
    sender_id: str
    actions: List[RelayActionInModel]
    authorisation: str


class RelayOutModel(BaseModel):
    hash: str


@app.post("/execute", response_model=RelayOutModel)
async def relay_handler(data: RelayInModel):
    sign = sha256()
    sign.update(data.sender_id.encode("utf8"))
    for a in data.actions:
        sign.update(str(a).encode("utf8"))
    sign.update(CONFIG["auth_key"].encode("utf8"))
    if sign.hexdigest() != data.authorisation:
        logger.info(
            f"Authorisation failed {data.sender_id}: {sign.hexdigest()} != {data.authorisation}"
        )
        raise HTTPException(status_code=403, detail="Authorisation failed")

    if not data.actions:
        raise HTTPException(status_code=400, detail="No actions found")

    call_actions = []
    for action in data.actions:
        signature = action.signature
        transaction = action.transaction
        delegate_action = base64.b64decode(transaction)
        delegate_action = DelegateActionModel.from_bytes(delegate_action[4:])
        delegate_action.public_key = delegate_action.public_key.split(":")[1]

        signed_da = SignedDelegateAction(
            delegate_action=delegate_action.near_delegate_action,
            signature=base58.b58decode(signature),
        )
        call_actions.append(signed_da)

    try:
        ts = time.time()
        logger.info(f"Delegate action by {data.sender_id} submitted")
        tr_hash = await _relay_nc.sign_and_submit_tx(
            data.sender_id, call_actions, nowait=True
        )
        for _ in range(5):
            await asyncio.sleep(10)
            try:
                await _relay_nc.provider.get_tx(tr_hash, data.sender_id)
                logger.info(
                    f"Delegate action {tr_hash} by {data.sender_id} executed ({time.time() - ts:.2f}s)"
                )
                return {"hash": tr_hash}
            except Exception:
                await asyncio.sleep(5)
        tr_hash = await _relay_nc.sign_and_submit_tx(
            data.sender_id, call_actions, nowait=True
        )
        return {"hash": tr_hash}
    except NotEnoughBalance:
        raise HTTPException(status_code=400, detail="Not enough balance")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=f"{e}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def check_keys():
    for pk in CONFIG["replay_account"]["private_key"]:
        pk_n = pk
        if isinstance(pk, str):
            pk = base58.b58decode(pk.replace("ed25519:", ""))

        private_key = ed25519.SigningKey(pk)
        public_key = base58.b58encode(
            private_key.get_verifying_key().to_bytes()
        ).decode("utf-8")
        k = await _relay_nc.provider.get_access_key(_relay_nc.account_id, public_key)
        if "error" in k:
            print(pk_n, "error")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7001, timeout_keep_alive=60)
