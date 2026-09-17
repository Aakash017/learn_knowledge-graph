# Energy Knowledge Graph

A Python library for building and querying knowledge graphs focused on energy market data. Built with NetworkX for learning and Neo4j for production. Includes an MCP (Model Context Protocol) server for AI agent integration.

## Screenshots

### Interactive Graph Visualization
![Graph View](docs/images/dashboard-graph.png)

### Custom Cypher Queries
![Query View](docs/images/dashboard-query.png)

## Features

- Create entities with types (Markets, Hubs, Regions, PowerPlants, FuelTypes)
- Define relationships between entities (HAS_HUB, SUPPLIES, USES_FUEL, LOCATED_IN)
- Query related entities by relationship type
- Traverse multi-hop paths through the graph
- Filter entities by type and properties
- **Two backends**: In-memory (NetworkX) and persistent (Neo4j)
- **Interactive dashboard** for visualization and analytics
- **MCP Server**: Expose knowledge graph tools to AI agents via Model Context Protocol

## Installation

Requires Python 3.12+

```bash
uv sync
pip install neo4j
```

## Quick Start

### 1. Start Neo4j Database

```bash
# Start Neo4j with persistent storage (recommended)
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=none \
  -v neo4j_data:/data \
  neo4j:latest

# Or without persistence (data lost on restart)
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=none neo4j:latest
```

### 2. Load Sample Data

```bash
python load_data.py
```

This loads ERCOT market data from CSV files:
- **1 Market**: ERCOT
- **5 Hubs**: HB_HOUSTON, HB_BUSAVG, HB_NORTH, HB_SOUTH, HB_WEST
- **4 Load Zones**: LZ_SOUTH, LZ_NORTH, LZ_WEST, LZ_HOUSTON
- **8 Power Plants**: With capacity, fuel type, and hub connections
- **5 Fuel Types**: Coal, Natural Gas, Nuclear, Wind, Solar

### 3. Verify Data Loaded

Open Neo4j Browser at http://localhost:7474 and run:

```cypher
MATCH (n)-[r]->(m) RETURN n, r, m
```

## Data Loading

### Reload Data After Docker Restart

If you restart Docker or lose Neo4j data:

```bash
python load_data.py
```

The script will:
1. Clear existing data
2. Create the ERCOT market entity
3. Load hubs and load zones from `data/hubs.csv`
4. Load power plants from `data/power_plants.csv`
5. Create all relationships (HAS_HUB, SUPPLIES, USES_FUEL)

### CSV Data Files

**data/hubs.csv** - Hubs and Load Zones:
```csv
name,type,zone,market
HB_HOUSTON,Hub,Houston,ERCOT
LZ_SOUTH,LoadZone,South,ERCOT
```

**data/power_plants.csv** - Power Plants:
```csv
name,type,capacity_mw,fuel,hub,online_year
Limestone_Station,PowerPlant,1850,Coal,HB_NORTH,1985
```

## MCP Server

The project includes an MCP (Model Context Protocol) server that exposes knowledge graph tools to AI agents and chatbots.

### Running the MCP Server

**HTTP Mode** (for chatbots and external clients):

```bash
uv run mcp_run.py --transport http --port 8001
```

The server will be available at `http://127.0.0.1:8001/mcp`

**Stdio Mode** (for Kiro/IDE integration):

```bash
uv run mcp_run.py
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--transport` | `stdio` | Transport mode: `stdio` or `http` |
| `--host` | `127.0.0.1` | Host to bind (HTTP mode) |
| `--port` | `8001` | Port to listen on (HTTP mode) |

### Available MCP Tools

| Tool | Description | Example Query |
|------|-------------|---------------|
| `list_markets` | List all available markets | "What markets are available?" |
| `fetch_market_hubs` | Get all hubs for a market | "What hubs does ERCOT have?" |
| `fetch_hubs_regions` | Get regions for a hub | "What region is HB_NORTH in?" |
| `fetch_region_data` | Get data for a region | "Tell me about the North region" |
| `fetch_market_hubs_with_regions` | Get hubs with their regions | "Show me all ERCOT hubs and regions" |
| `fetch_fuel_types` | Get fuel types for a market | "What fuel types are used in ERCOT?" |
| `fetch_power_plants` | Get power plants for a market | "What power plants are in ERCOT?" |
| `fetch_power_plants_by_fuel` | Get plants by fuel type | "Which plants use wind energy?" |
| `fetch_power_plants_by_hub` | Get plants supplying a hub | "What plants supply HB_SOUTH?" |

### Sample Questions for Testing

```
1. "What markets are available in the knowledge graph?"
   → ERCOT

2. "What hubs are connected to ERCOT?"
   → HB_BUSAVG, HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST, LZ_SOUTH, LZ_NORTH, LZ_WEST, LZ_HOUSTON

3. "What fuel types are used by power plants in ERCOT?"
   → Coal, Natural Gas, Nuclear, Wind, Solar

4. "What power plants are in ERCOT?"
   → 8 plants with capacity, fuel type, and hub

5. "Which power plants use wind energy?"
   → Sweetwater_Wind (585 MW), Gulf_Wind (283 MW)

6. "What power plants supply HB_SOUTH?"
   → WA_Parish (3653 MW), Deer_Park_Energy (1238 MW), Gulf_Wind (283 MW)
```

### Kiro IDE Configuration

Add to `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "energy-kg": {
      "command": "uv",
      "args": ["run", "mcp_run.py"],
      "cwd": "/path/to/energy-knowledge-graph"
    }
  }
}
```

### HTTP Client Configuration

For chatbots or external clients using HTTP:

```json
{
  "mcpServers": {
    "energy-kg": {
      "url": "http://127.0.0.1:8001/mcp",
      "type": "streamable-http"
    }
  }
}
```

## In-Memory Graph (Alternative)

For testing without Neo4j, use the NetworkX backend:

```python
from src.energy_kg.graph import EnergyKnowledgeGraph

kg = EnergyKnowledgeGraph()

# Add entities
kg.add_entity("ERCOT", "Market")
kg.add_entity("HB_SOUTH", "Hub")
kg.add_entity("South Texas", "Region")

# Add relationships
kg.add_relationship("ERCOT", "HB_SOUTH", "HAS_HUB")
kg.add_relationship("HB_SOUTH", "South Texas", "LOCATED_IN")

# Query
hubs = kg.get_related_entities("ERCOT", "HAS_HUB")
regions = kg.traverse("ERCOT", ["HAS_HUB", "LOCATED_IN"])
```

## Visualization Dashboard

```bash
uv run streamlit run dashboard.py
```

Open http://localhost:8501 for:
- **Graph View**: Interactive network visualization
- **Analytics**: Capacity by fuel type, renewable energy mix
- **Query**: Run custom Cypher queries

## Neo4j Browser

Access http://localhost:7474 for the native Neo4j visualization. Try:

```cypher
-- View entire graph
MATCH (n)-[r]->(m) RETURN n, r, m

-- Find power plants by fuel
MATCH (p:Entity {type: 'PowerPlant'})-[:USES_FUEL]->(f)
RETURN p.name, f.name

-- Total capacity by fuel type
MATCH (p:Entity {type: 'PowerPlant'})-[:USES_FUEL]->(f)
RETURN f.name, sum(p.capacity_mw) AS capacity
ORDER BY capacity DESC

-- Power plants supplying each hub
MATCH (p:Entity {type: 'PowerPlant'})-[:SUPPLIES]->(h)
RETURN h.name AS hub, collect(p.name) AS plants
```

## Project Structure

```
energy-knowledge-graph/
├── src/energy_kg/
│   ├── graph.py          # NetworkX backend
│   └── neo4j_graph.py    # Neo4j backend
├── data/
│   ├── power_plants.csv  # Sample power plant data
│   └── hubs.csv          # Sample hub/zone data
├── main.py               # NetworkX example
├── main_neo4j.py         # Neo4j example
├── load_data.py          # CSV data loader
├── dashboard.py          # Streamlit visualization
├── server.py             # MCP server definition
├── mcp_run.py            # MCP server runner
├── services.py           # Knowledge graph service functions
└── README.md
```

## Entity Types

| Type | Description | Example |
|------|-------------|---------|
| Market | Power market/ISO | ERCOT |
| Hub | Pricing/trading point | HB_SOUTH, HB_NORTH |
| LoadZone | Demand area | LZ_SOUTH, LZ_WEST |
| Region | Geographic area | South Texas |
| PowerPlant | Generation facility | Limestone_Station |
| FuelType | Energy source | Natural Gas, Solar |

## Relationships

| Relationship | From → To | Meaning |
|--------------|-----------|---------|
| HAS_HUB | Market → Hub/LoadZone | Market contains hub |
| LOCATED_IN | Hub → Region | Hub location |
| SUPPLIES | PowerPlant → Hub | Plant feeds hub |
| USES_FUEL | PowerPlant → FuelType | Plant's fuel source |

## Troubleshooting

### Neo4j Connection Error

```
ServiceUnavailable: Unable to retrieve routing information
```

**Solution**: Make sure Neo4j is running:
```bash
docker ps  # Check if neo4j container is running
docker start neo4j  # Start if stopped
```

### Data Not Showing in Graph

**Solution**: Reload the data:
```bash
python load_data.py
```

### MCP Tools Not Working

**Solution**: 
1. Restart the MCP server
2. Make sure Neo4j is running and data is loaded
3. Check the server logs for errors

## Dependencies

- networkx >= 3.6.1
- neo4j >= 5.0.0
- streamlit >= 1.0.0
- pyvis >= 0.3.0
- mcp[cli] >= 2.0.0

## Roadmap / What's Next

### Short-Term Enhancements
- [ ] Add more markets (PJM, NYISO, CAISO, MISO, SPP)
- [ ] Add transmission line relationships between hubs
- [ ] Add more MCP tools (total capacity, renewable percentage, market comparison)
- [ ] Add historical pricing data (LMPs)

### Medium-Term (Production-Ready)
- [ ] Add authentication to MCP server (API keys)
- [ ] Connection pooling and retry logic
- [ ] Logging and observability
- [ ] Query caching for performance
- [ ] Containerize with Docker for deployment

### Long-Term Vision
- [ ] Connect to real data sources (EIA, ERCOT OASIS, PJM Data Miner)
- [ ] Build agent workflows for complex multi-step analysis
- [ ] Add write operations via chat
- [ ] Multi-tenant support with role-based access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
