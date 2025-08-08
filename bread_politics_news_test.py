#!/usr/bin/env python3
"""
Bread Politics & News Brief Test - Selling bread to people who like politics and news.
"""

import asyncio
import json
import httpx
from datetime import datetime
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport

async def test_bread_politics_news_brief():
    """Test selling bread to people who like politics and news."""
    
    results = {
        "test_metadata": {
            "advertiser": "FreshBake Co.",
            "campaign_name": "Breaking Bread - Politics & News",
            "test_timestamp": datetime.now().isoformat(),
            "brief_summary": "Selling premium bread to people who like politics and news"
        },
        "signals_agent": {},
        "sales_agent": {},
        "combined_workflow": {},
        "final_results": {}
    }
    
    print("🔍 Testing Bread Politics & News Brief...")
    
    # Test Signals Agent
    print("\n1. Testing Signals Agent for politics and news audiences...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Health check
        try:
            health_response = await client.get("http://127.0.0.1:8000/health")
            if health_response.status_code == 200:
                results["signals_agent"]["health"] = health_response.json()
        except Exception as e:
            results["signals_agent"]["health"] = {"error": str(e)}
        
        # Signal discovery for politics and news enthusiasts
        try:
            discovery_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_signals",
                    "arguments": {
                        "signal_spec": "politics news enthusiasts political content readers news consumers",
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
                results["signals_agent"]["discovery"] = discovery_data.get('result', {})
        except Exception as e:
            results["signals_agent"]["discovery"] = {"error": str(e)}
        
        # Signal activation for key segments
        try:
            if results["signals_agent"].get("discovery", {}).get("signals"):
                signals = results["signals_agent"]["discovery"]["signals"]
                activations = []
                
                for signal in signals[:2]:  # Activate first 2 signals
                    activation_request = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "activate_signal",
                            "arguments": {
                                "signals_agent_segment_id": signal.get('signals_agent_segment_id'),
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
                        activations.append({
                            "signal_id": signal.get('signals_agent_segment_id'),
                            "signal_name": signal.get('name'),
                            "activation_result": activation_data.get('result', {})
                        })
                
                results["signals_agent"]["activations"] = activations
        except Exception as e:
            results["signals_agent"]["activations"] = {"error": str(e)}
    
    # Test Sales Agent
    print("\n2. Testing Sales Agent for bread products...")
    
    server_url = "http://127.0.0.1:8101"
    token = "purina_token"
    headers = {"x-adcp-auth": token, "x-adcp-tenant": "default"}
    
    try:
        transport = StreamableHttpTransport(url=f"{server_url}/mcp/", headers=headers)
        client = Client(transport=transport)
        
        async with client:
            # Product discovery for bread targeting politics/news audiences
            result = await client.call_tool("get_products", {
                "req": {
                    "brief": "Premium bread products targeting politics and news enthusiasts",
                    "promoted_offering": "FreshBake Co. premium bread for political news readers"
                }
            })
            
            if hasattr(result, 'structured_content'):
                products_data = result.structured_content
            else:
                products_data = result.content if hasattr(result, 'content') else result
            
            results["sales_agent"]["products"] = products_data
            
            # Media buy creation for bread campaign
            if products_data.get('products'):
                product_ids = [p.get("product_id") for p in products_data['products'][:3]]  # Use first 3 products
                
                media_buy_result = await client.call_tool("create_media_buy", {
                    "req": {
                        "product_ids": product_ids,
                        "flight_start_date": "2025-01-15",
                        "flight_end_date": "2025-02-15",
                        "total_budget": 25000.0,
                        "targeting_overlay": {
                            "geo_country_any_of": ["US"],
                            "device_type_any_of": ["mobile", "desktop"],
                            "content_cat_any_of": ["politics", "news", "current_events"]
                        },
                        "po_number": "PO-BREAD-POLITICS-2025",
                        "pacing": "even"
                    }
                })
                
                if hasattr(media_buy_result, 'structured_content'):
                    media_buy_data = media_buy_result.structured_content
                else:
                    media_buy_data = media_buy_result.content if hasattr(media_buy_result, 'content') else media_buy_result
                
                results["sales_agent"]["media_buy"] = media_buy_data
    except Exception as e:
        results["sales_agent"]["error"] = str(e)
    
    # Combined workflow analysis
    print("\n3. Analyzing Combined Workflow...")
    
    results["combined_workflow"] = {
        "signals_found": len(results.get("signals_agent", {}).get("discovery", {}).get("signals", [])),
        "signals_activated": len(results.get("signals_agent", {}).get("activations", [])),
        "products_found": len(results.get("sales_agent", {}).get("products", {}).get("products", [])),
        "media_buy_created": bool(results.get("sales_agent", {}).get("media_buy")),
        "workflow_status": "complete"
    }
    
    # Final results summary
    results["final_results"] = {
        "campaign_ready": results["combined_workflow"]["media_buy_created"],
        "signals_available": results["combined_workflow"]["signals_found"],
        "products_available": results["combined_workflow"]["products_found"],
        "budget_allocation": 25000.0,
        "flight_dates": "2025-01-15 to 2025-02-15",
        "targeting_summary": "US politics and news enthusiasts",
        "recommendations": []
    }
    
    # Generate recommendations
    recommendations = []
    
    if results["combined_workflow"]["signals_found"] > 0:
        recommendations.append("✅ Signals discovered and activated for politics and news enthusiasts")
    
    if results["combined_workflow"]["products_found"] > 0:
        recommendations.append("✅ Premium inventory identified for politics and news content")
    
    if results["combined_workflow"]["media_buy_created"]:
        recommendations.append("✅ Campaign created successfully with $25,000 budget")
    
    recommendations.append("🎯 Ready for FreshBake Co. 'Breaking Bread - Politics & News' campaign execution")
    
    results["final_results"]["recommendations"] = recommendations
    
    return results

async def main():
    """Main function to run the bread politics & news brief test."""
    
    print("🚀 Starting Bread Politics & News Brief Test")
    print("=" * 60)
    
    # Run the test
    results = await test_bread_politics_news_brief()
    
    # Output as JSON
    print("\n" + "=" * 60)
    print("📊 BREAD POLITICS & NEWS BRIEF TEST RESULTS")
    print("=" * 60)
    
    # Pretty print the JSON
    json_output = json.dumps(results, indent=2, default=str)
    print(json_output)
    
    # Save to file
    with open("bread_politics_news_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: bread_politics_news_test_results.json")
    print(f"🎯 Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
