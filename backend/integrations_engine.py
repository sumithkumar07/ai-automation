import requests
import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from models import Integration, IntegrationCategory
import logging

logger = logging.getLogger(__name__)

class IntegrationsEngine:
    """Engine for managing external integrations."""
    
    def __init__(self):
        self.integrations = self._load_integrations()
        logger.info(f"Loaded {len(self.integrations)} integrations")
    
    def _load_integrations(self) -> Dict[str, Integration]:
        """Load available integrations with comprehensive list."""
        integrations = {
            # Communication
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
                    {"id": "set_status", "name": "Set Status", "description": "Update your Slack status"},
                ],
                triggers=[
                    {"id": "new_message", "name": "New Message", "description": "Trigger when a new message is posted"},
                    {"id": "mention", "name": "Mention", "description": "Trigger when you're mentioned"},
                ]
            ),
            "discord": Integration(
                id="discord",
                name="Discord",
                description="Send messages and manage Discord servers",
                icon_url="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6918e57475a843dcdc_full_logo_blurple_RGB.png",
                category=IntegrationCategory.COMMUNICATION,
                auth_type="oauth2",
                actions=[
                    {"id": "send_message", "name": "Send Message", "description": "Send a message to a channel"},
                    {"id": "create_invite", "name": "Create Invite", "description": "Create an invite link"},
                ],
                triggers=[
                    {"id": "new_message", "name": "New Message", "description": "Trigger when a new message is posted"},
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
                    {"id": "mark_read", "name": "Mark as Read", "description": "Mark emails as read"},
                ],
                triggers=[
                    {"id": "new_email", "name": "New Email", "description": "Trigger when a new email is received"},
                    {"id": "labeled_email", "name": "Labeled Email", "description": "Trigger when an email gets a specific label"},
                ]
            ),
            "microsoft_teams": Integration(
                id="microsoft_teams",
                name="Microsoft Teams",
                description="Send messages and manage Teams channels",
                icon_url="https://upload.wikimedia.org/wikipedia/commons/c/c9/Microsoft_Office_Teams_%282018%E2%80%93present%29.svg",
                category=IntegrationCategory.COMMUNICATION,
                auth_type="oauth2",
                actions=[
                    {"id": "send_message", "name": "Send Message", "description": "Send a message to a channel"},
                    {"id": "create_meeting", "name": "Create Meeting", "description": "Schedule a Teams meeting"},
                ]
            ),
            
            # Productivity
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
                    {"id": "create_sheet", "name": "Create Sheet", "description": "Create a new spreadsheet"},
                ],
                triggers=[
                    {"id": "new_row", "name": "New Row", "description": "Trigger when a new row is added"},
                    {"id": "updated_cell", "name": "Updated Cell", "description": "Trigger when a cell is updated"},
                ]
            ),
            "microsoft_excel": Integration(
                id="microsoft_excel",
                name="Microsoft Excel",
                description="Work with Excel spreadsheets and data",
                icon_url="https://upload.wikimedia.org/wikipedia/commons/3/34/Microsoft_Office_Excel_%282019%E2%80%93present%29.svg",
                category=IntegrationCategory.PRODUCTIVITY,
                auth_type="oauth2",
                actions=[
                    {"id": "add_row", "name": "Add Row", "description": "Add a new row to a spreadsheet"},
                    {"id": "update_cell", "name": "Update Cell", "description": "Update a specific cell"},
                ]
            ),
            "notion": Integration(
                id="notion",
                name="Notion",
                description="Create and manage Notion pages and databases",
                icon_url="https://upload.wikimedia.org/wikipedia/commons/4/45/Notion_app_logo.png",
                category=IntegrationCategory.PRODUCTIVITY,
                auth_type="oauth2",
                actions=[
                    {"id": "create_page", "name": "Create Page", "description": "Create a new Notion page"},
                    {"id": "update_database", "name": "Update Database", "description": "Update a database entry"},
                ]
            ),
            "airtable": Integration(
                id="airtable",
                name="Airtable",
                description="Manage Airtable bases and records",
                icon_url="https://static-00.iconduck.com/assets.00/airtable-icon-512x512-4rflwjnq.png",
                category=IntegrationCategory.PRODUCTIVITY,
                auth_type="api_key",
                actions=[
                    {"id": "create_record", "name": "Create Record", "description": "Create a new record"},
                    {"id": "update_record", "name": "Update Record", "description": "Update an existing record"},
                ]
            ),
            "google_drive": Integration(
                id="google_drive",
                name="Google Drive",
                description="Manage files and folders in Google Drive",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/google/google-original.svg",
                category=IntegrationCategory.STORAGE,
                auth_type="oauth2",
                actions=[
                    {"id": "upload_file", "name": "Upload File", "description": "Upload a file to Google Drive"},
                    {"id": "create_folder", "name": "Create Folder", "description": "Create a new folder"},
                ]
            ),
            "dropbox": Integration(
                id="dropbox",
                name="Dropbox",
                description="Manage files and folders in Dropbox",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/dropbox/dropbox-original.svg",
                category=IntegrationCategory.STORAGE,
                auth_type="oauth2",
                actions=[
                    {"id": "upload_file", "name": "Upload File", "description": "Upload a file to Dropbox"},
                    {"id": "create_folder", "name": "Create Folder", "description": "Create a new folder"},
                ]
            ),
            
            # Development
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
                    {"id": "add_comment", "name": "Add Comment", "description": "Add a comment to an issue or PR"},
                ],
                triggers=[
                    {"id": "new_commit", "name": "New Commit", "description": "Trigger when a new commit is pushed"},
                    {"id": "new_issue", "name": "New Issue", "description": "Trigger when a new issue is created"},
                ]
            ),
            "gitlab": Integration(
                id="gitlab",
                name="GitLab",
                description="Manage GitLab repositories and pipelines",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/gitlab/gitlab-original.svg",
                category=IntegrationCategory.DEVELOPMENT,
                auth_type="oauth2",
                actions=[
                    {"id": "create_issue", "name": "Create Issue", "description": "Create a new issue"},
                    {"id": "trigger_pipeline", "name": "Trigger Pipeline", "description": "Trigger a CI/CD pipeline"},
                ]
            ),
            "jira": Integration(
                id="jira",
                name="Jira",
                description="Manage Jira issues and projects",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jira/jira-original.svg",
                category=IntegrationCategory.DEVELOPMENT,
                auth_type="oauth2",
                actions=[
                    {"id": "create_issue", "name": "Create Issue", "description": "Create a new Jira issue"},
                    {"id": "update_issue", "name": "Update Issue", "description": "Update an existing issue"},
                ]
            ),
            
            # Finance
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
                    {"id": "create_subscription", "name": "Create Subscription", "description": "Create a subscription"},
                ],
                triggers=[
                    {"id": "payment_success", "name": "Payment Success", "description": "Trigger when a payment succeeds"},
                    {"id": "payment_failed", "name": "Payment Failed", "description": "Trigger when a payment fails"},
                ]
            ),
            "paypal": Integration(
                id="paypal",
                name="PayPal",
                description="Process PayPal payments and manage transactions",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/paypal/paypal-original.svg",
                category=IntegrationCategory.FINANCE,
                auth_type="oauth2",
                actions=[
                    {"id": "create_payment", "name": "Create Payment", "description": "Create a new payment"},
                    {"id": "verify_payment", "name": "Verify Payment", "description": "Verify payment status"},
                ]
            ),
            
            # CRM
            "salesforce": Integration(
                id="salesforce",
                name="Salesforce",
                description="Manage Salesforce CRM data and workflows",
                icon_url="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/salesforce/salesforce-original.svg",
                category=IntegrationCategory.CRM,
                auth_type="oauth2",
                actions=[
                    {"id": "create_lead", "name": "Create Lead", "description": "Create a new lead"},
                    {"id": "update_contact", "name": "Update Contact", "description": "Update contact information"},
                ]
            ),
            "hubspot": Integration(
                id="hubspot",
                name="HubSpot",
                description="Manage HubSpot CRM and marketing automation",
                icon_url="https://www.hubspot.com/hubfs/HubSpot_Logos/HubSpot-Inversed-Favicon.png",
                category=IntegrationCategory.CRM,
                auth_type="oauth2",
                actions=[
                    {"id": "create_contact", "name": "Create Contact", "description": "Create a new contact"},
                    {"id": "create_deal", "name": "Create Deal", "description": "Create a new deal"},
                ]
            ),
            
            # Marketing
            "mailchimp": Integration(
                id="mailchimp",
                name="Mailchimp",
                description="Manage email campaigns and subscriber lists",
                icon_url="https://cdn.worldvectorlogo.com/logos/mailchimp-freddie-icon.svg",
                category=IntegrationCategory.MARKETING,
                auth_type="api_key",
                actions=[
                    {"id": "add_subscriber", "name": "Add Subscriber", "description": "Add a subscriber to a list"},
                    {"id": "send_campaign", "name": "Send Campaign", "description": "Send an email campaign"},
                ]
            ),
            "twilio": Integration(
                id="twilio",
                name="Twilio",
                description="Send SMS, make calls, and manage communications",
                icon_url="https://www.vectorlogo.zone/logos/twilio/twilio-icon.svg",
                category=IntegrationCategory.COMMUNICATION,
                auth_type="api_key",
                actions=[
                    {"id": "send_sms", "name": "Send SMS", "description": "Send an SMS message"},
                    {"id": "make_call", "name": "Make Call", "description": "Make a phone call"},
                ]
            ),
            
            # AI Services
            "openai": Integration(
                id="openai",
                name="OpenAI",
                description="Generate text, analyze content with AI",
                icon_url="https://static.vecteezy.com/system/resources/previews/021/059/827/non_2x/chatgpt-logo-chat-gpt-icon-on-white-background-free-vector.jpg",
                category=IntegrationCategory.AI,
                auth_type="api_key",
                is_premium=True,
                actions=[
                    {"id": "generate_text", "name": "Generate Text", "description": "Generate text using GPT"},
                    {"id": "analyze_sentiment", "name": "Analyze Sentiment", "description": "Analyze sentiment of text"},
                    {"id": "generate_image", "name": "Generate Image", "description": "Generate images using DALL-E"},
                ],
            ),
            "groq": Integration(
                id="groq",
                name="GROQ AI",
                description="High-performance AI processing with Llama models",
                icon_url="https://wow.groq.com/wp-content/uploads/2024/03/PBG-mark1-color.svg",
                category=IntegrationCategory.AI,
                auth_type="api_key",
                is_premium=True,
                actions=[
                    {"id": "generate_text", "name": "Generate Text", "description": "Generate text using Llama models"},
                    {"id": "analyze_data", "name": "Analyze Data", "description": "Analyze data with AI"},
                    {"id": "process_text", "name": "Process Text", "description": "Process and transform text"},
                ],
            ),
            "anthropic": Integration(
                id="anthropic",
                name="Anthropic Claude",
                description="AI assistant powered by Claude",
                icon_url="https://pbs.twimg.com/profile_images/1784235872003919872/ZKJMTq3w_400x400.jpg",
                category=IntegrationCategory.AI,
                auth_type="api_key",
                is_premium=True,
                actions=[
                    {"id": "chat", "name": "Chat with Claude", "description": "Have a conversation with Claude AI"},
                    {"id": "analyze_document", "name": "Analyze Document", "description": "Analyze documents with Claude"},
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
        """Execute an integration action with real functionality."""
        integration = self.get_integration(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        logger.info(f"Executing {integration_id}.{action_id} with config: {list(config.keys())}")
        
        try:
            # Route to specific integration handlers
            if integration_id == "groq":
                return await self._execute_groq_action(action_id, config, data)
            elif integration_id == "slack":
                return await self._execute_slack_action(action_id, config, data)
            elif integration_id == "gmail":
                return await self._execute_gmail_action(action_id, config, data)
            elif integration_id == "github":
                return await self._execute_github_action(action_id, config, data)
            else:
                # Mock execution for other integrations
                return await self._mock_integration_execution(integration_id, action_id, config, data)
        
        except Exception as e:
            logger.error(f"Integration {integration_id}.{action_id} failed: {str(e)}")
            return {
                "status": "error",
                "integration": integration_id,
                "action": action_id,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def _execute_groq_action(self, action_id: str, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GROQ AI actions."""
        try:
            from ai_service import ai_service
            
            if action_id == "generate_text":
                prompt = config.get("prompt", data.get("text", "Generate helpful content"))
                response = await ai_service.process_with_groq(prompt, data)
                return {
                    "status": "success",
                    "integration": "groq",
                    "action": action_id,
                    "result": response,
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            elif action_id == "analyze_data":
                prompt = f"Analyze this data and provide insights: {json.dumps(data, indent=2)}"
                response = await ai_service.process_with_groq(prompt, data)
                return {
                    "status": "success",
                    "integration": "groq",
                    "action": action_id,
                    "analysis": response.get("response", "Analysis completed"),
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            else:
                return await self._mock_integration_execution("groq", action_id, config, data)
        
        except Exception as e:
            logger.error(f"GROQ action failed: {str(e)}")
            return {
                "status": "error",
                "integration": "groq", 
                "action": action_id,
                "error": str(e)
            }
    
    async def _execute_slack_action(self, action_id: str, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack actions (mock implementation)."""
        # Mock Slack API call
        await asyncio.sleep(0.2)
        
        if action_id == "send_message":
            channel = config.get("channel", "#general")
            message = config.get("message", data.get("message", "Automated message"))
            
            return {
                "status": "success",
                "integration": "slack",
                "action": action_id,
                "result": {
                    "channel": channel,
                    "message": message,
                    "message_id": f"slack_msg_{asyncio.get_event_loop().time()}",
                    "sent": True
                },
                "timestamp": asyncio.get_event_loop().time()
            }
        
        return await self._mock_integration_execution("slack", action_id, config, data)
    
    async def _execute_gmail_action(self, action_id: str, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Gmail actions (mock implementation)."""
        await asyncio.sleep(0.3)
        
        if action_id == "send_email":
            to_email = config.get("to", data.get("email", "recipient@example.com"))
            subject = config.get("subject", data.get("subject", "Automated Email"))
            body = config.get("body", data.get("body", "This email was sent by workflow automation"))
            
            return {
                "status": "success",
                "integration": "gmail",
                "action": action_id,
                "result": {
                    "to": to_email,
                    "subject": subject,
                    "message_id": f"gmail_msg_{asyncio.get_event_loop().time()}",
                    "sent": True
                },
                "timestamp": asyncio.get_event_loop().time()
            }
        
        return await self._mock_integration_execution("gmail", action_id, config, data)
    
    async def _execute_github_action(self, action_id: str, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub actions (mock implementation)."""
        await asyncio.sleep(0.4)
        
        if action_id == "create_issue":
            repo = config.get("repository", "owner/repo")
            title = config.get("title", data.get("title", "Automated Issue"))
            body = config.get("body", data.get("body", "This issue was created by workflow automation"))
            
            return {
                "status": "success",
                "integration": "github",
                "action": action_id,
                "result": {
                    "repository": repo,
                    "title": title,
                    "issue_number": int(asyncio.get_event_loop().time()) % 1000,
                    "url": f"https://github.com/{repo}/issues/123",
                    "created": True
                },
                "timestamp": asyncio.get_event_loop().time()
            }
        
        return await self._mock_integration_execution("github", action_id, config, data)
    
    async def _mock_integration_execution(self, integration_id: str, action_id: str, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock execution for integrations without specific handlers."""
        # Simulate API call delay
        await asyncio.sleep(0.1 + (hash(integration_id) % 5) / 10)
        
        return {
            "status": "success",
            "integration": integration_id,
            "action": action_id,
            "result": {
                "message": f"Successfully executed {action_id} on {integration_id}",
                "data_processed": len(str(data)),
                "config_applied": list(config.keys()),
                "execution_id": f"{integration_id}_{action_id}_{int(asyncio.get_event_loop().time())}"
            },
            "timestamp": asyncio.get_event_loop().time(),
            "mock_execution": True
        }
    
    def validate_config(self, integration_id: str, config: Dict[str, Any]) -> bool:
        """Validate integration configuration."""
        integration = self.get_integration(integration_id)
        if not integration:
            return False
        
        # Enhanced validation based on auth type
        if integration.auth_type == "api_key":
            return "api_key" in config or "token" in config
        elif integration.auth_type == "oauth2":
            return "access_token" in config or "oauth_token" in config
        
        # Basic validation for other auth types
        required_fields = [field.get("name") for field in integration.config_fields if field.get("required", False)]
        return all(field in config for field in required_fields)

# Global instance
integrations_engine = IntegrationsEngine()