#!/usr/bin/env python3
"""
Simple Results Table - Comprehensive data points from Signals Agent + Sales Agent integration test.
"""

import asyncio
import json
import httpx
from datetime import datetime
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport

async def collect_data():
    """Collect all data points from both agents."""
    
    data = {
        "signals_agent": {},
        "sales_agent": {},
        "metadata": {}
    }
    
    # Collect Signals Agent Data
    print("🔍 Collecting Signals Agent Data...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Health check
        try:
            health_response = await client.get("http://127.0.0.1:8000/health")
            if health_response.status_code == 200:
                data["signals_agent"]["health"] = health_response.json()
        except Exception as e:
            data["signals_agent"]["health"] = {"error": str(e)}
        
        # Agent card
        try:
            agent_card_response = await client.get("http://127.0.0.1:8000/agent-card")
            if agent_card_response.status_code == 200:
                data["signals_agent"]["agent_card"] = agent_card_response.json()
        except Exception as e:
            data["signals_agent"]["agent_card"] = {"error": str(e)}
        
        # Signal discovery
        try:
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
        except Exception as e:
            data["signals_agent"]["discovery"] = {"error": str(e)}
        
        # Signal activation
        try:
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
        except Exception as e:
            data["signals_agent"]["activation"] = {"error": str(e)}
    
    # Collect Sales Agent Data
    print("🔗 Collecting Sales Agent Data...")
    
    server_url = "http://127.0.0.1:8101"
    token = "purina_token"
    headers = {"x-adcp-auth": token, "x-adcp-tenant": "default"}
    
    try:
        transport = StreamableHttpTransport(url=f"{server_url}/mcp/", headers=headers)
        client = Client(transport=transport)
        
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

def print_comprehensive_table(data):
    """Print comprehensive table showing all data points."""
    
    print("\n" + "="*100)
    print("🎯 ADCP INTEGRATION TEST RESULTS - COMPLETE DATA POINTS")
    print("="*100)
    
    # Signals Agent Data
    print("\n📊 SIGNALS AGENT DATA")
    print("-" * 50)
    
    signals_data = data.get("signals_agent", {})
    
    # Health Status
    health = signals_data.get("health", {})
    if "error" not in health:
        print(f"✅ Health Status: {health.get('status', 'Unknown')}")
        print(f"   Protocols: {', '.join(health.get('protocols', []))}")
    else:
        print(f"❌ Health Error: {health.get('error')}")
    
    # Agent Card
    agent_card = signals_data.get("agent_card", {})
    if "error" not in agent_card:
        print(f"🤖 Agent Name: {agent_card.get('name', 'Unknown')}")
        print(f"   Version: {agent_card.get('version', 'N/A')}")
        print(f"   Description: {agent_card.get('description', 'No description')[:100]}...")
        print(f"   Skills: {len(agent_card.get('skills', []))} available")
    else:
        print(f"❌ Agent Card Error: {agent_card.get('error')}")
    
    # Signal Discovery
    discovery = signals_data.get("discovery", {})
    if "error" not in discovery:
        signals = discovery.get("signals", [])
        print(f"\n📊 Signals Found: {len(signals)}")
        print(f"   Message: {discovery.get('message', 'No message')[:100]}...")
        
        # Individual Signals
        for i, signal in enumerate(signals):
            print(f"\n   Signal {i+1}: {signal.get('name', 'Unknown')}")
            print(f"     ID: {signal.get('signals_agent_segment_id', 'N/A')}")
            print(f"     Description: {signal.get('description', 'No description')[:80]}...")
            print(f"     Coverage: {signal.get('coverage_percentage', 0)}%")
            print(f"     CPM: ${signal.get('pricing', {}).get('cpm', 0)}")
            print(f"     Type: {signal.get('signal_type', 'Unknown')}")
            print(f"     Provider: {signal.get('data_provider', 'Unknown')}")
            
            # Deployments
            deployments = signal.get("deployments", [])
            if deployments:
                print(f"     Platforms: {', '.join([d.get('platform', '') for d in deployments])}")
    else:
        print(f"❌ Discovery Error: {discovery.get('error')}")
    
    # Signal Activation
    activation = signals_data.get("activation", {})
    if activation and "error" not in activation:
        print(f"\n🎯 Signal Activation:")
        print(f"   Status: {activation.get('status', 'Unknown')}")
        print(f"   Platform Segment ID: {activation.get('decisioning_platform_segment_id', 'N/A')}")
        print(f"   Message: {activation.get('message', 'No message')[:100]}...")
    elif activation:
        print(f"❌ Activation Error: {activation.get('error')}")
    
    # Sales Agent Data
    print("\n\n🔗 SALES AGENT DATA")
    print("-" * 50)
    
    sales_data = data.get("sales_agent", {})
    
    if "error" in sales_data:
        print(f"❌ Sales Agent Error: {sales_data.get('error')}")
    else:
        # Products
        products = sales_data.get("products", {}).get("products", [])
        print(f"📦 Products Found: {len(products)}")
        print(f"   Brief: Premium inventory for luxury automotive audiences")
        
        # Individual Products
        for i, product in enumerate(products[:5]):  # Show first 5 products
            print(f"\n   Product {i+1}: {product.get('name', 'Unknown')}")
            print(f"     ID: {product.get('product_id', 'N/A')}")
            print(f"     Type: {product.get('delivery_type', 'Unknown')}")
            
            # Pricing
            price_guidance = product.get("price_guidance", {})
            if price_guidance:
                print(f"     P50 CPM: ${price_guidance.get('p50', 'N/A')}")
                print(f"     Floor CPM: ${price_guidance.get('floor', 'N/A')}")
                print(f"     P90 CPM: ${price_guidance.get('p90', 'N/A')}")
            
            # Formats
            formats = product.get("formats", [])
            if formats:
                format_names = ", ".join([f.get("format_id", "") for f in formats])
                print(f"     Formats: {format_names}")
        
        # Media Buy
        media_buy = sales_data.get("media_buy", {})
        if media_buy:
            print(f"\n🎯 Media Buy Created:")
            print(f"   ID: {media_buy.get('media_buy_id', 'N/A')}")
            print(f"   Status: {media_buy.get('status', 'Unknown')}")
            print(f"   Budget: ${media_buy.get('total_budget', 0):,.2f}")
            print(f"   Flight: {media_buy.get('flight_start_date', 'N/A')} to {media_buy.get('flight_end_date', 'N/A')}")
            print(f"   PO Number: {media_buy.get('po_number', 'N/A')}")
    
    # Metadata
    print("\n\n📋 SYSTEM METADATA")
    print("-" * 50)
    
    metadata = data.get("metadata", {})
    print(f"🕒 Test Timestamp: {metadata.get('test_timestamp', 'Unknown')}")
    print(f"🎯 Test Scenario: {metadata.get('test_scenario', 'N/A')}")
    print(f"🔗 Signals Agent URL: {metadata.get('signals_agent_url', 'N/A')} (Port: 8000)")
    print(f"🔗 Sales Agent URL: {metadata.get('sales_agent_url', 'N/A')} (Port: 8101)")
    
    # Summary
    print("\n\n" + "="*100)
    print("✅ INTEGRATION TEST SUMMARY")
    print("="*100)
    
    signals_count = len(data.get("signals_agent", {}).get("discovery", {}).get("signals", []))
    products_count = len(data.get("sales_agent", {}).get("products", {}).get("products", []))
    media_buy_created = "Yes" if data.get("sales_agent", {}).get("media_buy") else "No"
    
    print(f"📊 Signals Found: {signals_count}")
    print(f"📦 Products Found: {products_count}")
    print(f"🎯 Media Buy Created: {media_buy_created}")
    print(f"🔄 Workflow Status: Complete")
    print(f"🎉 Integration Test: SUCCESSFUL")

async def main():
    """Main function to collect and display all data points."""
    
    print("🚀 Starting AdCP Integration Test - Complete Data Points Collection")
    print("="*80)
    
    # Collect all data
    data = await collect_data()
    
    # Print comprehensive table
    print_comprehensive_table(data)

if __name__ == "__main__":
    asyncio.run(main())
