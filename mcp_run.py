from server import mcp
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Energy Knowledge Graph MCP server")

    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport to use: 'stdio' (default) or 'http'",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to when using HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to listen on when using HTTP transport (default: 8001)",
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="URL path for the MCP endpoint when using HTTP transport (default: /mcp)",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.transport == "http":
        print(f"Starting MCP server in HTTP mode on {args.host}:{args.port}/mcp...")
        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
        )
    else:
        # Default to stdio mode
        mcp.run()


if __name__ == "__main__":
    main()
