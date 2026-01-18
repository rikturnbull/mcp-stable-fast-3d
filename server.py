#!/usr/bin/env python3
"""
Stable Fast 3D MCP Server

A Model Context Protocol (MCP) server that provides tools to generate 3D models
from images using Stability AI's Stable Fast 3D API.
"""

import os
import base64
import httpx
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Stable Fast 3D")

# API configuration
STABILITY_API_URL = "https://api.stability.ai/v2beta/3d/stable-fast-3d"


def get_api_key() -> str:
    """Get the Stability AI API key from environment variable."""
    api_key = os.environ.get("STABILITY_API_KEY")
    if not api_key:
        raise ValueError(
            "STABILITY_API_KEY environment variable is not set. "
            "Please set it to your Stability AI API key."
        )
    return api_key


@mcp.tool()
async def generate_3d_model(
    image_path: str,
    output_path: Optional[str] = None,
    texture_resolution: str = "1024",
    foreground_ratio: float = 0.85,
    remesh: str = "none",
    vertex_count: int = -1,
) -> str:
    """
    Generate a 3D model (GLB file) from a 2D image using Stability AI's Stable Fast 3D API.

    Args:
        image_path: Path to the input image file (JPEG, PNG, or WebP).
                   The image should have dimensions between 64-2048 pixels per side,
                   with total pixel count between 4,096 and 4,194,304 pixels.
        output_path: Optional path for the output GLB file. If not provided,
                    will save to the same directory as input with .glb extension.
        texture_resolution: Resolution of the textures (albedo and normal maps).
                           Options: "512", "1024" (default), "2048".
                           Higher values = more detail but larger file size.
        foreground_ratio: Controls padding around the object (0.1 to 1.0, default 0.85).
                         Higher = less padding, larger object.
                         Lower = more padding, smaller object.
                         Useful for long/narrow objects viewed from narrow side.
        remesh: Remeshing algorithm for the 3D model.
               Options: "none" (default), "quad", "triangle".
               "quad" is useful for DCC tools like Maya or Blender.
        vertex_count: Target vertex count for mesh simplification (-1 to 20000).
                     -1 (default) means no limit.
                     Lower values = simpler mesh with fewer details.

    Returns:
        A message indicating success with the path to the generated GLB file,
        or an error message if generation failed.
    """
    # Validate parameters
    if texture_resolution not in ["512", "1024", "2048"]:
        return f"Error: texture_resolution must be '512', '1024', or '2048', got '{texture_resolution}'"

    if not 0.1 <= foreground_ratio <= 1.0:
        return f"Error: foreground_ratio must be between 0.1 and 1.0, got {foreground_ratio}"

    if remesh not in ["none", "quad", "triangle"]:
        return f"Error: remesh must be 'none', 'quad', or 'triangle', got '{remesh}'"

    if not -1 <= vertex_count <= 20000:
        return f"Error: vertex_count must be between -1 and 20000, got {vertex_count}"

    # Check if input file exists
    input_path = Path(image_path)
    if not input_path.exists():
        return f"Error: Input image file not found: {image_path}"

    # Validate file extension
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    if input_path.suffix.lower() not in valid_extensions:
        return f"Error: Unsupported image format. Supported formats: JPEG, PNG, WebP"

    # Determine output path
    if output_path:
        out_path = Path(output_path)
    else:
        out_path = input_path.with_suffix(".glb")

    # Get API key
    try:
        api_key = get_api_key()
    except ValueError as e:
        return str(e)

    # Read image file
    try:
        image_data = input_path.read_bytes()
    except Exception as e:
        return f"Error reading image file: {e}"

    # Prepare the request
    headers = {
        "authorization": f"Bearer {api_key}",
    }

    # Prepare multipart form data
    files = {
        "image": (input_path.name, image_data, f"image/{input_path.suffix.lower().strip('.')}"),
    }

    data = {
        "texture_resolution": texture_resolution,
        "foreground_ratio": str(foreground_ratio),
        "remesh": remesh,
    }

    # Only include vertex_count if it's not -1 (the default)
    if vertex_count != -1:
        data["vertex_count"] = str(vertex_count)

    # Make the API request
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                STABILITY_API_URL,
                headers=headers,
                files=files,
                data=data,
            )

            if response.status_code == 200:
                # Save the GLB file
                out_path.write_bytes(response.content)
                return f"Successfully generated 3D model: {out_path}"
            else:
                # Handle error responses
                try:
                    error_data = response.json()
                    error_msg = error_data.get("errors", [str(error_data)])
                    if isinstance(error_msg, list):
                        error_msg = ", ".join(error_msg)
                    return f"API Error ({response.status_code}): {error_msg}"
                except Exception:
                    return f"API Error ({response.status_code}): {response.text}"

    except httpx.TimeoutException:
        return "Error: Request timed out. The API may be experiencing high load. Please try again."
    except Exception as e:
        return f"Error making API request: {e}"


@mcp.tool()
async def generate_3d_model_from_base64(
    image_base64: str,
    image_format: str,
    output_path: str,
    texture_resolution: str = "1024",
    foreground_ratio: float = 0.85,
    remesh: str = "none",
    vertex_count: int = -1,
) -> str:
    """
    Generate a 3D model (GLB file) from a base64-encoded image using Stability AI's Stable Fast 3D API.

    Args:
        image_base64: Base64-encoded image data (without data URL prefix).
        image_format: Format of the image: "jpeg", "png", or "webp".
        output_path: Path for the output GLB file.
        texture_resolution: Resolution of the textures (albedo and normal maps).
                           Options: "512", "1024" (default), "2048".
        foreground_ratio: Controls padding around the object (0.1 to 1.0, default 0.85).
        remesh: Remeshing algorithm: "none" (default), "quad", or "triangle".
        vertex_count: Target vertex count (-1 to 20000, default -1 for no limit).

    Returns:
        A message indicating success with the path to the generated GLB file,
        or an error message if generation failed.
    """
    # Validate parameters
    if image_format.lower() not in ["jpeg", "jpg", "png", "webp"]:
        return f"Error: image_format must be 'jpeg', 'png', or 'webp', got '{image_format}'"

    if texture_resolution not in ["512", "1024", "2048"]:
        return f"Error: texture_resolution must be '512', '1024', or '2048', got '{texture_resolution}'"

    if not 0.1 <= foreground_ratio <= 1.0:
        return f"Error: foreground_ratio must be between 0.1 and 1.0, got {foreground_ratio}"

    if remesh not in ["none", "quad", "triangle"]:
        return f"Error: remesh must be 'none', 'quad', or 'triangle', got '{remesh}'"

    if not -1 <= vertex_count <= 20000:
        return f"Error: vertex_count must be between -1 and 20000, got {vertex_count}"

    # Decode base64 image
    try:
        image_data = base64.b64decode(image_base64)
    except Exception as e:
        return f"Error decoding base64 image: {e}"

    # Get API key
    try:
        api_key = get_api_key()
    except ValueError as e:
        return str(e)

    # Normalize format
    fmt = image_format.lower()
    if fmt == "jpg":
        fmt = "jpeg"

    # Prepare the request
    headers = {
        "authorization": f"Bearer {api_key}",
    }

    files = {
        "image": (f"image.{fmt}", image_data, f"image/{fmt}"),
    }

    data = {
        "texture_resolution": texture_resolution,
        "foreground_ratio": str(foreground_ratio),
        "remesh": remesh,
    }

    if vertex_count != -1:
        data["vertex_count"] = str(vertex_count)

    # Make the API request
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                STABILITY_API_URL,
                headers=headers,
                files=files,
                data=data,
            )

            if response.status_code == 200:
                out_path = Path(output_path)
                out_path.write_bytes(response.content)
                return f"Successfully generated 3D model: {out_path}"
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("errors", [str(error_data)])
                    if isinstance(error_msg, list):
                        error_msg = ", ".join(error_msg)
                    return f"API Error ({response.status_code}): {error_msg}"
                except Exception:
                    return f"API Error ({response.status_code}): {response.text}"

    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except Exception as e:
        return f"Error making API request: {e}"


@mcp.tool()
async def check_api_balance() -> str:
    """
    Check the remaining credit balance for your Stability AI account.

    Returns:
        The current credit balance or an error message.
    """
    try:
        api_key = get_api_key()
    except ValueError as e:
        return str(e)

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.stability.ai/v1/user/balance",
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                credits = data.get("credits", 0)
                return f"Current credit balance: {credits:.2f} credits"
            else:
                return f"Error checking balance ({response.status_code}): {response.text}"

    except Exception as e:
        return f"Error checking balance: {e}"


@mcp.resource("info://stable-fast-3d")
def get_api_info() -> str:
    """
    Get information about the Stable Fast 3D API and its parameters.
    """
    return """
# Stable Fast 3D API Information

## Overview
Stable Fast 3D generates high-quality 3D assets from a single 2D input image.
The output is a GLB file (glTF binary format) that includes:
- 3D mesh geometry
- Albedo (color) texture map
- Normal texture map

## Cost
- **10 credits** per successful generation
- Failed generations are not charged

## Input Image Requirements
- **Formats:** JPEG, PNG, or WebP
- **Dimensions:** Each side must be at least 64 pixels
- **Total pixels:** Between 4,096 and 4,194,304 pixels
- **Best practices:**
  - Use images with a clear subject and clean background
  - Object should be centered in the image
  - Good lighting helps produce better results

## Parameters

### texture_resolution
Resolution of the texture maps (albedo and normal).
- `"512"` - Lower detail, smaller file size
- `"1024"` - Default, good balance
- `"2048"` - Higher detail, larger file size

### foreground_ratio (0.1 - 1.0)
Controls padding around the object.
- Default: `0.85`
- Higher values = less padding, larger object
- Lower values = more padding, smaller object
- Tip: Lower values help with long/narrow objects viewed from the narrow side

### remesh
Controls the mesh topology.
- `"none"` - Default, original mesh
- `"triangle"` - Triangular faces
- `"quad"` - Quadrilateral faces (useful for Maya/Blender)

### vertex_count (-1 to 20000)
Target vertex count for mesh simplification.
- `-1` - No limit (default)
- Lower values create simpler meshes

## Output
The output is a binary GLB file containing:
- JSON metadata
- Geometry buffers
- Texture images

See: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
"""


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
