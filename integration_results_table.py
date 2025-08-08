#!/usr/bin/env python3
"""
Integration Results Table - Comprehensive data points from Signals Agent + Sales Agent integration test.
"""

import asyncio
import json
import httpx
from datetime import datetime
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

async def collect_all_data():
    """Collect all data points from both agents."""
    
    data = {
        "signals_agent": {},
        "sales_agent": {},
        "combined_workflow": {},
        "metadata": {}
    }
    
    # Collect Signals Agent Data
    console.print("\n🔍 Collecting Signals Agent Data...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Health check
        health_response = await client.get("http://127.0.0.1:8000/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            data["signals_agent"]["health"] = health_data
        
        # Agent card
        agent_card_response = await client.get("http://127.0.0.1:8000/agent-card")
        if agent_card_response.status_code == 200:
            agent_card = agent_card_response.json()
            data["signals_agent"]["agent_card"] = agent_card
        
        # Signal discovery
        discovery_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_signals",
                "arguments": {
                    "signal_spec": "luxury automotive high income audiences",
                    "deliver_to": {
                        "platforms": "all",
                        "countries": ["US"]
                    },
                    "max_results": 5
                }
            },
            "id": 1
        }
        
        discovery_response = await client.post(
            "http://127.0.0.1:8000/mcp/",
            json=discovery_request,
            headers={"Content-Type": "application/json"}
        )
        
        if discovery_response.status_code == 200:
            discovery_data = discovery_response.json()
            data["signals_agent"]["discovery"] = discovery_data.get('result', {})
        
        # Signal activation
        if data["signals_agent"].get("discovery", {}).get("signals"):
            first_signal = data["signals_agent"]["discovery"]["signals"][0]
            activation_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "activate_signal",
                    "arguments": {
                        "signals_agent_segment_id": first_signal.get('signals_agent_segment_id'),
                        "platform": "index-exchange",
                        "account": None
                    }
                },
                "id": 2
            }
            
            activation_response = await client.post(
                "http://127.0.0.1:8000/mcp/",
                json=activation_request,
                headers={"Content-Type": "application/json"}
            )
            
            if activation_response.status_code == 200:
                activation_data = activation_response.json()
                data["signals_agent"]["activation"] = activation_data.get('result', {})
    
    # Collect Sales Agent Data
    console.print("\n🔗 Collecting Sales Agent Data...")
    
    server_url = "http://127.0.0.1:8101"
    token = "purina_token"
    headers = {"x-adcp-auth": token, "x-adcp-tenant": "default"}
    
    transport = StreamableHttpTransport(url=f"{server_url}/mcp/", headers=headers)
    client = Client(transport=transport)
    
    try:
        async with client:
            # Product discovery
            result = await client.call_tool("get_products", {
                "req": {
                    "brief": "Premium video inventory for luxury automotive audiences",
                    "promoted_offering": "Luxury automotive brand campaign"
                }
            })
            
            if hasattr(result, 'structured_content'):
                products_data = result.structured_content
            else:
                products_data = result.content if hasattr(result, 'content') else result
            
            data["sales_agent"]["products"] = products_data
            
            # Media buy creation
            if products_data.get('products'):
                product_ids = [p.get("product_id") for p in products_data['products'][:2]]
                
                media_buy_result = await client.call_tool("create_media_buy", {
                    "req": {
                        "product_ids": product_ids,
                        "flight_start_date": "2025-10-01",
                        "flight_end_date": "2025-10-31",
                        "total_budget": 50000.0,
                        "targeting_overlay": {
                            "geo_country_any_of": ["US"],
                            "device_type_any_of": ["mobile", "desktop"],
                            "content_cat_any_of": ["automotive", "luxury"]
                        },
                        "po_number": "PO-LUXURY-AUTO-2025-10",
                        "pacing": "even"
                    }
                })
                
                if hasattr(media_buy_result, 'structured_content'):
                    media_buy_data = media_buy_result.structured_content
                else:
                    media_buy_data = media_buy_result.content if hasattr(media_buy_result, 'content') else media_buy_result
                
                data["sales_agent"]["media_buy"] = media_buy_data
    except Exception as e:
        data["sales_agent"]["error"] = str(e)
    
    # Metadata
    data["metadata"] = {
        "test_timestamp": datetime.now().isoformat(),
        "signals_agent_url": "http://127.0.0.1:8000",
        "sales_agent_url": "http://127.0.0.1:8101",
        "test_scenario": "Luxury Automotive Campaign with Signal Enhancement"
    }
    
    return data

def create_comprehensive_table(data):
    """Create comprehensive tables showing all data points."""
    
    # Main Results Table
    main_table = Table(title="🎯 AdCP Integration Test Results - Complete Data Points", show_header=True, header_style="bold magenta")
    main_table.add_column("Category", style="cyan", no_wrap=True)
    main_table.add_column("Metric", style="green")
    main_table.add_column("Value", style="yellow")
    main_table.add_column("Details", style="white")
    
    # Signals Agent Data
    signals_data = data.get("signals_agent", {})
    
    # Health Status
    health = signals_data.get("health", {})
    main_table.add_row(
        "Signals Agent",
        "Health Status",
        health.get("status", "Unknown"),
        f"Protocols: {', '.join(health.get('protocols', []))}"
    )
    
    # Agent Card
    agent_card = signals_data.get("agent_card", {})
    main_table.add_row(
        "Signals Agent",
        "Agent Name",
        agent_card.get("name", "Unknown"),
        f"Version: {agent_card.get('version', 'N/A')}"
    )
    
    main_table.add_row(
        "Signals Agent",
        "Description",
        agent_card.get("description", "No description")[:50] + "...",
        f"Skills: {len(agent_card.get('skills', []))} available"
    )
    
    # Signal Discovery
    discovery = signals_data.get("discovery", {})
    signals = discovery.get("signals", [])
    main_table.add_row(
        "Signals Agent",
        "Signals Found",
        str(len(signals)),
        discovery.get("message", "No message")[:50] + "..."
    )
    
    # Individual Signals
    for i, signal in enumerate(signals):
        main_table.add_row(
            "Signals Agent",
            f"Signal {i+1}",
            signal.get("name", "Unknown"),
            f"Coverage: {signal.get('coverage_percentage', 0)}% | CPM: ${signal.get('pricing', {}).get('cpm', 0)}"
        )
        
        main_table.add_row(
            "Signals Agent",
            f"Signal {i+1} ID",
            signal.get("signals_agent_segment_id", "N/A"),
            f"Type: {signal.get('signal_type', 'Unknown')} | Provider: {signal.get('data_provider', 'Unknown')}"
        )
    
    # Signal Activation
    activation = signals_data.get("activation", {})
    if activation:
        main_table.add_row(
            "Signals Agent",
            "Signal Activation",
            activation.get("status", "Unknown"),
            f"Platform Segment ID: {activation.get('decisioning_platform_segment_id', 'N/A')}"
        )
    
    # Sales Agent Data
    sales_data = data.get("sales_agent", {})
    
    # Products
    products = sales_data.get("products", {}).get("products", [])
    main_table.add_row(
        "Sales Agent",
        "Products Found",
        str(len(products)),
        "Premium inventory for luxury automotive audiences"
    )
    
    # Individual Products
    for i, product in enumerate(products[:5]):  # Show first 5 products
        main_table.add_row(
            "Sales Agent",
            f"Product {i+1}",
            product.get("name", "Unknown"),
            f"Type: {product.get('delivery_type', 'Unknown')} | ID: {product.get('product_id', 'N/A')}"
        )
        
        if product.get("price_guidance"):
            price_info = product["price_guidance"]
            main_table.add_row(
                "Sales Agent",
                f"Product {i+1} Pricing",
                f"${price_info.get('p50', 'N/A')} CPM",
                f"Floor: ${price_info.get('floor', 'N/A')} | P90: ${price_info.get('p90', 'N/A')}"
            )
    
    # Media Buy
    media_buy = sales_data.get("media_buy", {})
    if media_buy:
        main_table.add_row(
            "Sales Agent",
            "Media Buy ID",
            media_buy.get("media_buy_id", "N/A"),
            f"Status: {media_buy.get('status', 'Unknown')}"
        )
        
        main_table.add_row(
            "Sales Agent",
            "Media Buy Budget",
            f"${media_buy.get('total_budget', 0):,.2f}",
            f"Flight: {media_buy.get('flight_start_date', 'N/A')} to {media_buy.get('flight_end_date', 'N/A')}"
        )
    
    # Metadata
    metadata = data.get("metadata", {})
    main_table.add_row(
        "System",
        "Test Timestamp",
        metadata.get("test_timestamp", "Unknown"),
        f"Scenario: {metadata.get('test_scenario', 'N/A')}"
    )
    
    main_table.add_row(
        "System",
        "Signals Agent URL",
        metadata.get("signals_agent_url", "N/A"),
        "Port: 8000"
    )
    
    main_table.add_row(
        "System",
        "Sales Agent URL",
        metadata.get("sales_agent_url", "N/A"),
        "Port: 8101"
    )
    
    return main_table

def create_signals_detail_table(data):
    """Create detailed signals table."""
    
    signals = data.get("signals_agent", {}).get("discovery", {}).get("signals", [])
    
    if not signals:
        return None
    
    signals_table = Table(title="📊 Detailed Signals Analysis", show_header=True, header_style="bold blue")
    signals_table.add_column("Signal Name", style="cyan", no_wrap=True)
    signals_table.add_column("Coverage %", style="green", justify="right")
    signals_table.add_column("CPM $", style="yellow", justify="right")
    signals_table.add_column("Type", style="magenta")
    signals_table.add_column("Provider", style="white")
    signals_table.add_column("Platforms", style="white")
    signals_table.add_column("Description", style="white")
    
    for signal in signals:
        deployments = signal.get("deployments", [])
        platforms = ", ".join([d.get("platform", "") for d in deployments]) if deployments else "N/A"
        
        signals_table.add_row(
            signal.get("name", "Unknown"),
            f"{signal.get('coverage_percentage', 0):.1f}%",
            f"${signal.get('pricing', {}).get('cpm', 0):.2f}",
            signal.get("signal_type", "Unknown"),
            signal.get("data_provider", "Unknown"),
            platforms,
            signal.get("description", "No description")[:60] + "..." if len(signal.get("description", "")) > 60 else signal.get("description", "No description")
        )
    
    return signals_table

def create_products_detail_table(data):
    """Create detailed products table."""
    
    products = data.get("sales_agent", {}).get("products", {}).get("products", [])
    
    if not products:
        return None
    
    products_table = Table(title="📦 Detailed Products Analysis", show_header=True, header_style="bold green")
    products_table.add_column("Product Name", style="cyan", no_wrap=True)
    products_table.add_column("Delivery Type", style="magenta")
    products_table.add_column("Product ID", style="yellow")
    products_table.add_column("P50 CPM $", style="green", justify="right")
    products_table.add_column("Floor CPM $", style="green", justify="right")
    products_table.add_column("P90 CPM $", style="green", justify="right")
    products_table.add_column("Formats", style="white")
    
    for product in products:
        price_guidance = product.get("price_guidance", {})
        formats = product.get("formats", [])
        format_names = ", ".join([f.get("format_id", "") for f in formats]) if formats else "N/A"
        
        products_table.add_row(
            product.get("name", "Unknown"),
            product.get("delivery_type", "Unknown"),
            product.get("product_id", "N/A"),
            f"${price_guidance.get('p50', 'N/A')}" if price_guidance.get('p50') else "N/A",
            f"${price_guidance.get('floor', 'N/A')}" if price_guidance.get('floor') else "N/A",
            f"${price_guidance.get('p90', 'N/A')}" if price_guidance.get('p90') else "N/A",
            format_names
        )
    
    return products_table

async def main():
    """Main function to collect and display all data points."""
    
    console.print(Panel.fit("🎯 AdCP Integration Test - Complete Data Points Collection", style="bold blue"))
    
    # Collect all data
    data = await collect_all_data()
    
    # Create and display tables
    console.print("\n" + "="*80)
    
    # Main comprehensive table
    main_table = create_comprehensive_table(data)
    console.print(main_table)
    
    # Detailed signals table
    signals_table = create_signals_detail_table(data)
    if signals_table:
        console.print("\n")
        console.print(signals_table)
    
    # Detailed products table
    products_table = create_products_detail_table(data)
    if products_table:
        console.print("\n")
        console.print(products_table)
    
    # Summary
    console.print("\n" + "="*80)
    console.print(Panel.fit(
        f"✅ Integration Test Summary\n\n"
        f"📊 Signals Found: {len(data.get('signals_agent', {}).get('discovery', {}).get('signals', []))}\n"
        f"📦 Products Found: {len(data.get('sales_agent', {}).get('products', {}).get('products', []))}\n"
        f"🎯 Media Buy Created: {'Yes' if data.get('sales_agent', {}).get('media_buy') else 'No'}\n"
        f"🔄 Workflow Status: Complete",
        style="bold green"
    ))

if __name__ == "__main__":
    asyncio.run(main())
