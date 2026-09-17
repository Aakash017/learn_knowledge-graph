# Chatbot Integration with Energy Knowledge Graph using MCP Server

## Overview

This document describes how we integrated a chatbot with an Energy Knowledge Graph using the **Model Context Protocol (MCP)**. The solution enables natural language queries about energy markets, power plants, hubs, and fuel types.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER                                           │
│                    "What power plants supply HB_SOUTH?"                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CHATBOT (LLM)                                     │
│  • Receives natural language question                                       │
│  • Analyzes available MCP tools                                             │
│  • Selects appropriate tool: fetch_power_plants_by_hub("HB_SOUTH")         │
│  • Formats response in natural language                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                          HTTP POST /mcp
                          (JSON-RPC 2.0)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MCP SERVER (Python)                                 │
│  • Endpoint: http://127.0.0.1:8001/mcp                                     │
│  • Protocol: Streamable HTTP (JSON-RPC 2.0)                                │
│  • Exposes 9 tools for knowledge graph queries                             │
│  • Routes requests to service functions                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                          Cypher Query
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NEO4J DATABASE                                      │
│  • Graph database storing energy market data                               │
│  • Entities: Markets, Hubs, PowerPlants, FuelTypes                         │
│  • Relationships: HAS_HUB, SUPPLIES, USES_FUEL                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RESPONSE                                         │
│  "The following power plants supply HB_SOUTH:                              │
│   - WA_Parish (3653 MW, Natural Gas)                                       │
│   - Deer_Park_Energy (1238 MW, Natural Gas)                                │
│   - Gulf_Wind (283 MW, Wind)"                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## What is MCP (Model Context Protocol)?

**MCP** is an open protocol that enables AI assistants/chatbots to interact with external data sources and tools in a standardized way.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **MCP Server** | Exposes tools and resources that AI can use |
| **MCP Client** | The AI/chatbot that connects to MCP servers |
| **Tools** | Functions the AI can call (e.g., `fetch_power_plants`) |
| **Transport** | Communication method: `stdio` or `HTTP` |

### Why MCP?

- **Standardized Interface**: One protocol for all AI-to-tool integrations
- **Tool Discovery**: AI automatically discovers available tools and their parameters
- **Type Safety**: Tools define input/output schemas
- **Flexible Transports**: Works locally (stdio) or over network (HTTP)

---

## Request/Response Flow

### 1. Tool Discovery

When the chatbot connects, it requests available tools:

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "fetch_power_plants_by_hub",
        "description": "Given a hub name, e.g. HB_SOUTH, HB_NORTH, returns all power plants that supply that hub",
        "inputSchema": {
          "type": "object",
          "properties": {
            "hub_name": { "type": "string" }
          },
          "required": ["hub_name"]
        }
      }
      // ... other tools
    ]
  }
}
```

### 2. Tool Invocation

When user asks: *"What power plants supply HB_SOUTH?"*

The LLM selects the appropriate tool and sends:

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "fetch_power_plants_by_hub",
    "arguments": {
      "hub_name": "HB_SOUTH"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"hub_name\": \"HB_SOUTH\", \"power_plants\": [{\"name\": \"WA_Parish\", \"capacity_mw\": 3653, \"fuel_type\": \"Natural Gas\"}, {\"name\": \"Deer_Park_Energy\", \"capacity_mw\": 1238, \"fuel_type\": \"Natural Gas\"}, {\"name\": \"Gulf_Wind\", \"capacity_mw\": 283, \"fuel_type\": \"Wind\"}], \"count\": 3, \"total_capacity_mw\": 5174}"
      }
    ]
  }
}
```

### 3. Response Formatting

The LLM receives the JSON data and formats a natural language response for the user.

---

## MCP Server Implementation

### Server Definition (`server.py`)

```python
from mcp.server.mcpserver import MCPServer
from typing import Any

mcp = MCPServer("Energy Knowledge Graph")

@mcp.tool()
def fetch_power_plants_by_hub(hub_name: str) -> dict[str, Any]:
    """fetch_power_plants_by_hub
    Given a hub name, e.g. HB_SOUTH, HB_NORTH, HB_WEST,
    Returns all power plants that supply that hub with their capacity and fuel type"""
    from services import get_power_plants_by_hub
    return get_power_plants_by_hub(hub_name)
```

### Server Runner (`mcp_run.py`)

```python
from server import mcp

# HTTP mode for chatbot integration
mcp.run(
    transport="streamable-http",
    host="127.0.0.1",
    port=8001,
)
```

### Starting the Server

```bash
# HTTP mode (for chatbot)
uv run mcp_run.py --transport http --port 8001

# Server available at: http://127.0.0.1:8001/mcp
```

---

## Available MCP Tools

| Tool | Input | Description | Example Query |
|------|-------|-------------|---------------|
| `list_markets` | - | List all available markets | "What markets are available?" |
| `fetch_market_hubs` | `market_name` | Get all hubs for a market | "What hubs does ERCOT have?" |
| `fetch_hubs_regions` | `hub_name` | Get regions for a hub | "What region is HB_NORTH in?" |
| `fetch_region_data` | `region_name` | Get data for a region | "Tell me about the North region" |
| `fetch_market_hubs_with_regions` | `market_name` | Get hubs with their regions | "Show me all ERCOT hubs and regions" |
| `fetch_fuel_types` | `market_name` | Get fuel types used in a market | "What fuel types are used in ERCOT?" |
| `fetch_power_plants` | `market_name` | Get all power plants in a market | "What power plants are in ERCOT?" |
| `fetch_power_plants_by_fuel` | `fuel_type` | Get plants by fuel type | "Which plants use wind energy?" |
| `fetch_power_plants_by_hub` | `hub_name` | Get plants supplying a hub | "What plants supply HB_SOUTH?" |

---

## Knowledge Graph Data Model

### Entity Types

```
┌─────────────┐     HAS_HUB      ┌─────────────┐
│   Market    │ ───────────────► │     Hub     │
│   (ERCOT)   │                  │  (HB_SOUTH) │
└─────────────┘                  └─────────────┘
                                       ▲
                                       │ SUPPLIES
                                       │
                                 ┌─────────────┐     USES_FUEL    ┌─────────────┐
                                 │ PowerPlant  │ ────────────────► │  FuelType   │
                                 │ (WA_Parish) │                   │ (Natural Gas)│
                                 └─────────────┘                   └─────────────┘
```

### Current Data (ERCOT Market)

| Entity Type | Count | Examples |
|-------------|-------|----------|
| Market | 1 | ERCOT |
| Hub | 5 | HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST, HB_BUSAVG |
| LoadZone | 4 | LZ_SOUTH, LZ_NORTH, LZ_WEST, LZ_HOUSTON |
| PowerPlant | 8 | WA_Parish, Comanche_Peak, Sweetwater_Wind |
| FuelType | 5 | Coal, Natural Gas, Nuclear, Wind, Solar |

### Relationships

| Relationship | From → To | Count |
|--------------|-----------|-------|
| HAS_HUB | Market → Hub/LoadZone | 9 |
| SUPPLIES | PowerPlant → Hub | 8 |
| USES_FUEL | PowerPlant → FuelType | 8 |

---

## Demo Scenarios

### Scenario 1: Market Overview
**User:** "What markets are available in the knowledge graph?"
**Tool Used:** `list_markets`
**Answer:** ERCOT

### Scenario 2: Hub Discovery
**User:** "What hubs are connected to ERCOT?"
**Tool Used:** `fetch_market_hubs("ERCOT")`
**Answer:** HB_BUSAVG, HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST, LZ_SOUTH, LZ_NORTH, LZ_WEST, LZ_HOUSTON

### Scenario 3: Fuel Mix Analysis
**User:** "What fuel types are used by power plants in ERCOT?"
**Tool Used:** `fetch_fuel_types("ERCOT")`
**Answer:** Coal, Natural Gas, Nuclear, Wind, Solar

### Scenario 4: Hub Supply Analysis
**User:** "What power plants supply HB_SOUTH?"
**Tool Used:** `fetch_power_plants_by_hub("HB_SOUTH")`
**Answer:**
- WA_Parish (3653 MW, Natural Gas)
- Deer_Park_Energy (1238 MW, Natural Gas)
- Gulf_Wind (283 MW, Wind)
- Total Capacity: 5,174 MW

### Scenario 5: Renewable Energy Query
**User:** "Which power plants use wind energy?"
**Tool Used:** `fetch_power_plants_by_fuel("Wind")`
**Answer:**
- Sweetwater_Wind (585 MW) → HB_WEST
- Gulf_Wind (283 MW) → HB_SOUTH

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Knowledge Graph | Neo4j | Graph database for entities & relationships |
| MCP Server | Python + mcp library | Expose tools via MCP protocol |
| Transport | Streamable HTTP | Network communication |
| Chatbot | LLM (Claude/GPT) | Natural language processing |
| Data Format | JSON-RPC 2.0 | Request/response protocol |

---

## Setup Instructions

### 1. Start Neo4j

```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=none \
  -v neo4j_data:/data \
  neo4j:latest
```

### 2. Load Data

```bash
python load_data.py
```

### 3. Start MCP Server

```bash
uv run mcp_run.py --transport http --port 8001
```

### 4. Configure Chatbot

Point chatbot MCP client to: `http://127.0.0.1:8001/mcp`

---

## Future Enhancements

- Add more markets (PJM, NYISO, CAISO, etc.)
- Include pricing data and time series
- Add transmission line relationships
- Implement complex multi-hop queries
- Add authentication/authorization

---

## References

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Energy Knowledge Graph Repository](https://github.com/woodmac/energy-knowledge-graph)
