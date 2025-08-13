"""
Enhanced Integrations Library - 25+ New Popular Integrations
Expanding the integration ecosystem with trending and powerful platforms
"""

def get_enhanced_integrations():
    """Return enhanced integration categories with 25+ new popular integrations"""
    return {
        "communication": [
            # Existing
            {"name": "Slack", "icon": "slack", "oauth": True, "description": "Team communication platform"},
            {"name": "Discord", "icon": "discord", "oauth": True, "description": "Community chat platform"},
            {"name": "Microsoft Teams", "icon": "teams", "oauth": True, "description": "Business communication"},
            {"name": "Email", "icon": "email", "oauth": False, "description": "Email communication"},
            
            # NEW ADDITIONS
            {"name": "WhatsApp Business", "icon": "whatsapp", "oauth": True, "description": "Business messaging"},
            {"name": "Telegram", "icon": "telegram", "oauth": True, "description": "Secure messaging"},
            {"name": "Signal", "icon": "signal", "oauth": False, "description": "Private messaging"},
            {"name": "Zoom", "icon": "zoom", "oauth": True, "description": "Video conferencing"},
            {"name": "Google Meet", "icon": "meet", "oauth": True, "description": "Video meetings"},
            {"name": "Webex", "icon": "webex", "oauth": True, "description": "Enterprise video"},
            {"name": "Mattermost", "icon": "mattermost", "oauth": True, "description": "Open-source messaging"},
        ],
        
        "productivity": [
            # Existing
            {"name": "Google Workspace", "icon": "google", "oauth": True, "description": "Google productivity suite"},
            {"name": "Microsoft 365", "icon": "microsoft", "oauth": True, "description": "Microsoft productivity suite"},
            {"name": "Notion", "icon": "notion", "oauth": True, "description": "All-in-one workspace"},
            {"name": "Airtable", "icon": "airtable", "oauth": True, "description": "Database and spreadsheets"},
            
            # NEW TRENDING ADDITIONS
            {"name": "Linear", "icon": "linear", "oauth": True, "description": "Modern project management"},
            {"name": "Height", "icon": "height", "oauth": True, "description": "Autonomous project tool"},
            {"name": "Coda", "icon": "coda", "oauth": True, "description": "Next-gen documents"},
            {"name": "Obsidian", "icon": "obsidian", "oauth": False, "description": "Knowledge management"},
            {"name": "Roam Research", "icon": "roam", "oauth": True, "description": "Network thinking tool"},
            {"name": "RemNote", "icon": "remnote", "oauth": True, "description": "Note-taking and spaced repetition"},
            {"name": "Craft", "icon": "craft", "oauth": True, "description": "Structured writing"},
        ],
        
        "social": [
            # Existing
            {"name": "Twitter", "icon": "twitter", "oauth": True, "description": "Microblogging platform"},
            {"name": "LinkedIn", "icon": "linkedin", "oauth": True, "description": "Professional network"},
            {"name": "Facebook", "icon": "facebook", "oauth": True, "description": "Social networking"},
            {"name": "Instagram", "icon": "instagram", "oauth": True, "description": "Photo sharing"},
            
            # NEW TRENDING ADDITIONS
            {"name": "TikTok", "icon": "tiktok", "oauth": True, "description": "Short-form video platform"},
            {"name": "YouTube Shorts", "icon": "youtube", "oauth": True, "description": "Short video content"},
            {"name": "Threads", "icon": "threads", "oauth": True, "description": "Text-based social network"},
            {"name": "Mastodon", "icon": "mastodon", "oauth": True, "description": "Decentralized social network"},
            {"name": "BeReal", "icon": "bereal", "oauth": True, "description": "Authentic social sharing"},
            {"name": "Clubhouse", "icon": "clubhouse", "oauth": True, "description": "Audio social network"},
            {"name": "Reddit", "icon": "reddit", "oauth": True, "description": "Community discussions"},
        ],
        
        "development": [
            # Existing
            {"name": "GitHub", "icon": "github", "oauth": True, "description": "Code repository platform"},
            {"name": "GitLab", "icon": "gitlab", "oauth": True, "description": "DevOps platform"},
            {"name": "Jira", "icon": "jira", "oauth": True, "description": "Issue tracking"},
            {"name": "Trello", "icon": "trello", "oauth": True, "description": "Project management"},
            
            # NEW TRENDING ADDITIONS
            {"name": "Vercel", "icon": "vercel", "oauth": True, "description": "Frontend deployment"},
            {"name": "Netlify", "icon": "netlify", "oauth": True, "description": "Web platform"},
            {"name": "Railway", "icon": "railway", "oauth": True, "description": "Cloud deployment"},
            {"name": "Supabase", "icon": "supabase", "oauth": True, "description": "Open-source Firebase"},
            {"name": "PlanetScale", "icon": "planetscale", "oauth": True, "description": "Serverless database"},
            {"name": "Neon", "icon": "neon", "oauth": True, "description": "Serverless PostgreSQL"},
            {"name": "CodeSandbox", "icon": "codesandbox", "oauth": True, "description": "Online IDE"},
        ],
        
        "ai": [
            # Existing
            {"name": "OpenAI", "icon": "openai", "oauth": False, "description": "GPT and AI models"},
            {"name": "GROQ", "icon": "groq", "oauth": False, "description": "Fast AI inference"},
            {"name": "Anthropic", "icon": "anthropic", "oauth": False, "description": "Claude AI assistant"},
            
            # NEW CUTTING-EDGE ADDITIONS
            {"name": "Perplexity", "icon": "perplexity", "oauth": False, "description": "AI search engine"},
            {"name": "Mistral AI", "icon": "mistral", "oauth": False, "description": "Open-source AI models"},
            {"name": "Cohere", "icon": "cohere", "oauth": False, "description": "Enterprise AI platform"},
            {"name": "Hugging Face", "icon": "huggingface", "oauth": True, "description": "ML community platform"},
            {"name": "Replicate", "icon": "replicate", "oauth": False, "description": "AI model hosting"},
            {"name": "RunPod", "icon": "runpod", "oauth": False, "description": "GPU cloud platform"},
            {"name": "Together AI", "icon": "together", "oauth": False, "description": "Collaborative AI platform"},
            {"name": "Fireworks AI", "icon": "fireworks", "oauth": False, "description": "Fast AI inference"},
        ],
        
        # NEW CATEGORIES
        "design": [
            {"name": "Figma", "icon": "figma", "oauth": True, "description": "Collaborative design tool"},
            {"name": "Canva", "icon": "canva", "oauth": True, "description": "Graphic design platform"},
            {"name": "Adobe Creative", "icon": "adobe", "oauth": True, "description": "Creative software suite"},
            {"name": "Sketch", "icon": "sketch", "oauth": True, "description": "Digital design toolkit"},
            {"name": "Framer", "icon": "framer", "oauth": True, "description": "Interactive design tool"},
            {"name": "InVision", "icon": "invision", "oauth": True, "description": "Digital product design"},
            {"name": "Miro", "icon": "miro", "oauth": True, "description": "Online whiteboard"},
        ],
        
        "no_code": [
            {"name": "Webflow", "icon": "webflow", "oauth": True, "description": "Visual web development"},
            {"name": "Bubble", "icon": "bubble", "oauth": True, "description": "No-code app builder"},
            {"name": "Zapier", "icon": "zapier", "oauth": True, "description": "Automation platform"},
            {"name": "Make", "icon": "make", "oauth": True, "description": "Visual automation"},
            {"name": "n8n", "icon": "n8n", "oauth": True, "description": "Open-source automation"},
            {"name": "Retool", "icon": "retool", "oauth": True, "description": "Internal tools builder"},
            {"name": "Glide", "icon": "glide", "oauth": True, "description": "App builder from data"},
        ],
        
        "crypto": [
            {"name": "Coinbase", "icon": "coinbase", "oauth": True, "description": "Cryptocurrency exchange"},
            {"name": "Binance", "icon": "binance", "oauth": False, "description": "Global crypto exchange"},
            {"name": "Kraken", "icon": "kraken", "oauth": False, "description": "Crypto trading platform"},
            {"name": "CoinGecko", "icon": "coingecko", "oauth": False, "description": "Crypto data platform"},
            {"name": "DeFiPulse", "icon": "defipulse", "oauth": False, "description": "DeFi analytics"},
            {"name": "Moralis", "icon": "moralis", "oauth": False, "description": "Web3 development"},
            {"name": "Alchemy", "icon": "alchemy", "oauth": False, "description": "Blockchain infrastructure"},
        ],
        
        "gaming": [
            {"name": "Steam", "icon": "steam", "oauth": True, "description": "Gaming platform"},
            {"name": "Twitch", "icon": "twitch", "oauth": True, "description": "Game streaming"},
            {"name": "Unity", "icon": "unity", "oauth": True, "description": "Game development"},
            {"name": "Epic Games", "icon": "epic", "oauth": True, "description": "Game store and engine"},
            {"name": "Roblox", "icon": "roblox", "oauth": True, "description": "Gaming platform"},
            {"name": "Itch.io", "icon": "itch", "oauth": True, "description": "Indie game platform"},
        ]
    }

def get_integration_capabilities():
    """Return capabilities and features for each integration"""
    return {
        # AI Platform Capabilities
        "perplexity": {
            "capabilities": ["search", "reasoning", "citations", "real_time_data"],
            "models": ["sonar-small", "sonar-medium", "sonar-pro"],
            "rate_limits": {"requests_per_minute": 60, "tokens_per_minute": 100000}
        },
        "mistral": {
            "capabilities": ["chat", "completion", "embeddings", "fine_tuning"],
            "models": ["mistral-7b", "mistral-8x7b", "mistral-large"],
            "rate_limits": {"requests_per_minute": 100, "tokens_per_minute": 200000}
        },
        "cohere": {
            "capabilities": ["generation", "embeddings", "classification", "summarization"],
            "models": ["command", "command-light", "embed-english", "embed-multilingual"],
            "rate_limits": {"requests_per_minute": 1000, "tokens_per_minute": 500000}
        },
        
        # Design Platform Capabilities
        "figma": {
            "capabilities": ["files", "comments", "version_history", "prototypes", "components"],
            "webhooks": ["file_update", "comment_added", "version_published"],
            "rate_limits": {"requests_per_minute": 60}
        },
        "canva": {
            "capabilities": ["designs", "templates", "brand_kit", "folders", "sharing"],
            "formats": ["png", "jpg", "pdf", "mp4", "gif"],
            "rate_limits": {"requests_per_minute": 100}
        },
        
        # No-Code Platform Capabilities
        "webflow": {
            "capabilities": ["sites", "collections", "forms", "ecommerce", "cms"],
            "webhooks": ["form_submission", "order_placed", "site_published"],
            "rate_limits": {"requests_per_minute": 60}
        },
        "bubble": {
            "capabilities": ["data", "workflows", "users", "files", "api_workflows"],
            "webhooks": ["data_change", "user_signup", "workflow_trigger"],
            "rate_limits": {"requests_per_minute": 120}
        },
        
        # Social Platform Capabilities
        "tiktok": {
            "capabilities": ["videos", "user_info", "analytics", "comments", "hashtags"],
            "content_types": ["video", "image", "carousel"],
            "rate_limits": {"requests_per_minute": 100}
        },
        "threads": {
            "capabilities": ["posts", "replies", "media", "user_info", "insights"],
            "content_types": ["text", "image", "video"],
            "rate_limits": {"requests_per_minute": 200}
        }
    }

def get_oauth_configurations():
    """Return OAuth configuration templates for new integrations"""
    return {
        "linear": {
            "auth_url": "https://linear.app/oauth/authorize",
            "token_url": "https://api.linear.app/oauth/token",
            "scopes": ["read", "write", "issues:create", "comments:create"],
            "redirect_uri": "/api/oauth/callback/linear"
        },
        "notion": {
            "auth_url": "https://api.notion.com/v1/oauth/authorize",
            "token_url": "https://api.notion.com/v1/oauth/token",
            "scopes": ["read_content", "update_content", "insert_content"],
            "redirect_uri": "/api/oauth/callback/notion"
        },
        "figma": {
            "auth_url": "https://www.figma.com/oauth",
            "token_url": "https://www.figma.com/api/oauth/token",
            "scopes": ["files:read", "file_comments:write"],
            "redirect_uri": "/api/oauth/callback/figma"
        },
        "vercel": {
            "auth_url": "https://vercel.com/oauth/authorize",
            "token_url": "https://api.vercel.com/v2/oauth/access_token",
            "scopes": ["deployments", "projects", "teams"],
            "redirect_uri": "/api/oauth/callback/vercel"
        }
    }