"""
Enhanced Nodes Library - Advanced Node Types for Aether Automation
Expanding the node ecosystem with industry-specific and advanced capabilities
"""

def get_enhanced_node_categories():
    """Return enhanced node categories with 30+ new node types"""
    return {
        "triggers": [
            # Existing triggers enhanced
            {"id": "webhook-trigger", "name": "Webhook Trigger", "description": "Trigger on HTTP webhook", "category": "triggers"},
            {"id": "schedule-trigger", "name": "Schedule Trigger", "description": "Time-based trigger", "category": "triggers"},
            {"id": "email-trigger", "name": "Email Trigger", "description": "Trigger on email receipt", "category": "triggers"},
            
            # NEW ADVANCED TRIGGERS
            {"id": "database-change-trigger", "name": "Database Change", "description": "Trigger on database modifications", "category": "triggers"},
            {"id": "file-watcher-trigger", "name": "File System Watcher", "description": "Monitor file/folder changes", "category": "triggers"},
            {"id": "social-mention-trigger", "name": "Social Media Mention", "description": "Trigger on social media mentions", "category": "triggers"},
            {"id": "stock-price-trigger", "name": "Stock Price Alert", "description": "Trigger on stock price changes", "category": "triggers"},
            {"id": "weather-trigger", "name": "Weather Condition", "description": "Trigger on weather conditions", "category": "triggers"},
            {"id": "calendar-event-trigger", "name": "Calendar Event", "description": "Trigger on calendar events", "category": "triggers"},
            {"id": "form-submission-trigger", "name": "Form Submission", "description": "Trigger on form submissions", "category": "triggers"},
            {"id": "iot-sensor-trigger", "name": "IoT Sensor Data", "description": "Trigger on IoT sensor readings", "category": "triggers"},
            {"id": "git-commit-trigger", "name": "Git Commit", "description": "Trigger on code commits", "category": "triggers"},
        ],
        
        "actions": [
            # Existing actions enhanced
            {"id": "http-request", "name": "HTTP Request", "description": "Make HTTP API calls", "category": "actions"},
            {"id": "email-send", "name": "Send Email", "description": "Send emails", "category": "actions"},
            {"id": "database-query", "name": "Database Query", "description": "Query databases", "category": "actions"},
            
            # NEW ADVANCED ACTIONS
            {"id": "pdf-generator", "name": "PDF Generator", "description": "Generate PDF documents", "category": "actions"},
            {"id": "excel-processor", "name": "Excel Processor", "description": "Process Excel/CSV files", "category": "actions"},
            {"id": "image-processor", "name": "Image Processor", "description": "Resize, crop, convert images", "category": "actions"},
            {"id": "video-processor", "name": "Video Processor", "description": "Process and convert videos", "category": "actions"},
            {"id": "qr-generator", "name": "QR Code Generator", "description": "Generate QR codes", "category": "actions"},
            {"id": "barcode-scanner", "name": "Barcode Scanner", "description": "Scan and read barcodes", "category": "actions"},
            {"id": "ocr-processor", "name": "OCR Text Extract", "description": "Extract text from images", "category": "actions"},
            {"id": "text-to-speech", "name": "Text to Speech", "description": "Convert text to speech", "category": "actions"},
            {"id": "speech-to-text", "name": "Speech to Text", "description": "Convert speech to text", "category": "actions"},
            {"id": "language-translator", "name": "Language Translator", "description": "Translate between languages", "category": "actions"},
            {"id": "sentiment-analyzer", "name": "Sentiment Analysis", "description": "Analyze text sentiment", "category": "actions"},
            {"id": "web-scraper", "name": "Web Scraper", "description": "Extract data from websites", "category": "actions"},
            {"id": "cloud-storage", "name": "Cloud Storage", "description": "Upload/download cloud files", "category": "actions"},
            {"id": "ftp-operations", "name": "FTP Operations", "description": "FTP file operations", "category": "actions"},
            {"id": "compression-tool", "name": "File Compression", "description": "Compress/decompress files", "category": "actions"},
            {"id": "encryption-tool", "name": "Data Encryption", "description": "Encrypt/decrypt data", "category": "actions"},
        ],
        
        "logic": [
            # Existing logic enhanced
            {"id": "condition", "name": "Condition", "description": "If/then logic", "category": "logic"},
            {"id": "loop", "name": "Loop", "description": "Repeat actions", "category": "logic"},
            {"id": "delay", "name": "Delay", "description": "Wait/pause execution", "category": "logic"},
            
            # NEW ADVANCED LOGIC
            {"id": "parallel-execution", "name": "Parallel Execution", "description": "Run multiple branches simultaneously", "category": "logic"},
            {"id": "error-handler", "name": "Error Handler", "description": "Handle errors gracefully", "category": "logic"},
            {"id": "retry-mechanism", "name": "Retry Logic", "description": "Retry failed operations", "category": "logic"},
            {"id": "rate-limiter", "name": "Rate Limiter", "description": "Control execution rate", "category": "logic"},
            {"id": "data-validator", "name": "Data Validator", "description": "Validate data formats", "category": "logic"},
            {"id": "switch-case", "name": "Switch Case", "description": "Multi-branch conditions", "category": "logic"},
            {"id": "aggregator", "name": "Data Aggregator", "description": "Aggregate multiple inputs", "category": "logic"},
            {"id": "filter-processor", "name": "Data Filter", "description": "Filter data based on criteria", "category": "logic"},
            {"id": "json-processor", "name": "JSON Processor", "description": "Parse and manipulate JSON", "category": "logic"},
            {"id": "xml-processor", "name": "XML Processor", "description": "Parse and manipulate XML", "category": "logic"},
            {"id": "regex-processor", "name": "Regex Processor", "description": "Pattern matching and extraction", "category": "logic"},
            {"id": "template-engine", "name": "Template Engine", "description": "Generate content from templates", "category": "logic"},
        ],
        
        "ai": [
            # Existing AI enhanced
            {"id": "ai-text-generator", "name": "AI Text Generator", "description": "Generate text with AI", "category": "ai"},
            {"id": "ai-chat", "name": "AI Chat", "description": "Conversational AI", "category": "ai"},
            
            # NEW ADVANCED AI NODES
            {"id": "ai-code-generator", "name": "AI Code Generator", "description": "Generate code with AI", "category": "ai"},
            {"id": "ai-image-generator", "name": "AI Image Generator", "description": "Generate images with AI", "category": "ai"},
            {"id": "ai-content-moderator", "name": "AI Content Moderator", "description": "Moderate content with AI", "category": "ai"},
            {"id": "ai-summarizer", "name": "AI Summarizer", "description": "Summarize text with AI", "category": "ai"},
            {"id": "ai-classifier", "name": "AI Classifier", "description": "Classify content with AI", "category": "ai"},
            {"id": "ai-entity-extractor", "name": "AI Entity Extractor", "description": "Extract entities from text", "category": "ai"},
            {"id": "ai-keyword-extractor", "name": "AI Keyword Extractor", "description": "Extract keywords from text", "category": "ai"},
            {"id": "ai-language-detector", "name": "AI Language Detector", "description": "Detect language of text", "category": "ai"},
            {"id": "ai-plagiarism-checker", "name": "AI Plagiarism Checker", "description": "Check for plagiarism", "category": "ai"},
            {"id": "ai-readability-analyzer", "name": "AI Readability Analyzer", "description": "Analyze text readability", "category": "ai"},
            {"id": "ai-topic-modeler", "name": "AI Topic Modeler", "description": "Extract topics from text", "category": "ai"},
            {"id": "ai-emotion-detector", "name": "AI Emotion Detector", "description": "Detect emotions in text", "category": "ai"},
            {"id": "ai-intent-classifier", "name": "AI Intent Classifier", "description": "Classify user intent", "category": "ai"},
        ],
        
        # NEW INDUSTRY-SPECIFIC CATEGORIES
        "finance": [
            {"id": "tax-calculator", "name": "Tax Calculator", "description": "Calculate taxes and deductions", "category": "finance"},
            {"id": "invoice-generator", "name": "Invoice Generator", "description": "Generate professional invoices", "category": "finance"},
            {"id": "expense-tracker", "name": "Expense Tracker", "description": "Track and categorize expenses", "category": "finance"},
            {"id": "budget-analyzer", "name": "Budget Analyzer", "description": "Analyze budget performance", "category": "finance"},
            {"id": "currency-converter", "name": "Currency Converter", "description": "Convert between currencies", "category": "finance"},
            {"id": "crypto-tracker", "name": "Crypto Tracker", "description": "Track cryptocurrency prices", "category": "finance"},
            {"id": "payment-processor", "name": "Payment Processor", "description": "Process payments securely", "category": "finance"},
            {"id": "financial-report", "name": "Financial Report", "description": "Generate financial reports", "category": "finance"},
        ],
        
        "ecommerce": [
            {"id": "inventory-manager", "name": "Inventory Manager", "description": "Manage product inventory", "category": "ecommerce"},
            {"id": "order-processor", "name": "Order Processor", "description": "Process customer orders", "category": "ecommerce"},
            {"id": "shipping-calculator", "name": "Shipping Calculator", "description": "Calculate shipping costs", "category": "ecommerce"},
            {"id": "product-recommender", "name": "Product Recommender", "description": "Recommend products to customers", "category": "ecommerce"},
            {"id": "price-tracker", "name": "Price Tracker", "description": "Track competitor prices", "category": "ecommerce"},
            {"id": "review-analyzer", "name": "Review Analyzer", "description": "Analyze customer reviews", "category": "ecommerce"},
            {"id": "abandoned-cart", "name": "Abandoned Cart Recovery", "description": "Recover abandoned carts", "category": "ecommerce"},
            {"id": "loyalty-manager", "name": "Loyalty Program Manager", "description": "Manage customer loyalty", "category": "ecommerce"},
        ],
        
        "marketing": [
            {"id": "campaign-manager", "name": "Campaign Manager", "description": "Manage marketing campaigns", "category": "marketing"},
            {"id": "lead-scorer", "name": "Lead Scorer", "description": "Score and qualify leads", "category": "marketing"},
            {"id": "ab-tester", "name": "A/B Tester", "description": "Run A/B tests", "category": "marketing"},
            {"id": "social-scheduler", "name": "Social Media Scheduler", "description": "Schedule social media posts", "category": "marketing"},
            {"id": "email-personalizer", "name": "Email Personalizer", "description": "Personalize email content", "category": "marketing"},
            {"id": "seo-analyzer", "name": "SEO Analyzer", "description": "Analyze SEO performance", "category": "marketing"},
            {"id": "content-curator", "name": "Content Curator", "description": "Curate relevant content", "category": "marketing"},
            {"id": "influencer-tracker", "name": "Influencer Tracker", "description": "Track influencer metrics", "category": "marketing"},
        ],
        
        "healthcare": [
            {"id": "appointment-scheduler", "name": "Appointment Scheduler", "description": "Schedule medical appointments", "category": "healthcare"},
            {"id": "patient-reminder", "name": "Patient Reminder", "description": "Send patient reminders", "category": "healthcare"},
            {"id": "health-monitor", "name": "Health Monitor", "description": "Monitor patient health data", "category": "healthcare"},
            {"id": "prescription-manager", "name": "Prescription Manager", "description": "Manage prescriptions", "category": "healthcare"},
            {"id": "insurance-verifier", "name": "Insurance Verifier", "description": "Verify insurance coverage", "category": "healthcare"},
            {"id": "symptom-checker", "name": "Symptom Checker", "description": "Check symptoms and provide guidance", "category": "healthcare"},
            {"id": "medical-transcriber", "name": "Medical Transcriber", "description": "Transcribe medical notes", "category": "healthcare"},
        ]
    }

def get_node_configurations():
    """Return default configurations for each node type"""
    return {
        # AI Node Configurations
        "ai-code-generator": {
            "language": "python",
            "framework": "fastapi",
            "style": "clean",
            "comments": True,
            "testing": False
        },
        "ai-image-generator": {
            "style": "photorealistic",
            "size": "1024x1024",
            "quality": "standard",
            "n": 1
        },
        "ai-content-moderator": {
            "check_toxicity": True,
            "check_spam": True,
            "check_adult_content": True,
            "threshold": 0.8
        },
        
        # Finance Node Configurations
        "tax-calculator": {
            "country": "US",
            "tax_year": 2024,
            "filing_status": "single",
            "include_state_tax": True
        },
        "currency-converter": {
            "base_currency": "USD",
            "target_currency": "EUR",
            "use_live_rates": True,
            "precision": 2
        },
        
        # E-commerce Node Configurations
        "inventory-manager": {
            "track_variants": True,
            "low_stock_alert": 10,
            "auto_reorder": False,
            "sync_platforms": True
        },
        "price-tracker": {
            "check_frequency": "daily",
            "alert_threshold": 5,
            "include_competitors": True,
            "track_history": True
        },
        
        # Marketing Node Configurations
        "campaign-manager": {
            "platforms": ["email", "social", "ads"],
            "auto_optimize": True,
            "track_conversions": True,
            "budget_alerts": True
        },
        "lead-scorer": {
            "scoring_model": "predictive",
            "threshold": 75,
            "auto_qualify": True,
            "integration": "crm"
        }
    }

def get_node_templates():
    """Return pre-built node templates for common use cases"""
    return {
        "customer_onboarding": {
            "name": "Customer Onboarding Flow",
            "description": "Complete customer onboarding automation",
            "nodes": [
                {"type": "form-submission-trigger", "name": "New Customer Form"},
                {"type": "email-personalizer", "name": "Welcome Email"},
                {"type": "crm-integration", "name": "Add to CRM"},
                {"type": "task-creator", "name": "Create Onboarding Tasks"}
            ]
        },
        "content_workflow": {
            "name": "AI Content Creation Workflow",
            "description": "Automated content creation and publishing",
            "nodes": [
                {"type": "ai-content-generator", "name": "Generate Content"},
                {"type": "ai-content-moderator", "name": "Content Review"},
                {"type": "seo-analyzer", "name": "SEO Optimization"},
                {"type": "social-scheduler", "name": "Schedule Publishing"}
            ]
        },
        "ecommerce_order": {
            "name": "E-commerce Order Processing",
            "description": "Complete order processing automation",
            "nodes": [
                {"type": "order-processor", "name": "Process Order"},
                {"type": "inventory-manager", "name": "Update Inventory"},
                {"type": "payment-processor", "name": "Process Payment"},
                {"type": "shipping-calculator", "name": "Calculate Shipping"},
                {"type": "customer-notification", "name": "Send Confirmation"}
            ]
        }
    }