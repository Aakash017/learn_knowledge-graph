# Test the MCP tool logic directly (no MCP overhead)
from services.fetch_market_hubs import get_market_hubs

print("Testing fetch_Market_hubs tool...")
print("-" * 40)

result = get_market_hubs("ERCOT")
print(f"Result: {result}")
