"""
Database Schemas for Budgeting & Personal Finance App

Each Pydantic model corresponds to a MongoDB collection. The collection name
is the lowercase of the class name (e.g., Account -> "account").

Collections:
- Account: a single household account that can have multiple user profiles
- Profile: individual user profile under an account (like Netflix profiles)
- Transaction: income/expense entries, can be shared or tied to a profile
- Debt: track debts/loans with balances and due dates
- Goal: savings goals with target and progress
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import date, datetime


class Account(BaseModel):
    name: str = Field(..., description="Household or account name")
    email: Optional[str] = Field(None, description="Primary contact email for account owner")


class Profile(BaseModel):
    account_id: str = Field(..., description="Parent account ID")
    name: str = Field(..., description="Display name for the profile")
    color: Optional[str] = Field(None, description="Preferred avatar/accent color (e.g., #FF6A00)")
    emoji: Optional[str] = Field(None, description="Optional emoji for avatar")


class Transaction(BaseModel):
    account_id: str = Field(..., description="Parent account ID")
    profile_id: Optional[str] = Field(None, description="Profile ID if personal; null if shared")
    type: Literal["income", "expense"] = Field(..., description="Transaction type")
    amount: float = Field(..., gt=0, description="Positive amount in account currency")
    category: str = Field(..., description="Category name (e.g., Groceries, Salary)")
    date: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of transaction")
    note: Optional[str] = Field(None, description="Optional note")
    shared: bool = Field(False, description="If true, this is a shared household transaction")


class Debt(BaseModel):
    account_id: str = Field(..., description="Parent account ID")
    profile_id: Optional[str] = Field(None, description="Profile ID if personal; null/shared otherwise")
    creditor: str = Field(..., description="Name of creditor/lender")
    principal: float = Field(..., gt=0, description="Original principal amount")
    balance: float = Field(..., ge=0, description="Current outstanding balance")
    interest_rate: Optional[float] = Field(0, ge=0, description="APR as percentage (e.g., 19.99)")
    due_date: Optional[date] = Field(None, description="Next due date")
    status: Literal["open", "closed"] = Field("open", description="Debt status")


class Goal(BaseModel):
    account_id: str = Field(..., description="Parent account ID")
    profile_id: Optional[str] = Field(None, description="Profile ID if personal; null/shared otherwise")
    title: str = Field(..., description="Goal name (e.g., Emergency Fund)")
    target_amount: float = Field(..., gt=0, description="Target savings amount")
    current_amount: float = Field(0, ge=0, description="Current saved amount")
    deadline: Optional[date] = Field(None, description="Optional target date")
