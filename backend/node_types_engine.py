from typing import Dict, List, Any
from models import NodeType

class NodeTypesEngine:
    """Engine for managing workflow node types."""
    
    def __init__(self):
        self.node_types = self._load_node_types()
    
    def _load_node_types(self) -> Dict[str, Any]:
        """Load all available node types organized by categories."""
        return {
            "categories": {
                "triggers": [
                    {
                        "id": "manual_trigger",
                        "name": "Manual Trigger",
                        "description": "Manually start this workflow",
                        "type": "trigger",
                        "category": "basic",
                        "icon": "🚀",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string", "default": "Click to run"}
                            }
                        }
                    },
                    {
                        "id": "schedule_trigger",
                        "name": "Schedule Trigger",
                        "description": "Run on a schedule (cron-like)",
                        "type": "trigger",
                        "category": "basic",
                        "icon": "⏰",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "schedule": {"type": "string", "default": "0 9 * * MON-FRI"},
                                "timezone": {"type": "string", "default": "UTC"}
                            }
                        }
                    },
                    {
                        "id": "webhook_trigger",
                        "name": "Webhook Trigger",
                        "description": "Trigger when webhook receives data",
                        "type": "trigger", 
                        "category": "advanced",
                        "icon": "🔗",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "method": {"type": "string", "enum": ["GET", "POST"], "default": "POST"},
                                "authentication": {"type": "boolean", "default": False}
                            }
                        }
                    },
                    {
                        "id": "email_trigger",
                        "name": "Email Received",
                        "description": "Trigger when email is received",
                        "type": "trigger",
                        "category": "basic",
                        "icon": "📧",
                        "integration": "gmail",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "from_filter": {"type": "string", "default": ""},
                                "subject_contains": {"type": "string", "default": ""}
                            }
                        }
                    },
                    {
                        "id": "file_upload_trigger",
                        "name": "File Upload",
                        "description": "Trigger when file is uploaded",
                        "type": "trigger",
                        "category": "basic",
                        "icon": "📁",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "file_types": {"type": "string", "default": "*"},
                                "max_size_mb": {"type": "number", "default": 10}
                            }
                        }
                    },
                    {
                        "id": "ai_content_trigger",
                        "name": "AI Content Detection",
                        "description": "Trigger when AI detects specific content patterns",
                        "type": "trigger",
                        "category": "ai",
                        "icon": "🤖",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "content_type": {"type": "string", "enum": ["sentiment", "keywords", "language"], "default": "sentiment"},
                                "threshold": {"type": "number", "default": 0.7},
                                "model": {"type": "string", "enum": ["groq", "openai", "anthropic"], "default": "groq"}
                            }
                        }
                    },
                    {
                        "id": "data_threshold_trigger",
                        "name": "Data Threshold",
                        "description": "Trigger when data exceeds or falls below threshold",
                        "type": "trigger",
                        "category": "advanced",
                        "icon": "📊",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "metric": {"type": "string", "default": "value"},
                                "operator": {"type": "string", "enum": [">", "<", ">=", "<=", "=="], "default": ">"},
                                "threshold": {"type": "number", "default": 100}
                            }
                        }
                    }
                ],
                "actions": [
                    {
                        "id": "send_email",
                        "name": "Send Email",
                        "description": "Send an email notification",
                        "type": "action",
                        "category": "basic",
                        "icon": "✉️",
                        "integration": "gmail",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "to": {"type": "string", "default": ""},
                                "subject": {"type": "string", "default": "Workflow Notification"},
                                "body": {"type": "string", "default": "This email was sent by your workflow"}
                            }
                        }
                    },
                    {
                        "id": "send_slack_message",
                        "name": "Send Slack Message",
                        "description": "Send message to Slack channel",
                        "type": "action",
                        "category": "basic",
                        "icon": "💬",
                        "integration": "slack",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string", "default": "#general"},
                                "message": {"type": "string", "default": "Workflow notification"}
                            }
                        }
                    },
                    {
                        "id": "add_to_sheets",
                        "name": "Add to Google Sheets",
                        "description": "Add data to Google Sheets",
                        "type": "action",
                        "category": "basic",
                        "icon": "📊",
                        "integration": "google_sheets",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "spreadsheet_id": {"type": "string", "default": ""},
                                "sheet_name": {"type": "string", "default": "Sheet1"},
                                "range": {"type": "string", "default": "A1:Z1"}
                            }
                        }
                    },
                    {
                        "id": "create_github_issue",
                        "name": "Create GitHub Issue",
                        "description": "Create a new GitHub issue",
                        "type": "action",
                        "category": "basic",
                        "icon": "🐛",
                        "integration": "github",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "repository": {"type": "string", "default": "owner/repo"},
                                "title": {"type": "string", "default": "New Issue"},
                                "body": {"type": "string", "default": "Created by workflow automation"}
                            }
                        }
                    },
                    {
                        "id": "http_request",
                        "name": "HTTP Request",
                        "description": "Make an HTTP API call",
                        "type": "action",
                        "category": "advanced",
                        "icon": "🌐",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "default": "https://api.example.com"},
                                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
                                "headers": {"type": "object", "default": {}},
                                "body": {"type": "string", "default": ""}
                            }
                        }
                    },
                    {
                        "id": "ai_text_generation",
                        "name": "AI Text Generation",
                        "description": "Generate text using AI models",
                        "type": "action",
                        "category": "ai",
                        "icon": "🤖",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "model": {"type": "string", "enum": ["groq", "openai_gpt4", "anthropic_claude", "google_gemini"], "default": "groq"},
                                "prompt": {"type": "string", "default": "Generate helpful content"},
                                "max_tokens": {"type": "number", "default": 1000},
                                "temperature": {"type": "number", "default": 0.7}
                            }
                        }
                    },
                    {
                        "id": "ai_image_generation",
                        "name": "AI Image Generation",
                        "description": "Generate images using AI models",
                        "type": "action",
                        "category": "ai",
                        "icon": "🎨",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "model": {"type": "string", "enum": ["dalle3", "midjourney", "stability_ai"], "default": "dalle3"},
                                "prompt": {"type": "string", "default": "A beautiful landscape"},
                                "size": {"type": "string", "enum": ["256x256", "512x512", "1024x1024"], "default": "512x512"},
                                "style": {"type": "string", "enum": ["natural", "vivid", "artistic"], "default": "natural"}
                            }
                        }
                    },
                    {
                        "id": "ai_document_processing",
                        "name": "AI Document Processing",
                        "description": "Process and analyze documents with AI",
                        "type": "action",
                        "category": "ai",
                        "icon": "📄",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "operation": {"type": "string", "enum": ["ocr", "summarize", "extract_entities", "translate"], "default": "summarize"},
                                "language": {"type": "string", "default": "auto"},
                                "output_format": {"type": "string", "enum": ["text", "json", "markdown"], "default": "text"}
                            }
                        }
                    },
                    {
                        "id": "ai_voice_synthesis",
                        "name": "AI Voice Synthesis",
                        "description": "Convert text to speech using AI",
                        "type": "action",
                        "category": "ai",
                        "icon": "🗣️",
                        "integration": "elevenlabs",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "default": "Hello, this is AI generated speech"},
                                "voice": {"type": "string", "default": "default"},
                                "model": {"type": "string", "enum": ["eleven_monolingual_v1", "eleven_multilingual_v2"], "default": "eleven_monolingual_v1"},
                                "output_format": {"type": "string", "enum": ["mp3", "wav"], "default": "mp3"}
                            }
                        }
                    },
                    {
                        "id": "data_transformation",
                        "name": "Data Transformation",
                        "description": "Transform and manipulate data",
                        "type": "action",
                        "category": "advanced",
                        "icon": "🔄",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "operation": {"type": "string", "enum": ["filter", "map", "reduce", "sort", "group"], "default": "filter"},
                                "field": {"type": "string", "default": ""},
                                "condition": {"type": "string", "default": ""},
                                "output_format": {"type": "string", "enum": ["json", "csv", "xml"], "default": "json"}
                            }
                        }
                    },
                    {
                        "id": "file_processing",
                        "name": "File Processing",
                        "description": "Process and manipulate files",
                        "type": "action",
                        "category": "advanced",
                        "icon": "🗂️",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "operation": {"type": "string", "enum": ["compress", "extract", "convert", "merge", "split"], "default": "compress"},
                                "format": {"type": "string", "enum": ["zip", "pdf", "csv", "json", "xml"], "default": "zip"},
                                "quality": {"type": "number", "default": 85}
                            }
                        }
                    },
                    {
                        "id": "database_query",
                        "name": "Database Query",
                        "description": "Execute database queries",
                        "type": "action",
                        "category": "advanced",
                        "icon": "🗄️",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "query_type": {"type": "string", "enum": ["SELECT", "INSERT", "UPDATE", "DELETE"], "default": "SELECT"},
                                "table": {"type": "string", "default": ""},
                                "conditions": {"type": "string", "default": ""},
                                "limit": {"type": "number", "default": 100}
                            }
                        }
                    },
                    {
                        "id": "send_webhook",
                        "name": "Send Webhook",
                        "description": "Send data to webhook endpoints",
                        "type": "action",
                        "category": "advanced",
                        "icon": "📡",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "default": "https://webhook.example.com"},
                                "method": {"type": "string", "enum": ["POST", "PUT", "PATCH"], "default": "POST"},
                                "headers": {"type": "object", "default": {"Content-Type": "application/json"}},
                                "payload": {"type": "object", "default": {}}
                            }
                        }
                    },
                    {
                        "id": "send_sms",
                        "name": "Send SMS",
                        "description": "Send SMS message via Twilio",
                        "type": "action",
                        "category": "basic",
                        "icon": "📱",
                        "integration": "twilio",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "to": {"type": "string", "default": ""},
                                "message": {"type": "string", "default": "Workflow notification"}
                            }
                        }
                    },
                    {
                        "id": "create_trello_card",
                        "name": "Create Trello Card",
                        "description": "Create a new card in Trello",
                        "type": "action",
                        "category": "basic",
                        "icon": "📋",
                        "integration": "trello",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "board_id": {"type": "string", "default": ""},
                                "list_id": {"type": "string", "default": ""},
                                "title": {"type": "string", "default": "New Task"},
                                "description": {"type": "string", "default": ""}
                            }
                        }
                    },
                    {
                        "id": "upload_to_drive",
                        "name": "Upload to Google Drive",
                        "description": "Upload file to Google Drive",
                        "type": "action",
                        "category": "basic",
                        "icon": "☁️",
                        "integration": "google_drive",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "folder_id": {"type": "string", "default": ""},
                                "file_name": {"type": "string", "default": "workflow-file.txt"}
                            }
                        }
                    }
                ],
                "logic": [
                    {
                        "id": "condition",
                        "name": "Condition",
                        "description": "Branch workflow based on conditions",
                        "type": "condition",
                        "category": "basic",
                        "icon": "🔀",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "field": {"type": "string", "default": ""},
                                "operator": {"type": "string", "enum": ["equals", "contains", "greater_than", "less_than"], "default": "equals"},
                                "value": {"type": "string", "default": ""}
                            }
                        }
                    },
                    {
                        "id": "delay",
                        "name": "Delay",
                        "description": "Wait for specified time",
                        "type": "delay",
                        "category": "basic",
                        "icon": "⏱️",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "delay_seconds": {"type": "number", "default": 5},
                                "delay_type": {"type": "string", "enum": ["seconds", "minutes", "hours"], "default": "seconds"}
                            }
                        }
                    },
                    {
                        "id": "loop",
                        "name": "Loop",
                        "description": "Repeat actions for each item",
                        "type": "loop",
                        "category": "advanced",
                        "icon": "🔄",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "items_field": {"type": "string", "default": "items"},
                                "max_iterations": {"type": "number", "default": 100}
                            }
                        }
                    },
                    {
                        "id": "filter",
                        "name": "Filter Data",
                        "description": "Filter data based on criteria",
                        "type": "filter",
                        "category": "basic",
                        "icon": "🔍",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "filter_field": {"type": "string", "default": ""},
                                "filter_value": {"type": "string", "default": ""},
                                "filter_operator": {"type": "string", "enum": ["equals", "contains", "starts_with"], "default": "equals"}
                            }
                        }
                    },
                    {
                        "id": "transform_data",
                        "name": "Transform Data",
                        "description": "Transform and reshape data",
                        "type": "transform",
                        "category": "advanced",
                        "icon": "🔧",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "transformation": {"type": "string", "default": ""},
                                "output_format": {"type": "string", "enum": ["json", "csv", "xml"], "default": "json"}
                            }
                        }
                    },
                    {
                        "id": "merge_data",
                        "name": "Merge Data",
                        "description": "Combine data from multiple sources",
                        "type": "merge",
                        "category": "advanced",
                        "icon": "🔗",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "merge_key": {"type": "string", "default": "id"},
                                "merge_strategy": {"type": "string", "enum": ["inner", "outer", "left"], "default": "inner"}
                            }
                        }
                    }
                ],
                "ai": [
                    {
                        "id": "ai_text_generation",
                        "name": "Generate Text",
                        "description": "Generate text using AI",
                        "type": "ai",
                        "category": "advanced",
                        "icon": "🤖",
                        "integration": "groq",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "default": "Generate helpful content based on the input data"},
                                "model": {"type": "string", "enum": ["llama-3.1-8b-instant", "llama-3.1-70b-versatile"], "default": "llama-3.1-8b-instant"},
                                "temperature": {"type": "number", "default": 0.7}
                            }
                        }
                    },
                    {
                        "id": "ai_data_analysis",
                        "name": "Analyze Data",
                        "description": "Analyze data with AI insights",
                        "type": "ai",
                        "category": "advanced",
                        "icon": "📈",
                        "integration": "groq",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "analysis_type": {"type": "string", "enum": ["summary", "insights", "classification"], "default": "insights"},
                                "data_field": {"type": "string", "default": "data"}
                            }
                        }
                    },
                    {
                        "id": "ai_sentiment_analysis",
                        "name": "Sentiment Analysis",
                        "description": "Analyze sentiment of text",
                        "type": "ai",
                        "category": "basic",
                        "icon": "😊",
                        "integration": "groq",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "text_field": {"type": "string", "default": "text"},
                                "output_format": {"type": "string", "enum": ["score", "label", "detailed"], "default": "detailed"}
                            }
                        }
                    },
                    {
                        "id": "ai_translation",
                        "name": "Translate Text",
                        "description": "Translate text to another language",
                        "type": "ai",
                        "category": "basic",
                        "icon": "🌐",
                        "integration": "groq",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "source_language": {"type": "string", "default": "auto"},
                                "target_language": {"type": "string", "default": "english"},
                                "text_field": {"type": "string", "default": "text"}
                            }
                        }
                    },
                    {
                        "id": "ai_classification",
                        "name": "Classify Content",
                        "description": "Classify content into categories",
                        "type": "ai",
                        "category": "advanced",
                        "icon": "🏷️",
                        "integration": "groq",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "categories": {"type": "string", "default": "positive,negative,neutral"},
                                "content_field": {"type": "string", "default": "content"}
                            }
                        }
                    },
                    {
                        "id": "ai_summarization",
                        "name": "Summarize Content",
                        "description": "Create summary of long content",
                        "type": "ai",
                        "category": "basic",
                        "icon": "📝",
                        "integration": "groq",
                        "config_schema": {
                            "type": "object",
                            "properties": {
                                "content_field": {"type": "string", "default": "content"},
                                "summary_length": {"type": "string", "enum": ["short", "medium", "long"], "default": "medium"}
                            }
                        }
                    }
                ]
            },
            "stats": {
                "total_nodes": 0,
                "categories": 4,
                "basic_nodes": 0,
                "advanced_nodes": 0
            }
        }
    
    def get_node_types(self) -> Dict[str, Any]:
        """Get all node types with statistics."""
        node_types = self.node_types.copy()
        
        # Calculate statistics
        total_nodes = 0
        basic_nodes = 0
        advanced_nodes = 0
        
        for category, nodes in node_types["categories"].items():
            total_nodes += len(nodes)
            for node in nodes:
                if node.get("category") == "basic":
                    basic_nodes += 1
                elif node.get("category") == "advanced":
                    advanced_nodes += 1
        
        node_types["stats"] = {
            "total_nodes": total_nodes,
            "categories": len(node_types["categories"]),
            "basic_nodes": basic_nodes,
            "advanced_nodes": advanced_nodes
        }
        
        return node_types
    
    def get_node_type_by_id(self, node_id: str) -> Dict[str, Any]:
        """Get a specific node type by ID."""
        for category, nodes in self.node_types["categories"].items():
            for node in nodes:
                if node["id"] == node_id:
                    return node
        return None
    
    def search_node_types(self, query: str) -> List[Dict[str, Any]]:
        """Search node types by name or description."""
        query = query.lower()
        results = []
        
        for category, nodes in self.node_types["categories"].items():
            for node in nodes:
                if (query in node["name"].lower() or 
                    query in node["description"].lower() or
                    query in node.get("integration", "").lower()):
                    result = node.copy()
                    result["category_name"] = category
                    results.append(result)
        
        return results

# Global instance
node_types_engine = NodeTypesEngine()