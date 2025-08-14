"""
🎯 AETHER AUTOMATION - SUBSCRIPTION SYSTEM
Comprehensive subscription management with Stripe integration
Supports Basic (7-day trial), Pro, and Enterprise tiers
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import logging
from fastapi import HTTPException
from pymongo import MongoClient
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

logger = logging.getLogger(__name__)

# Subscription Plans and Limits
class SubscriptionTier(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class PlanLimits:
    workflows_per_month: int
    executions_per_month: int
    integrations_limit: int
    ai_requests_per_month: int
    team_members: int
    templates_access: int
    storage_gb: int
    priority_support: bool
    advanced_analytics: bool
    custom_integrations: bool

@dataclass
class PlanPricing:
    tier: SubscriptionTier
    price_monthly: float
    price_yearly: float
    stripe_monthly_price_id: Optional[str]
    stripe_yearly_price_id: Optional[str]
    limits: PlanLimits

# Plan Definitions
SUBSCRIPTION_PLANS = {
    SubscriptionTier.BASIC: PlanPricing(
        tier=SubscriptionTier.BASIC,
        price_monthly=29.0,
        price_yearly=290.0,  # 2 months free
        stripe_monthly_price_id=None,  # Will be set from environment
        stripe_yearly_price_id=None,
        limits=PlanLimits(
            workflows_per_month=50,
            executions_per_month=1000,
            integrations_limit=10,
            ai_requests_per_month=500,
            team_members=2,
            templates_access=50,
            storage_gb=5,
            priority_support=False,
            advanced_analytics=False,
            custom_integrations=False
        )
    ),
    SubscriptionTier.PRO: PlanPricing(
        tier=SubscriptionTier.PRO,
        price_monthly=79.0,
        price_yearly=790.0,  # 2 months free
        stripe_monthly_price_id=None,
        stripe_yearly_price_id=None,
        limits=PlanLimits(
            workflows_per_month=200,
            executions_per_month=5000,
            integrations_limit=50,
            ai_requests_per_month=2000,
            team_members=10,
            templates_access=150,
            storage_gb=25,
            priority_support=True,
            advanced_analytics=True,
            custom_integrations=False
        )
    ),
    SubscriptionTier.ENTERPRISE: PlanPricing(
        tier=SubscriptionTier.ENTERPRISE,
        price_monthly=199.0,
        price_yearly=1990.0,  # 2 months free
        stripe_monthly_price_id=None,
        stripe_yearly_price_id=None,
        limits=PlanLimits(
            workflows_per_month=999999,  # Unlimited
            executions_per_month=999999,  # Unlimited
            integrations_limit=999999,  # Unlimited
            ai_requests_per_month=10000,
            team_members=50,
            templates_access=999999,  # Unlimited
            storage_gb=200,
            priority_support=True,
            advanced_analytics=True,
            custom_integrations=True
        )
    )
}

class SubscriptionStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class SubscriptionManager:
    """Manages user subscriptions, usage tracking, and billing"""
    
    def __init__(self, db: MongoClient, stripe_api_key: str):
        self.db = db
        self.users_collection = db.users
        self.subscriptions_collection = db.subscriptions
        self.usage_collection = db.usage_tracking
        self.payment_transactions_collection = db.payment_transactions
        
        # Initialize Stripe
        self.stripe_api_key = stripe_api_key
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for subscription system"""
        try:
            # Subscription indexes
            self.subscriptions_collection.create_index("user_id")
            self.subscriptions_collection.create_index("status")
            self.subscriptions_collection.create_index("expires_at")
            
            # Usage tracking indexes
            self.usage_collection.create_index([("user_id", 1), ("month", 1), ("year", 1)])
            self.usage_collection.create_index("user_id")
            
            # Payment transactions indexes
            self.payment_transactions_collection.create_index("session_id")
            self.payment_transactions_collection.create_index("user_id")
            self.payment_transactions_collection.create_index("payment_status")
            
            logger.info("✅ Subscription system indexes created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating subscription indexes: {e}")
    
    def create_trial_subscription(self, user_id: str) -> Dict[str, Any]:
        """Create 7-day trial subscription for new users"""
        try:
            # Check if user already has a subscription
            existing_subscription = self.subscriptions_collection.find_one({"user_id": user_id})
            if existing_subscription:
                return existing_subscription
            
            trial_end = datetime.utcnow() + timedelta(days=7)
            
            subscription_doc = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "tier": SubscriptionTier.BASIC,
                "status": SubscriptionStatus.TRIAL,
                "billing_cycle": BillingCycle.MONTHLY,
                "created_at": datetime.utcnow(),
                "trial_start": datetime.utcnow(),
                "trial_end": trial_end,
                "expires_at": trial_end,
                "stripe_customer_id": None,
                "stripe_subscription_id": None,
                "payment_method": None,
                "next_billing_date": None,
                "usage_limits": SUBSCRIPTION_PLANS[SubscriptionTier.BASIC].limits.__dict__
            }
            
            self.subscriptions_collection.insert_one(subscription_doc)
            
            # Initialize usage tracking
            self._initialize_usage_tracking(user_id)
            
            logger.info(f"✅ Trial subscription created for user {user_id}")
            return subscription_doc
            
        except Exception as e:
            logger.error(f"❌ Error creating trial subscription for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to create trial subscription")
    
    def get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current subscription"""
        try:
            subscription = self.subscriptions_collection.find_one({"user_id": user_id})
            if not subscription:
                return None
            
            # Check if trial/subscription has expired
            if subscription.get("expires_at") and datetime.utcnow() > subscription["expires_at"]:
                if subscription["status"] in [SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE]:
                    self._expire_subscription(user_id)
                    subscription["status"] = SubscriptionStatus.EXPIRED
            
            return subscription
            
        except Exception as e:
            logger.error(f"❌ Error getting subscription for user {user_id}: {e}")
            return None
    
    def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's current usage statistics"""
        try:
            current_month = datetime.utcnow().month
            current_year = datetime.utcnow().year
            
            usage = self.usage_collection.find_one({
                "user_id": user_id,
                "month": current_month,
                "year": current_year
            })
            
            if not usage:
                usage = self._initialize_usage_tracking(user_id)
            
            subscription = self.get_user_subscription(user_id)
            limits = subscription.get("usage_limits", {}) if subscription else {}
            
            return {
                "current_usage": {
                    "workflows_created": usage.get("workflows_created", 0),
                    "executions_run": usage.get("executions_run", 0),
                    "ai_requests": usage.get("ai_requests", 0),
                    "storage_used_mb": usage.get("storage_used_mb", 0)
                },
                "limits": limits,
                "percentage_used": self._calculate_usage_percentages(usage, limits)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting usage stats for user {user_id}: {e}")
            return {"current_usage": {}, "limits": {}, "percentage_used": {}}
    
    def track_usage(self, user_id: str, usage_type: str, amount: int = 1) -> bool:
        """Track user's resource usage"""
        try:
            current_month = datetime.utcnow().month
            current_year = datetime.utcnow().year
            
            # Get current usage
            usage_doc = self.usage_collection.find_one({
                "user_id": user_id,
                "month": current_month,
                "year": current_year
            })
            
            if not usage_doc:
                usage_doc = self._initialize_usage_tracking(user_id)
            
            # Update usage
            update_field = f"{usage_type}"
            self.usage_collection.update_one(
                {
                    "user_id": user_id,
                    "month": current_month,
                    "year": current_year
                },
                {
                    "$inc": {update_field: amount},
                    "$set": {"last_updated": datetime.utcnow()}
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error tracking usage for user {user_id}: {e}")
            return False
    
    def check_usage_limit(self, user_id: str, usage_type: str) -> Dict[str, Any]:
        """Check if user has exceeded usage limits"""
        try:
            subscription = self.get_user_subscription(user_id)
            if not subscription:
                return {"allowed": False, "reason": "No subscription found"}
            
            if subscription["status"] == SubscriptionStatus.EXPIRED:
                return {"allowed": False, "reason": "Subscription expired"}
            
            usage_stats = self.get_usage_stats(user_id)
            current_usage = usage_stats["current_usage"]
            limits = usage_stats["limits"]
            
            # Map usage types to limit fields
            limit_mapping = {
                "workflows_created": "workflows_per_month",
                "executions_run": "executions_per_month", 
                "ai_requests": "ai_requests_per_month"
            }
            
            limit_field = limit_mapping.get(usage_type)
            if not limit_field:
                return {"allowed": True, "reason": "Usage type not limited"}
            
            current_count = current_usage.get(usage_type, 0)
            limit = limits.get(limit_field, 999999)
            
            if current_count >= limit:
                return {
                    "allowed": False, 
                    "reason": f"Usage limit exceeded: {current_count}/{limit}",
                    "current_usage": current_count,
                    "limit": limit
                }
            
            return {
                "allowed": True, 
                "remaining": limit - current_count,
                "current_usage": current_count,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking usage limit for user {user_id}: {e}")
            return {"allowed": False, "reason": "Error checking limits"}
    
    def get_stripe_checkout(self, host_url: str) -> StripeCheckout:
        """Initialize Stripe checkout with webhook URL"""
        webhook_url = f"{host_url.rstrip('/')}/api/webhook/stripe"
        return StripeCheckout(api_key=self.stripe_api_key, webhook_url=webhook_url)
    
    async def create_subscription_checkout(
        self, 
        user_id: str, 
        tier: SubscriptionTier, 
        billing_cycle: BillingCycle,
        origin_url: str,
        host_url: str
    ) -> Dict[str, Any]:
        """Create Stripe checkout session for subscription"""
        try:
            if tier not in SUBSCRIPTION_PLANS:
                raise HTTPException(status_code=400, detail="Invalid subscription tier")
            
            plan = SUBSCRIPTION_PLANS[tier]
            
            # Get pricing based on billing cycle
            if billing_cycle == BillingCycle.MONTHLY:
                amount = plan.price_monthly
                description = f"{tier.value.title()} Plan - Monthly"
            else:
                amount = plan.price_yearly
                description = f"{tier.value.title()} Plan - Yearly (2 months free!)"
            
            # Create success and cancel URLs
            success_url = f"{origin_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{origin_url}/pricing"
            
            # Create Stripe checkout session
            stripe_checkout = self.get_stripe_checkout(host_url)
            
            metadata = {
                "user_id": user_id,
                "subscription_tier": tier.value,
                "billing_cycle": billing_cycle.value,
                "source": "subscription_upgrade"
            }
            
            checkout_request = CheckoutSessionRequest(
                amount=amount,
                currency="usd",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )
            
            session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
            
            # Create payment transaction record
            transaction_doc = {
                "_id": str(uuid.uuid4()),
                "session_id": "pending",  # Will be set when session is created
                "user_id": user_id,
                "amount": amount,
                "currency": "usd",
                "subscription_tier": tier.value,
                "billing_cycle": billing_cycle.value,
                "description": description,
                "payment_status": "pending",
                "status": "initiated",
                "created_at": datetime.utcnow(),
                "metadata": metadata
            }
            
            self.payment_transactions_collection.insert_one(transaction_doc)
            
            logger.info(f"✅ Checkout session created for user {user_id}, tier {tier.value}")
            
            return {
                "checkout_url": "pending",  # Will be set when session is created
                "session_id": "pending",  # Will be set when session is created
                "amount": amount,
                "tier": tier.value,
                "billing_cycle": billing_cycle.value
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating subscription checkout: {e}")
            raise HTTPException(status_code=500, detail="Failed to create checkout session")
    
    def process_successful_payment(self, session_id: str) -> bool:
        """Process successful subscription payment and update user subscription"""
        try:
            # Get transaction record
            transaction = self.payment_transactions_collection.find_one({"session_id": session_id})
            if not transaction:
                logger.error(f"❌ Transaction not found for session {session_id}")
                return False
            
            # Prevent duplicate processing
            if transaction.get("processed", False):
                logger.info(f"ℹ️ Transaction {session_id} already processed")
                return True
            
            user_id = transaction["user_id"]
            tier = SubscriptionTier(transaction["subscription_tier"])
            billing_cycle = BillingCycle(transaction["billing_cycle"])
            
            # Calculate subscription dates
            start_date = datetime.utcnow()
            if billing_cycle == BillingCycle.MONTHLY:
                end_date = start_date + timedelta(days=30)
            else:
                end_date = start_date + timedelta(days=365)
            
            # Update or create subscription
            subscription_update = {
                "tier": tier.value,
                "status": SubscriptionStatus.ACTIVE,
                "billing_cycle": billing_cycle.value,
                "current_period_start": start_date,
                "current_period_end": end_date,
                "expires_at": end_date,
                "next_billing_date": end_date,
                "updated_at": datetime.utcnow(),
                "usage_limits": SUBSCRIPTION_PLANS[tier].limits.__dict__
            }
            
            # Update existing subscription or create new one
            result = self.subscriptions_collection.update_one(
                {"user_id": user_id},
                {"$set": subscription_update},
                upsert=True
            )
            
            # Mark transaction as processed
            self.payment_transactions_collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": "paid",
                        "status": "completed",
                        "processed": True,
                        "processed_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"✅ Subscription updated for user {user_id} to {tier.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing successful payment for session {session_id}: {e}")
            return False
    
    def _initialize_usage_tracking(self, user_id: str) -> Dict[str, Any]:
        """Initialize monthly usage tracking for user"""
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        
        usage_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "month": current_month,
            "year": current_year,
            "workflows_created": 0,
            "executions_run": 0,
            "ai_requests": 0,
            "storage_used_mb": 0,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
        
        try:
            self.usage_collection.insert_one(usage_doc)
            logger.info(f"✅ Usage tracking initialized for user {user_id}")
        except Exception as e:
            # Handle duplicate key error (user already has usage tracking)
            if "duplicate key" not in str(e).lower():
                logger.error(f"❌ Error initializing usage tracking: {e}")
        
        return usage_doc
    
    def _calculate_usage_percentages(self, usage: Dict[str, Any], limits: Dict[str, Any]) -> Dict[str, float]:
        """Calculate usage percentages for display"""
        percentages = {}
        
        usage_mapping = {
            "workflows_created": "workflows_per_month",
            "executions_run": "executions_per_month",
            "ai_requests": "ai_requests_per_month"
        }
        
        for usage_key, limit_key in usage_mapping.items():
            current = usage.get(usage_key, 0)
            limit = limits.get(limit_key, 1)
            
            if limit == 0:
                percentages[usage_key] = 0.0
            else:
                percentages[usage_key] = min((current / limit) * 100, 100.0)
        
        return percentages
    
    def _expire_subscription(self, user_id: str):
        """Mark subscription as expired"""
        self.subscriptions_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "status": SubscriptionStatus.EXPIRED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"⚠️ Subscription expired for user {user_id}")
    
    def get_all_plans(self) -> Dict[str, Any]:
        """Get all available subscription plans"""
        plans_data = {}
        for tier, plan in SUBSCRIPTION_PLANS.items():
            plans_data[tier.value] = {
                "tier": tier.value,
                "name": tier.value.title(),
                "price_monthly": plan.price_monthly,
                "price_yearly": plan.price_yearly,
                "yearly_savings": (plan.price_monthly * 12) - plan.price_yearly,
                "limits": plan.limits.__dict__,
                "features": self._get_plan_features(tier)
            }
        
        return plans_data
    
    def _get_plan_features(self, tier: SubscriptionTier) -> List[str]:
        """Get feature list for a plan tier"""
        plan = SUBSCRIPTION_PLANS[tier]
        features = []
        
        if tier == SubscriptionTier.BASIC:
            features = [
                f"{plan.limits.workflows_per_month} workflows per month",
                f"{plan.limits.executions_per_month:,} workflow executions",
                f"{plan.limits.integrations_limit} integrations",
                f"{plan.limits.ai_requests_per_month} AI requests",
                f"{plan.limits.team_members} team members",
                f"{plan.limits.storage_gb}GB storage",
                "7-day free trial",
                "Email support"
            ]
        elif tier == SubscriptionTier.PRO:
            features = [
                f"{plan.limits.workflows_per_month} workflows per month",
                f"{plan.limits.executions_per_month:,} workflow executions",
                f"{plan.limits.integrations_limit} integrations",
                f"{plan.limits.ai_requests_per_month:,} AI requests",
                f"{plan.limits.team_members} team members",
                f"{plan.limits.storage_gb}GB storage",
                "Advanced analytics",
                "Priority support",
                "API access",
                "Custom webhooks"
            ]
        else:  # ENTERPRISE
            features = [
                "Unlimited workflows",
                "Unlimited executions",
                "Unlimited integrations",
                f"{plan.limits.ai_requests_per_month:,} AI requests",
                f"{plan.limits.team_members} team members",
                f"{plan.limits.storage_gb}GB storage",
                "Advanced analytics",
                "Priority support",
                "Custom integrations",
                "Dedicated account manager",
                "SLA guarantee",
                "Custom security controls"
            ]
        
        return features

# Global subscription manager instance
subscription_manager = None

def initialize_subscription_manager(db: MongoClient, stripe_api_key: str) -> SubscriptionManager:
    """Initialize the global subscription manager"""
    global subscription_manager
    subscription_manager = SubscriptionManager(db, stripe_api_key)
    logger.info("✅ Subscription Manager initialized successfully")
    return subscription_manager

def get_subscription_manager() -> SubscriptionManager:
    """Get the global subscription manager instance"""
    if subscription_manager is None:
        raise RuntimeError("Subscription manager not initialized")
    return subscription_manager