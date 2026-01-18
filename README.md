# Stable Fast 3D MCP Server

An MCP (Model Context Protocol) server that provides tools to generate 3D models from images using Stability AI's Stable Fast 3D API.

## Features

- **Generate 3D models from images**: Convert any 2D image into a high-quality 3D GLB file
- **Customizable parameters**: Control texture resolution, mesh complexity, and more
- **Base64 support**: Generate from base64-encoded images for programmatic use
- **Credit balance check**: Monitor your Stability AI account balance

## Prerequisites

- Python 3.10 or higher
- A Stability AI API key (get one at https://platform.stability.ai/account/keys)

## Installation

1. Clone or download this repository:
```bash
cd mcp-stable-fast-3d
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set your Stability AI API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:STABILITY_API_KEY = "sk-your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set STABILITY_API_KEY=sk-your-api-key-here
```

**Linux/macOS:**
```bash
export STABILITY_API_KEY="sk-your-api-key-here"
```

## Usage

### Running the Server

```bash
python server.py
```

Or using the installed command:
```bash
mcp-stable-fast-3d
```

### Configuring with Claude Desktop

Add this to your Claude Desktop configuration file (`claude_desktop_config.json`):

**Using uvx from GitHub (recommended - no installation required):**
```json
{
  "mcpServers": {
    "stable-fast-3d": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/YOUR_USERNAME/mcp-stable-fast-3d", "mcp-stable-fast-3d"],
      "env": {
        "STABILITY_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

**Using local installation with Python:**

Windows:
```json
{
  "mcpServers": {
    "stable-fast-3d": {
      "command": "python",
      "args": ["C:\\path\\to\\mcp-stable-fast-3d\\server.py"],
      "env": {
        "STABILITY_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

macOS/Linux:
```json
{
  "mcpServers": {
    "stable-fast-3d": {
      "command": "python",
      "args": ["/path/to/mcp-stable-fast-3d/server.py"],
      "env": {
        "STABILITY_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

### Configuring with VS Code (GitHub Copilot)

Add to your VS Code `settings.json` or create `.vscode/mcp.json` in your project:

**Using uvx from GitHub (recommended):**
```json
{
  "servers": {
    "stable-fast-3d": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/YOUR_USERNAME/mcp-stable-fast-3d", "mcp-stable-fast-3d"],
      "env": {
        "STABILITY_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

**Using local virtual environment:**
```json
{
  "servers": {
    "stable-fast-3d": {
      "command": "c:\\path\\to\\mcp-stable-fast-3d\\.venv\\Scripts\\python.exe",
      "args": ["c:\\path\\to\\mcp-stable-fast-3d\\server.py"],
      "env": {
        "STABILITY_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### `generate_3d_model`

Generate a 3D model (GLB file) from a 2D image file.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_path` | string | Yes | - | Path to input image (JPEG, PNG, or WebP) |
| `output_path` | string | No | Same as input with .glb extension | Path for output GLB file |
| `texture_resolution` | string | No | "1024" | Texture resolution: "512", "1024", or "2048" |
| `foreground_ratio` | float | No | 0.85 | Padding ratio (0.1 to 1.0) |
| `remesh` | string | No | "none" | Remeshing: "none", "quad", or "triangle" |
| `vertex_count` | int | No | -1 | Target vertex count (-1 for no limit) |

**Example:**
```
Generate a 3D model from the image at C:\images\cat-statue.png with high resolution textures
```

### `generate_3d_model_from_base64`

Generate a 3D model from a base64-encoded image.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_base64` | string | Yes | - | Base64-encoded image data |
| `image_format` | string | Yes | - | Image format: "jpeg", "png", or "webp" |
| `output_path` | string | Yes | - | Path for output GLB file |
| `texture_resolution` | string | No | "1024" | Texture resolution |
| `foreground_ratio` | float | No | 0.85 | Padding ratio |
| `remesh` | string | No | "none" | Remeshing algorithm |
| `vertex_count` | int | No | -1 | Target vertex count |

### `check_api_balance`

Check your Stability AI account credit balance.

## API Costs

- **Stable Fast 3D**: 10 credits per successful generation
- Failed generations are not charged

## Input Image Guidelines

For best results:
- Use images with a clear, well-lit subject
- The object should be centered in the frame
- Clean backgrounds work better
- Image dimensions should be between 64×64 and 2048×2048 pixels
- Total pixel count must be between 4,096 and 4,194,304 pixels

## Output Format

The generated 3D model is saved as a GLB file (glTF Binary), which includes:
- 3D mesh geometry
- Albedo (color) texture map
- Normal texture map

GLB files can be viewed in:
- Windows 3D Viewer
- Blender
- Unity/Unreal Engine
- Most modern web browsers (with appropriate viewers)

## Error Handling

The server handles common errors:
- Missing API key
- Invalid image formats
- API rate limiting (150 requests per 10 seconds)
- File not found errors
- Network timeouts

## License

MIT License
