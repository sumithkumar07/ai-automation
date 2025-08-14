"""
🎯 AETHER AUTOMATION - SUBSCRIPTION API ROUTES
FastAPI routes for subscription management with Stripe integration
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from subscription_system import (
    get_subscription_manager, SubscriptionTier, BillingCycle, 
    SUBSCRIPTION_PLANS, SubscriptionStatus
)
from auth import get_current_active_user
from emergentintegrations.payments.stripe.checkout import CheckoutStatusResponse

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/subscription", tags=["Subscription"])

# Request/Response Models
class SubscriptionUpgradeRequest(BaseModel):
    tier: SubscriptionTier = Field(..., description="Subscription tier")
    billing_cycle: BillingCycle = Field(default=BillingCycle.MONTHLY, description="Billing cycle")
    origin_url: str = Field(..., description="Frontend origin URL for redirects")

class PaymentStatusRequest(BaseModel):
    session_id: str = Field(..., description="Stripe checkout session ID")

# Routes

@router.get("/plans")
async def get_subscription_plans():
    """Get all available subscription plans with pricing and features"""
    try:
        manager = get_subscription_manager()
        plans = manager.get_all_plans()
        
        return {
            "status": "success",
            "plans": plans,
            "trial_days": 7,
            "currency": "USD"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting subscription plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve subscription plans")

@router.get("/current")
async def get_current_subscription(current_user: dict = Depends(get_current_active_user)):
    """Get user's current subscription details"""
    try:
        user_id = current_user["user_id"]
        manager = get_subscription_manager()
        subscription = manager.get_user_subscription(user_id)
        usage_stats = manager.get_usage_stats(user_id)
        
        if not subscription:
            return {
                "status": "no_subscription",
                "message": "No subscription found",
                "trial_available": True
            }
        
        # Calculate days remaining for trial/subscription
        days_remaining = 0
        if subscription.get("expires_at"):
            expires_at = subscription["expires_at"]
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            days_remaining = max(0, (expires_at - datetime.utcnow()).days)
        
        response_data = {
            "status": "success",
            "subscription": {
                "id": subscription["_id"],
                "tier": subscription["tier"],
                "status": subscription["status"],
                "billing_cycle": subscription.get("billing_cycle"),
                "created_at": subscription["created_at"],
                "expires_at": subscription.get("expires_at"),
                "days_remaining": days_remaining,
                "is_trial": subscription["status"] == SubscriptionStatus.TRIAL,
                "usage_limits": subscription.get("usage_limits", {})
            },
            "usage": usage_stats
        }
        
        # Add trial information if in trial
        if subscription["status"] == SubscriptionStatus.TRIAL:
            response_data["subscription"]["trial_end"] = subscription.get("trial_end")
            response_data["subscription"]["trial_days_remaining"] = days_remaining
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Error getting current subscription for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve subscription details")

@router.get("/usage")
async def get_usage_statistics(current_user: dict = Depends(get_current_active_user)):
    """Get user's current usage statistics"""
    try:
        user_id = current_user["user_id"]
        manager = get_subscription_manager()
        usage_stats = manager.get_usage_stats(user_id)
        
        return {
            "status": "success",
            "usage": usage_stats,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting usage statistics for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage statistics")

@router.post("/upgrade")
async def create_subscription_upgrade(
    upgrade_request: SubscriptionUpgradeRequest,
    request: Request,
    current_user: dict = Depends(get_current_active_user)
):
    """Create Stripe checkout session for subscription upgrade"""
    try:
        user_id = current_user["user_id"]
        manager = get_subscription_manager()
        
        # Validate subscription tier
        if upgrade_request.tier not in SUBSCRIPTION_PLANS:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        
        # Get host URL for webhook
        host_url = str(request.base_url).rstrip('/')
        
        # Create checkout session
        checkout_data = await manager.create_subscription_checkout(
            user_id=user_id,
            tier=upgrade_request.tier,
            billing_cycle=upgrade_request.billing_cycle,
            origin_url=upgrade_request.origin_url.rstrip('/'),
            host_url=host_url
        )
        
        return {
            "status": "success",
            "checkout": checkout_data,
            "message": "Checkout session created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating subscription upgrade for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription upgrade")

@router.post("/payment/status")
async def check_payment_status(
    status_request: PaymentStatusRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_active_user)
):
    """Check payment status and process successful payments"""
    try:
        user_id = current_user["user_id"]
        manager = get_subscription_manager()
        
        # Get Stripe checkout instance
        stripe_checkout = manager.get_stripe_checkout("https://dummy-host.com")  # Host not used for status check
        
        # Check payment status with Stripe
        checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(
            status_request.session_id
        )
        
        response_data = {
            "status": "success",
            "session_id": status_request.session_id,
            "payment_status": checkout_status.payment_status,
            "checkout_status": checkout_status.status,
            "amount_total": checkout_status.amount_total,
            "currency": checkout_status.currency,
            "metadata": checkout_status.metadata
        }
        
        # Process successful payment in background
        if checkout_status.payment_status == "paid":
            background_tasks.add_task(
                manager.process_successful_payment,
                status_request.session_id
            )
            response_data["message"] = "Payment successful! Your subscription is being activated."
        elif checkout_status.status == "expired":
            response_data["message"] = "Payment session has expired. Please try again."
        else:
            response_data["message"] = "Payment is still being processed."
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Error checking payment status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@router.get("/check-limits/{usage_type}")
async def check_usage_limits(
    usage_type: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Check if user has reached usage limits for specific resource"""
    try:
        user_id = current_user["user_id"]
        manager = get_subscription_manager()
        limit_check = manager.check_usage_limit(user_id, usage_type)
        
        return {
            "status": "success",
            "usage_type": usage_type,
            "limit_check": limit_check
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking usage limits for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to check usage limits")

@router.post("/track-usage")
async def track_resource_usage(
    usage_data: Dict[str, Any],
    current_user: dict = Depends(get_current_active_user)
):
    """Track user's resource usage (internal API)"""
    try:
        user_id = current_user["user_id"]
        manager = get_subscription_manager()
        
        usage_type = usage_data.get("usage_type")
        amount = usage_data.get("amount", 1)
        
        if not usage_type:
            raise HTTPException(status_code=400, detail="usage_type is required")
        
        success = manager.track_usage(user_id, usage_type, amount)
        
        return {
            "status": "success" if success else "error",
            "usage_type": usage_type,
            "amount": amount,
            "message": "Usage tracked successfully" if success else "Failed to track usage"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error tracking usage for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to track usage")

@router.post("/webhook/stripe", include_in_schema=False)
async def stripe_webhook_handler(request: Request):
    """Handle Stripe webhooks for subscription events"""
    try:
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        manager = get_subscription_manager()
        stripe_checkout = manager.get_stripe_checkout("https://dummy-host.com")
        
        # Process webhook
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Handle different webhook events
        if webhook_response.event_type == "checkout.session.completed":
            # Process successful payment
            if webhook_response.payment_status == "paid":
                success = manager.process_successful_payment(webhook_response.session_id)
                if success:
                    logger.info(f"✅ Webhook processed successfully for session {webhook_response.session_id}")
                else:
                    logger.error(f"❌ Failed to process webhook for session {webhook_response.session_id}")
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "event_processed": True}
        )
        
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

# Helper function to create trial subscription on user registration
async def create_user_trial_subscription(user_id: str) -> Dict[str, Any]:
    """Helper function to create trial subscription for new users"""
    try:
        manager = get_subscription_manager()
        trial_subscription = manager.create_trial_subscription(user_id)
        logger.info(f"✅ Trial subscription created for new user {user_id}")
        return trial_subscription
    except Exception as e:
        logger.error(f"❌ Error creating trial for new user {user_id}: {e}")
        return {}

# Usage tracking decorators and middleware helpers
def track_workflow_creation(user_id: str):
    """Track workflow creation usage"""
    try:
        manager = get_subscription_manager()
        manager.track_usage(user_id, "workflows_created", 1)
    except Exception as e:
        logger.error(f"❌ Error tracking workflow creation: {e}")

def track_workflow_execution(user_id: str):
    """Track workflow execution usage"""
    try:
        manager = get_subscription_manager()
        manager.track_usage(user_id, "executions_run", 1)
    except Exception as e:
        logger.error(f"❌ Error tracking workflow execution: {e}")

def track_ai_request(user_id: str):
    """Track AI request usage"""
    try:
        manager = get_subscription_manager()
        manager.track_usage(user_id, "ai_requests", 1)
    except Exception as e:
        logger.error(f"❌ Error tracking AI request: {e}")

def check_usage_before_action(user_id: str, usage_type: str) -> bool:
    """Check usage limits before allowing an action"""
    try:
        manager = get_subscription_manager()
        limit_check = manager.check_usage_limit(user_id, usage_type)
        return limit_check.get("allowed", False)
    except Exception as e:
        logger.error(f"❌ Error checking usage limits: {e}")
        return False