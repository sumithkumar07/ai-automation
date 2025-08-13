import requests
import asyncio
from typing import Dict, Any, List, Optional
from .models import Integration, IntegrationCategory
import os

class IntegrationsEngine:
    """Engine for managing external integrations."""
    
    def __init__(self):
        self.integrations = self._load_integrations()
    
    def _load_integrations(self) -> Dict[str, Integration]:
        """Load available integrations."""
        integrations = {
            "slack": Integration(
                id="slack",
                name="Slack",
                description="Send messages, create channels, manage your Slack workspace",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/slack/slack-original.svg",
                category=IntegrationCategory.COMMUNICATION,
                auth_type="oauth2",
                actions=[
                    {"id": "send_message", "name": "Send Message", "description": "Send a message to a channel or user"},
                    {"id": "create_channel", "name": "Create Channel", "description": "Create a new channel"},
                ],
                triggers=[
                    {"id": "new_message", "name": "New Message", "description": "Trigger when a new message is posted"},
                ]
            ),
            "google_sheets": Integration(
                id="google_sheets",
                name="Google Sheets",
                description="Create, update, and manage Google Sheets data",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/google/google-original.svg",
                category=IntegrationCategory.PRODUCTIVITY,
                auth_type="oauth2",
                actions=[
                    {"id": "add_row", "name": "Add Row", "description": "Add a new row to a spreadsheet"},
                    {"id": "update_cell", "name": "Update Cell", "description": "Update a specific cell"},
                ],
                triggers=[
                    {"id": "new_row", "name": "New Row", "description": "Trigger when a new row is added"},
                ]
            ),
            "gmail": Integration(
                id="gmail",
                name="Gmail",
                description="Send emails, manage your Gmail inbox",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/google/google-original.svg",
                category=IntegrationCategory.COMMUNICATION,
                auth_type="oauth2",
                actions=[
                    {"id": "send_email", "name": "Send Email", "description": "Send an email"},
                    {"id": "create_draft", "name": "Create Draft", "description": "Create a draft email"},
                ],
                triggers=[
                    {"id": "new_email", "name": "New Email", "description": "Trigger when a new email is received"},
                ]
            ),
            "github": Integration(
                id="github",
                name="GitHub",
                description="Manage repositories, issues, and pull requests",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg",
                category=IntegrationCategory.DEVELOPMENT,
                auth_type="oauth2",
                actions=[
                    {"id": "create_issue", "name": "Create Issue", "description": "Create a new issue"},
                    {"id": "create_pr", "name": "Create Pull Request", "description": "Create a new pull request"},
                ],
                triggers=[
                    {"id": "new_commit", "name": "New Commit", "description": "Trigger when a new commit is pushed"},
                ]
            ),
            "stripe": Integration(
                id="stripe",
                name="Stripe",
                description="Handle payments, subscriptions, and customer data",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/stripe/stripe-original.svg",
                category=IntegrationCategory.FINANCE,
                auth_type="api_key",
                actions=[
                    {"id": "create_customer", "name": "Create Customer", "description": "Create a new customer"},
                    {"id": "create_charge", "name": "Create Charge", "description": "Create a new charge"},
                ],
                triggers=[
                    {"id": "payment_success", "name": "Payment Success", "description": "Trigger when a payment succeeds"},
                ]
            ),
            "openai": Integration(
                id="openai",
                name="OpenAI",
                description="Generate text, analyze content with AI",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/openai/openai-original.svg",
                category=IntegrationCategory.AI,
                auth_type="api_key",
                is_premium=True,
                actions=[
                    {"id": "generate_text", "name": "Generate Text", "description": "Generate text using GPT"},
                    {"id": "analyze_sentiment", "name": "Analyze Sentiment", "description": "Analyze sentiment of text"},
                ],
            ),
        }
        return integrations
    
    def get_all_integrations(self) -> List[Integration]:
        """Get all available integrations."""
        return list(self.integrations.values())
    
    def get_integration(self, integration_id: str) -> Optional[Integration]:
        """Get a specific integration by ID."""
        return self.integrations.get(integration_id)
    
    def get_integrations_by_category(self, category: IntegrationCategory) -> List[Integration]:
        """Get integrations by category."""
        return [integration for integration in self.integrations.values() 
                if integration.category == category]
    
    async def execute_action(self, integration_id: str, action_id: str, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an integration action."""
        integration = self.get_integration(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        # Mock execution for demo purposes
        # In a real implementation, this would call actual APIs
        result = {
            "status": "success",
            "integration": integration_id,
            "action": action_id,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        return result
    
    def validate_config(self, integration_id: str, config: Dict[str, Any]) -> bool:
        """Validate integration configuration."""
        integration = self.get_integration(integration_id)
        if not integration:
            return False
        
        # Basic validation - in real implementation, this would validate auth tokens, etc.
        required_fields = [field.get("name") for field in integration.config_fields if field.get("required", False)]
        return all(field in config for field in required_fields)

# Global instance
integrations_engine = IntegrationsEngine()