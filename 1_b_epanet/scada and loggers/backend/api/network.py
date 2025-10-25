"""
Network API endpoints
Handles network file upload and information retrieval
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
from typing import Dict, Any
import os
import shutil
from pathlib import Path
from datetime import datetime

from services.network_loader import NetworkLoader
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

# Create router
router = APIRouter()

# Global network loader instance
network_loader = NetworkLoader()

@router.post("/upload")
async def upload_network_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload an EPANET .inp file and parse network information
    
    Args:
        file: Uploaded .inp file
        
    Returns:
        Network information and statistics
    """
    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {ALLOWED_EXTENSIONS}"
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Load network with EPyT
        result = network_loader.load_network(str(file_path))
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Network uploaded and parsed successfully",
                    "filename": filename,
                    "file_size": len(file_content),
                    "uploaded_at": datetime.now().isoformat(),
                    **result
                }
            )
        else:
            # Clean up failed upload
            if file_path.exists():
                file_path.unlink()
            
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on any error
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/info")
async def get_network_info() -> Dict[str, Any]:
    """
    Get information about the currently loaded network
    
    Returns:
        Network summary and details
    """
    if not network_loader.is_network_loaded():
        raise HTTPException(
            status_code=404,
            detail="No network loaded. Please upload a network file first."
        )
    
    try:
        summary = network_loader.get_network_summary()
        return JSONResponse(
            status_code=200,
            content={
                "message": "Network information retrieved successfully",
                "timestamp": datetime.now().isoformat(),
                **summary
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get network information: {str(e)}"
        )

@router.get("/coordinates")
async def get_network_coordinates() -> Dict[str, Any]:
    """
    Get node coordinates for network visualization
    
    Returns:
        Node coordinates for plotting
    """
    if not network_loader.is_network_loaded():
        raise HTTPException(
            status_code=404,
            detail="No network loaded. Please upload a network file first."
        )
    
    try:
        coordinates = network_loader.get_node_coordinates()
        
        if not coordinates:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No coordinates available in this network file",
                    "coordinates": {},
                    "has_coordinates": False
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Network coordinates retrieved successfully",
                "coordinates": coordinates,
                "has_coordinates": True,
                "node_count": len(coordinates)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get coordinates: {str(e)}"
        )

@router.get("/status")
async def get_network_status() -> Dict[str, Any]:
    """
    Get the current network loading status
    
    Returns:
        Status information
    """
    return JSONResponse(
        status_code=200,
        content={
            "network_loaded": network_loader.is_network_loaded(),
            "timestamp": datetime.now().isoformat(),
            "message": "Network status retrieved successfully"
        }
    )

@router.delete("/clear")
async def clear_network() -> Dict[str, Any]:
    """
    Clear the currently loaded network
    
    Returns:
        Confirmation message
    """
    try:
        network_loader.clear_network()
        
        # Clean up uploaded files
        for file_path in UPLOAD_DIR.glob("*.inp"):
            try:
                file_path.unlink()
            except:
                pass  # Ignore errors when cleaning up
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Network cleared successfully",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear network: {str(e)}"
        )

@router.get("/data")
async def get_network_data() -> Dict[str, Any]:
    """
    Get raw network data for client-side plotting
    
    Returns:
        Network data including coordinates, connectivity, and metadata
    """
    if not network_loader.is_network_loaded():
        raise HTTPException(
            status_code=404,
            detail="No network loaded. Please upload a network file first."
        )
    
    try:
        # Get the EPANET network object
        network = network_loader.get_network()
        if not network:
            raise HTTPException(
                status_code=500,
                detail="Network object not available"
            )
        
        # Extract network data for client-side plotting
        try:
            # Get node coordinates
            coords = network.getNodeCoordinates()
            
            # Get node information
            node_ids = network.getNodeNameID()
            node_types = network.getNodeType()
            
            # Get link information
            link_ids = network.getLinkNameID()
            link_types = network.getLinkType()
            
            # Get connectivity data
            connectivity = []
            for i in range(len(link_ids)):
                from_node = network.getLinkConnections()[i][0]
                to_node = network.getLinkConnections()[i][1]
                connectivity.append({
                    "link_id": link_ids[i],
                    "link_type": link_types[i],
                    "from_node": from_node,
                    "to_node": to_node
                })
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Network data retrieved successfully",
                    "coordinates": coords,
                    "node_ids": node_ids,
                    "node_types": node_types,
                    "link_ids": link_ids,
                    "link_types": link_types,
                    "connectivity": connectivity,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract network data: {str(e)}"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get network data: {str(e)}"
        )

@router.get("/test")
async def test_network_api() -> Dict[str, Any]:
    """
    Test endpoint to verify network API is working
    
    Returns:
        Test response
    """
    return JSONResponse(
        status_code=200,
        content={
            "message": "Network API is working",
            "endpoints": {
                "upload": "POST /api/network/upload",
                "info": "GET /api/network/info",
                "coordinates": "GET /api/network/coordinates",
                "data": "GET /api/network/data",
                "status": "GET /api/network/status",
                "clear": "DELETE /api/network/clear"
            },
            "timestamp": datetime.now().isoformat()
        }
    )
