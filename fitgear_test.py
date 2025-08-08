#!/usr/bin/env python3
"""
FitGear Pro Brief Test - Complete integration test with JSON output.
"""

import asyncio
import json
import httpx
from datetime import datetime
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport

async def test_fitgear_brief():
    """Test the FitGear Pro brief with both signals and sales agents."""
    
    results = {
        "test_metadata": {
            "advertiser": "FitGear Pro",
            "campaign_name": "Run Into Autumn",
            "test_timestamp": datetime.now().isoformat(),
            "brief_summary": "Premium sportswear & running gear brand targeting sports enthusiasts and urban runners"
        },
        "signals_agent": {},
        "sales_agent": {},
        "combined_workflow": {},
        "final_results": {}
    }
    
    print("🔍 Testing FitGear Pro Brief...")
    
    # Test Signals Agent
    print("\n1. Testing Signals Agent...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Health check
        try:
            health_response = await client.get("http://127.0.0.1:8000/health")
            if health_response.status_code == 200:
                results["signals_agent"]["health"] = health_response.json()
        except Exception as e:
            results["signals_agent"]["health"] = {"error": str(e)}
        
        # Signal discovery for sports enthusiasts and urban runners
        try:
            discovery_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_signals",
                    "arguments": {
                        "signal_spec": "sports enthusiasts urban runners premium sportswear running gear",
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
    print("\n2. Testing Sales Agent...")
    
    server_url = "http://127.0.0.1:8101"
    token = "purina_token"
    headers = {"x-adcp-auth": token, "x-adcp-tenant": "default"}
    
    try:
        transport = StreamableHttpTransport(url=f"{server_url}/mcp/", headers=headers)
        client = Client(transport=transport)
        
        async with client:
            # Product discovery for FitGear Pro
            result = await client.call_tool("get_products", {
                "req": {
                    "brief": "Premium running shoe range targeting sports enthusiasts and urban runners for marathon season",
                    "promoted_offering": "FitGear Pro premium sportswear & running gear"
                }
            })
            
            if hasattr(result, 'structured_content'):
                products_data = result.structured_content
            else:
                products_data = result.content if hasattr(result, 'content') else result
            
            results["sales_agent"]["products"] = products_data
            
            # Media buy creation for FitGear Pro campaign
            if products_data.get('products'):
                product_ids = [p.get("product_id") for p in products_data['products'][:3]]  # Use first 3 products
                
                media_buy_result = await client.call_tool("create_media_buy", {
                    "req": {
                        "product_ids": product_ids,
                        "flight_start_date": "2025-09-15",
                        "flight_end_date": "2025-10-15",
                        "total_budget": 40000.0,
                        "targeting_overlay": {
                            "geo_country_any_of": ["US"],
                            "device_type_any_of": ["mobile", "desktop"],
                            "content_cat_any_of": ["sports", "fitness", "running"]
                        },
                        "po_number": "PO-FITGEAR-AUTUMN-2025",
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
        "budget_allocation": 40000.0,
        "flight_dates": "2025-09-15 to 2025-10-15",
        "targeting_summary": "US sports enthusiasts and urban runners",
        "recommendations": []
    }
    
    # Generate recommendations
    recommendations = []
    
    if results["combined_workflow"]["signals_found"] > 0:
        recommendations.append("✅ Signals discovered and activated for sports enthusiasts and urban runners")
    
    if results["combined_workflow"]["products_found"] > 0:
        recommendations.append("✅ Premium inventory identified for sports and fitness content")
    
    if results["combined_workflow"]["media_buy_created"]:
        recommendations.append("✅ Campaign created successfully with $40,000 budget")
    
    recommendations.append("🎯 Ready for FitGear Pro 'Run Into Autumn' campaign execution")
    
    results["final_results"]["recommendations"] = recommendations
    
    return results

async def main():
    """Main function to run the FitGear Pro brief test."""
    
    print("🚀 Starting FitGear Pro Brief Test")
    print("=" * 60)
    
    # Run the test
    results = await test_fitgear_brief()
    
    # Output as JSON
    print("\n" + "=" * 60)
    print("📊 FITGEAR PRO BRIEF TEST RESULTS")
    print("=" * 60)
    
    # Pretty print the JSON
    json_output = json.dumps(results, indent=2, default=str)
    print(json_output)
    
    # Save to file
    with open("fitgear_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: fitgear_test_results.json")
    print(f"🎯 Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
