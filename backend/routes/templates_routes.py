"""
Advanced Template Management Routes
Supports template customization, sharing, and community features
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from database import get_database
from auth import get_current_active_user
import logging
import json
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/templates", tags=["templates"])

@router.get("/")
async def get_templates(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    tags: Optional[str] = None,
    sort_by: str = Query("popular", description="Sort by: popular, recent, rating, name"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Get workflow templates with filtering and sorting"""
    try:
        db = get_database()
        
        # Build query filters
        query_filter = {"is_active": True}
        
        if category:
            query_filter["category"] = category
            
        if difficulty:
            query_filter["difficulty"] = difficulty
            
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            query_filter["tags"] = {"$in": tag_list}
        
        # Build sort criteria
        sort_criteria = []
        if sort_by == "popular":
            sort_criteria = [("usage_count", -1), ("rating", -1)]
        elif sort_by == "recent":
            sort_criteria = [("created_at", -1)]
        elif sort_by == "rating":
            sort_criteria = [("rating", -1), ("rating_count", -1)]
        elif sort_by == "name":
            sort_criteria = [("name", 1)]
        else:
            sort_criteria = [("usage_count", -1)]
        
        # Execute query
        cursor = db.workflow_templates.find(query_filter).sort(sort_criteria).skip(offset).limit(limit)
        templates = await cursor.to_list(length=limit)
        
        # Get total count for pagination
        total_count = await db.workflow_templates.count_documents(query_filter)
        
        # Enhance templates with additional data
        enhanced_templates = []
        for template in templates:
            enhanced_template = {
                **template,
                "author_info": await get_template_author_info(template.get("author_id")),
                "is_favorited": False,  # Would check against user favorites
                "deployment_count": template.get("usage_count", 0),
                "last_updated": template.get("updated_at", template.get("created_at"))
            }
            enhanced_templates.append(enhanced_template)
        
        return {
            "templates": enhanced_templates,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            },
            "filters": {
                "available_categories": await get_template_categories(),
                "available_difficulties": ["beginner", "intermediate", "advanced"],
                "popular_tags": await get_popular_template_tags()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")

@router.get("/{template_id}")
async def get_template_details(template_id: str):
    """Get detailed template information"""
    try:
        db = get_database()
        
        template = await db.workflow_templates.find_one({"id": template_id, "is_active": True})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Get additional details
        author_info = await get_template_author_info(template.get("author_id"))
        
        # Get related templates
        related_templates = await get_related_templates(template_id, template.get("tags", []), template.get("category"))
        
        # Get usage statistics
        usage_stats = await get_template_usage_stats(template_id)
        
        detailed_template = {
            **template,
            "author_info": author_info,
            "related_templates": related_templates,
            "usage_statistics": usage_stats,
            "schema_validation": validate_template_schema(template.get("workflow_definition", {})),
            "compatibility": check_template_compatibility(template)
        }
        
        return detailed_template
        
    except Exception as e:
        logger.error(f"Error getting template details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template details")

@router.post("/{template_id}/deploy")
async def deploy_template(
    template_id: str,
    deployment_config: Dict[str, Any] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Deploy a template as a new workflow"""
    try:
        db = get_database()
        
        # Get template
        template = await db.workflow_templates.find_one({"id": template_id, "is_active": True})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create workflow from template
        workflow_definition = template["workflow_definition"].copy()
        
        # Apply deployment configuration if provided
        if deployment_config:
            workflow_definition = apply_deployment_config(workflow_definition, deployment_config)
        
        # Generate unique workflow ID
        workflow_id = str(uuid.uuid4())
        
        # Create new workflow
        new_workflow = {
            "id": workflow_id,
            "name": deployment_config.get("name", f"{template['name']} - Copy"),
            "description": deployment_config.get("description", template["description"]),
            "user_id": current_user["user_id"],
            "workflow_definition": workflow_definition,
            "is_active": True,
            "created_from_template": template_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "tags": deployment_config.get("tags", template.get("tags", [])),
            "category": template.get("category", "custom")
        }
        
        # Insert workflow
        result = await db.workflows.insert_one(new_workflow)
        
        # Update template usage count
        await db.workflow_templates.update_one(
            {"id": template_id},
            {
                "$inc": {"usage_count": 1},
                "$push": {"recent_deployments": {
                    "user_id": current_user["user_id"],
                    "deployed_at": datetime.utcnow(),
                    "workflow_id": workflow_id
                }}
            }
        )
        
        # Log template deployment
        await db.template_deployments.insert_one({
            "id": str(uuid.uuid4()),
            "template_id": template_id,
            "workflow_id": workflow_id,
            "user_id": current_user["user_id"],
            "deployed_at": datetime.utcnow(),
            "deployment_config": deployment_config or {}
        })
        
        return {
            "message": "Template deployed successfully",
            "workflow_id": workflow_id,
            "workflow_name": new_workflow["name"],
            "template_id": template_id
        }
        
    except Exception as e:
        logger.error(f"Error deploying template: {e}")
        raise HTTPException(status_code=500, detail="Failed to deploy template")

@router.post("/create")
async def create_custom_template(
    template_data: Dict[str, Any],
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new custom template"""
    try:
        db = get_database()
        
        # Validate required fields
        required_fields = ["name", "description", "workflow_definition", "category"]
        for field in required_fields:
            if field not in template_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Generate template ID
        template_id = str(uuid.uuid4())
        
        # Create template
        new_template = {
            "id": template_id,
            "name": template_data["name"],
            "description": template_data["description"],
            "workflow_definition": template_data["workflow_definition"],
            "category": template_data["category"],
            "difficulty": template_data.get("difficulty", "intermediate"),
            "tags": template_data.get("tags", []),
            "author_id": current_user["user_id"],
            "is_public": template_data.get("is_public", False),
            "is_active": True,
            "usage_count": 0,
            "rating": 0,
            "rating_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": "1.0.0",
            "changelog": [],
            "requirements": template_data.get("requirements", []),
            "preview_image": template_data.get("preview_image"),
            "recent_deployments": []
        }
        
        # Validate workflow definition
        validation_result = validate_template_schema(new_template["workflow_definition"])
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid workflow definition: {validation_result['errors']}"
            )
        
        # Insert template
        await db.workflow_templates.insert_one(new_template)
        
        return {
            "message": "Template created successfully",
            "template_id": template_id,
            "template": new_template
        }
        
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")

@router.put("/{template_id}")
async def update_template(
    template_id: str,
    updates: Dict[str, Any],
    current_user: dict = Depends(get_current_active_user)
):
    """Update an existing template"""
    try:
        db = get_database()
        
        # Verify ownership
        template = await db.workflow_templates.find_one({
            "id": template_id,
            "author_id": current_user["user_id"]
        })
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found or access denied")
        
        # Prepare update data
        allowed_fields = ["name", "description", "workflow_definition", "category", "difficulty", 
                         "tags", "is_public", "requirements", "preview_image"]
        
        update_data = {
            key: value for key, value in updates.items() 
            if key in allowed_fields
        }
        
        if "workflow_definition" in update_data:
            # Validate workflow definition
            validation_result = validate_template_schema(update_data["workflow_definition"])
            if not validation_result["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid workflow definition: {validation_result['errors']}"
                )
        
        # Add metadata
        update_data["updated_at"] = datetime.utcnow()
        
        # Version increment (simple semantic versioning)
        current_version = template.get("version", "1.0.0")
        version_parts = current_version.split(".")
        version_parts[2] = str(int(version_parts[2]) + 1)  # Increment patch version
        update_data["version"] = ".".join(version_parts)
        
        # Add to changelog
        changelog_entry = {
            "version": update_data["version"],
            "changes": updates.get("changelog_message", "Template updated"),
            "updated_at": datetime.utcnow()
        }
        
        await db.workflow_templates.update_one(
            {"id": template_id},
            {
                "$set": update_data,
                "$push": {"changelog": changelog_entry}
            }
        )
        
        return {
            "message": "Template updated successfully",
            "template_id": template_id,
            "new_version": update_data["version"]
        }
        
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        raise HTTPException(status_code=500, detail="Failed to update template")

@router.post("/{template_id}/rate")
async def rate_template(
    template_id: str,
    rating_data: Dict[str, Any],
    current_user: dict = Depends(get_current_active_user)
):
    """Rate and review a template"""
    try:
        db = get_database()
        
        # Validate rating
        rating = rating_data.get("rating")
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be an integer between 1 and 5")
        
        # Check if template exists
        template = await db.workflow_templates.find_one({"id": template_id, "is_active": True})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if user already rated this template
        existing_rating = await db.template_ratings.find_one({
            "template_id": template_id,
            "user_id": current_user["user_id"]
        })
        
        if existing_rating:
            # Update existing rating
            await db.template_ratings.update_one(
                {"id": existing_rating["id"]},
                {
                    "$set": {
                        "rating": rating,
                        "review": rating_data.get("review", ""),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            # Create new rating
            rating_id = str(uuid.uuid4())
            await db.template_ratings.insert_one({
                "id": rating_id,
                "template_id": template_id,
                "user_id": current_user["user_id"],
                "rating": rating,
                "review": rating_data.get("review", ""),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Recalculate template average rating
        ratings_cursor = db.template_ratings.find({"template_id": template_id})
        all_ratings = await ratings_cursor.to_list(length=None)
        
        if all_ratings:
            average_rating = sum(r["rating"] for r in all_ratings) / len(all_ratings)
            rating_count = len(all_ratings)
            
            await db.workflow_templates.update_one(
                {"id": template_id},
                {
                    "$set": {
                        "rating": round(average_rating, 2),
                        "rating_count": rating_count
                    }
                }
            )
        
        return {
            "message": "Rating submitted successfully",
            "template_id": template_id,
            "your_rating": rating
        }
        
    except Exception as e:
        logger.error(f"Error rating template: {e}")
        raise HTTPException(status_code=500, detail="Failed to rate template")

@router.get("/{template_id}/reviews")
async def get_template_reviews(
    template_id: str,
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0)
):
    """Get reviews for a template"""
    try:
        db = get_database()
        
        # Get reviews with user info
        ratings_cursor = db.template_ratings.find({
            "template_id": template_id,
            "review": {"$ne": ""}  # Only reviews with text
        }).sort([("created_at", -1)]).skip(offset).limit(limit)
        
        ratings = await ratings_cursor.to_list(length=limit)
        
        # Enhance with user information
        enhanced_reviews = []
        for rating in ratings:
            user_info = await get_user_public_info(rating["user_id"])
            enhanced_reviews.append({
                **rating,
                "user_info": user_info,
                "helpful_votes": 0  # Would track helpful votes in production
            })
        
        total_count = await db.template_ratings.count_documents({
            "template_id": template_id,
            "review": {"$ne": ""}
        })
        
        return {
            "reviews": enhanced_reviews,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting template reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template reviews")

# Helper functions
async def get_template_author_info(author_id: str) -> Dict[str, Any]:
    """Get public author information"""
    if not author_id:
        return {"name": "Anonymous", "avatar": None}
    
    db = get_database()
    user = await db.users.find_one({"id": author_id})
    
    if user:
        return {
            "id": author_id,
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
            "avatar": user.get("avatar"),
            "company": user.get("company")
        }
    
    return {"name": "Unknown User", "avatar": None}

async def get_user_public_info(user_id: str) -> Dict[str, Any]:
    """Get public user information for reviews"""
    return await get_template_author_info(user_id)

async def get_template_categories() -> List[str]:
    """Get available template categories"""
    db = get_database()
    categories = await db.workflow_templates.distinct("category", {"is_active": True})
    return sorted(categories)

async def get_popular_template_tags() -> List[str]:
    """Get popular template tags"""
    db = get_database()
    # This would be more sophisticated in production
    pipeline = [
        {"$match": {"is_active": True}},
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    
    result = await db.workflow_templates.aggregate(pipeline).to_list(length=20)
    return [item["_id"] for item in result]

async def get_related_templates(template_id: str, tags: List[str], category: str) -> List[Dict[str, Any]]:
    """Get related templates based on tags and category"""
    db = get_database()
    
    query_filter = {
        "id": {"$ne": template_id},
        "is_active": True,
        "$or": [
            {"tags": {"$in": tags}},
            {"category": category}
        ]
    }
    
    cursor = db.workflow_templates.find(query_filter).limit(5)
    related = await cursor.to_list(length=5)
    
    return related

async def get_template_usage_stats(template_id: str) -> Dict[str, Any]:
    """Get template usage statistics"""
    db = get_database()
    
    # Get deployment stats
    deployments = await db.template_deployments.count_documents({"template_id": template_id})
    
    # Get recent deployment trend (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_deployments = await db.template_deployments.count_documents({
        "template_id": template_id,
        "deployed_at": {"$gte": thirty_days_ago}
    })
    
    return {
        "total_deployments": deployments,
        "recent_deployments": recent_deployments,
        "deployment_trend": "increasing" if recent_deployments > deployments * 0.3 else "stable"
    }

def validate_template_schema(workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
    """Validate template workflow schema"""
    errors = []
    
    # Basic validation
    if not isinstance(workflow_definition, dict):
        errors.append("Workflow definition must be an object")
        return {"is_valid": False, "errors": errors}
    
    # Check required fields
    required_fields = ["nodes", "edges"]
    for field in required_fields:
        if field not in workflow_definition:
            errors.append(f"Missing required field: {field}")
    
    # Validate nodes
    nodes = workflow_definition.get("nodes", [])
    if not isinstance(nodes, list):
        errors.append("Nodes must be an array")
    elif len(nodes) == 0:
        errors.append("Template must have at least one node")
    
    # Validate edges
    edges = workflow_definition.get("edges", [])
    if not isinstance(edges, list):
        errors.append("Edges must be an array")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def check_template_compatibility(template: Dict[str, Any]) -> Dict[str, Any]:
    """Check template compatibility with current system"""
    return {
        "is_compatible": True,
        "required_integrations": template.get("requirements", []),
        "minimum_version": "1.0.0"
    }

def apply_deployment_config(workflow_definition: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply deployment configuration to workflow definition"""
    # This would customize the workflow based on deployment config
    # For example, replacing placeholder values with actual configuration
    
    customized_definition = workflow_definition.copy()
    
    # Apply variable substitutions if provided
    variables = config.get("variables", {})
    if variables:
        # Replace variables in workflow definition (simplified)
        definition_json = json.dumps(customized_definition)
        for var_name, var_value in variables.items():
            definition_json = definition_json.replace(f"{{{var_name}}}", str(var_value))
        customized_definition = json.loads(definition_json)
    
    return customized_definition