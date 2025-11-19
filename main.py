import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Account, Profile, Transaction, Debt, Goal

app = FastAPI(title="Budgeting & Personal Finance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers
class IdResponse(BaseModel):
    id: str


def oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id format")


@app.get("/")
def read_root():
    return {"message": "Budgeting API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            # list collections
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# ============ Accounts & Profiles ============
@app.post("/accounts", response_model=IdResponse)
def create_account(payload: Account):
    new_id = create_document("account", payload)
    return {"id": new_id}


@app.get("/accounts")
def list_accounts():
    return get_documents("account")


@app.post("/profiles", response_model=IdResponse)
def create_profile(payload: Profile):
    # ensure account exists
    if db["account"].count_documents({"_id": oid(payload.account_id)}) == 0:
        raise HTTPException(404, detail="Account not found")
    new_id = create_document("profile", payload)
    return {"id": new_id}


@app.get("/profiles")
def list_profiles(account_id: Optional[str] = None):
    filt = {"account_id": account_id} if account_id else {}
    return get_documents("profile", filt)


# ============ Transactions ============
@app.post("/transactions", response_model=IdResponse)
def create_transaction(payload: Transaction):
    # minimal validation
    if db["account"].count_documents({"_id": oid(payload.account_id)}) == 0:
        raise HTTPException(404, detail="Account not found")
    if payload.profile_id:
        if db["profile"].count_documents({"_id": oid(payload.profile_id)}) == 0:
            raise HTTPException(404, detail="Profile not found")
    new_id = create_document("transaction", payload)
    return {"id": new_id}


@app.get("/transactions")
def list_transactions(account_id: str, profile_id: Optional[str] = None):
    filt = {"account_id": account_id}
    if profile_id is not None:
        filt["$or"] = [{"profile_id": profile_id}, {"shared": True}]
    return get_documents("transaction", filt)


# ============ Debts ============
@app.post("/debts", response_model=IdResponse)
def create_debt(payload: Debt):
    if db["account"].count_documents({"_id": oid(payload.account_id)}) == 0:
        raise HTTPException(404, detail="Account not found")
    new_id = create_document("debt", payload)
    return {"id": new_id}


@app.get("/debts")
def list_debts(account_id: str, profile_id: Optional[str] = None):
    filt = {"account_id": account_id}
    if profile_id is not None:
        filt["$or"] = [{"profile_id": profile_id}, {"profile_id": None}]
    return get_documents("debt", filt)


# ============ Goals ============
@app.post("/goals", response_model=IdResponse)
def create_goal(payload: Goal):
    if db["account"].count_documents({"_id": oid(payload.account_id)}) == 0:
        raise HTTPException(404, detail="Account not found")
    new_id = create_document("goal", payload)
    return {"id": new_id}


@app.get("/goals")
def list_goals(account_id: str, profile_id: Optional[str] = None):
    filt = {"account_id": account_id}
    if profile_id is not None:
        filt["$or"] = [{"profile_id": profile_id}, {"profile_id": None}]
    return get_documents("goal", filt)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
