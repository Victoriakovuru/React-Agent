@router.post("/api/document", tags=["document"])
async def add_document(request: DocumentRequest):
    """Document addition endpoint"""
    try:
        # Create the tool input in the correct format
        tool_input = {
            "content": request.content,
            "metadata": {
                **request.metadata,
                "added_by": "Victoriakovuru",
                "added_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        result = await VectorStore.arun(tool_input)  # Pass as single argument
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "user": "Victoriakovuru",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )