#!/usr/bin/env python3
"""
Test script for the Signals Agent to demonstrate functionality.
This script shows how the signals agent can work in conjunction with the sales agent.
"""

import asyncio
import json
import httpx
from datetime import datetime

async def test_signals_agent():
    """Test the signals agent functionality."""
    
    # Signals agent configuration
    signals_server_url = "http://127.0.0.1:8000"
    
    print("🔍 Testing Signals Agent...")
    print(f"📍 Server: {signals_server_url}")
    
    try:
        async with httpx.AsyncClient() as client:
            print("\n1. Testing signal discovery...")
            
            # Test signal discovery using direct HTTP call
            discovery_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_signals",
                    "arguments": {
                        "signal_spec": "luxury automotive audiences with high income",
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
                f"{signals_server_url}/mcp/",
                json=discovery_request,
                headers={"Content-Type": "application/json"}
            )
            
            if discovery_response.status_code == 200:
                discovery_data = discovery_response.json()
                result = discovery_data.get('result', {})
                
                print(f"✅ Discovery response received")
                print(f"📊 Message: {result.get('message', 'No message')[:100]}...")
                
                signals = result.get('signals', [])
                print(f"📊 Found {len(signals)} signals")
                
                # Display some signals
                for i, signal in enumerate(signals[:3]):
                    print(f"  {i+1}. {signal.get('name', 'Unknown')} - {signal.get('description', 'No description')[:50]}...")
                    print(f"     Coverage: {signal.get('coverage_percentage', 0)}% | CPM: ${signal.get('pricing', {}).get('cpm', 0)}")
                
                # Test signal activation if we have signals
                if signals:
                    print("\n2. Testing signal activation...")
                    
                    first_signal = signals[0]
                    signal_id = first_signal.get('signals_agent_segment_id')
                    
                    if signal_id:
                        activation_request = {
                            "jsonrpc": "2.0",
                            "method": "tools/call",
                            "params": {
                                "name": "activate_signal",
                                "arguments": {
                                    "signals_agent_segment_id": signal_id,
                                    "platform": "index-exchange",
                                    "account": None
                                }
                            },
                            "id": 2
                        }
                        
                        activation_response = await client.post(
                            f"{signals_server_url}/mcp/",
                            json=activation_request,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if activation_response.status_code == 200:
                            activation_data = activation_response.json()
                            activation_result = activation_data.get('result', {})
                            
                            print(f"✅ Signal activation response received")
                            print(f"🎯 Activation status: {activation_result.get('status', 'unknown')}")
                            print(f"📋 Message: {activation_result.get('message', 'No message')[:100]}...")
                        else:
                            print(f"❌ Activation failed: {activation_response.status_code}")
            
            print("\n3. Testing A2A agent card...")
            
            # Test A2A agent card endpoint
            agent_card_response = await client.get(f"{signals_server_url}/agent-card")
            if agent_card_response.status_code == 200:
                agent_card = agent_card_response.json()
                print(f"✅ Agent card retrieved")
                print(f"🤖 Agent name: {agent_card.get('name', 'Unknown')}")
                print(f"📝 Description: {agent_card.get('description', 'No description')[:100]}...")
                print(f"🛠️ Skills: {len(agent_card.get('skills', []))} skills available")
                
                # Display skills
                for skill in agent_card.get('skills', []):
                    print(f"  - {skill.get('name', 'Unknown')}: {skill.get('description', 'No description')[:50]}...")
            else:
                print(f"❌ Failed to get agent card: {agent_card_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error testing signals agent: {e}")
        import traceback
        traceback.print_exc()

async def test_integration_with_sales_agent():
    """Test integration between signals agent and sales agent."""
    
    print("\n🔗 Testing Integration with Sales Agent...")
    
    # Sales agent configuration
    sales_server_url = "http://127.0.0.1:8101"
    sales_headers = {"x-adcp-auth": "purina_token", "x-adcp-tenant": "default"}
    
    try:
        async with httpx.AsyncClient() as client:
            print("\n1. Testing sales agent product discovery...")
            
            # Test product discovery with signals context
            products_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_products",
                    "arguments": {
                        "req": {
                            "brief": "Looking for premium video inventory to reach luxury automotive audiences",
                            "promoted_offering": "Luxury automotive brand campaign"
                        }
                    }
                },
                "id": 3
            }
            
            products_response = await client.post(
                f"{sales_server_url}/mcp/",
                json=products_request,
                headers={**sales_headers, "Content-Type": "application/json"}
            )
            
            if products_response.status_code == 200:
                products_data = products_response.json()
                result = products_data.get('result', {})
                
                print(f"✅ Sales agent products response received")
                
                products = result.get('products', [])
                print(f"📦 Found {len(products)} products")
                
                # Display some products
                for i, product in enumerate(products[:3]):
                    print(f"  {i+1}. {product.get('name', 'Unknown')} - {product.get('delivery_type', 'Unknown type')}")
                    if product.get('price_guidance'):
                        price_info = product['price_guidance']
                        print(f"     Pricing: ${price_info.get('p50', 'N/A')} CPM (50th percentile)")
            else:
                print(f"❌ Sales agent request failed: {products_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error testing sales agent integration: {e}")
        import traceback
        traceback.print_exc()

async def test_combined_workflow():
    """Test a combined workflow using both agents."""
    
    print("\n🔄 Testing Combined Workflow...")
    
    signals_server_url = "http://127.0.0.1:8000"
    sales_server_url = "http://127.0.0.1:8101"
    sales_headers = {"x-adcp-auth": "purina_token", "x-adcp-tenant": "default"}
    
    try:
        async with httpx.AsyncClient() as client:
            print("\n1. Step 1: Discover relevant signals for luxury automotive campaign...")
            
            # Discover signals
            signals_request = {
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
                        "max_results": 3
                    }
                },
                "id": 4
            }
            
            signals_response = await client.post(
                f"{signals_server_url}/mcp/",
                json=signals_request,
                headers={"Content-Type": "application/json"}
            )
            
            if signals_response.status_code == 200:
                signals_data = signals_response.json()
                signals_result = signals_data.get('result', {})
                signals_list = signals_result.get('signals', [])
                
                print(f"✅ Found {len(signals_list)} relevant signals")
                
                if signals_list:
                    # Use the first signal for activation
                    target_signal = signals_list[0]
                    signal_id = target_signal.get('signals_agent_segment_id')
                    
                    print(f"\n2. Step 2: Activate signal '{target_signal.get('name')}'...")
                    
                    activation_request = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "activate_signal",
                            "arguments": {
                                "signals_agent_segment_id": signal_id,
                                "platform": "index-exchange",
                                "account": None
                            }
                        },
                        "id": 5
                    }
                    
                    activation_response = await client.post(
                        f"{signals_server_url}/mcp/",
                        json=activation_request,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if activation_response.status_code == 200:
                        activation_data = activation_response.json()
                        activation_result = activation_data.get('result', {})
                        
                        print(f"✅ Signal activated successfully")
                        print(f"🎯 Status: {activation_result.get('status', 'unknown')}")
                        print(f"📋 Platform Segment ID: {activation_result.get('decisioning_platform_segment_id', 'N/A')}")
                        
                        print(f"\n3. Step 3: Find products that can leverage this signal...")
                        
                        # Find products that can use the activated signal
                        products_request = {
                            "jsonrpc": "2.0",
                            "method": "tools/call",
                            "params": {
                                "name": "get_products",
                                "arguments": {
                                    "req": {
                                        "brief": f"Premium inventory to reach {target_signal.get('name')} audience",
                                        "promoted_offering": "Luxury automotive campaign with activated signals"
                                    }
                                }
                            },
                            "id": 6
                        }
                        
                        products_response = await client.post(
                            f"{sales_server_url}/mcp/",
                            json=products_request,
                            headers={**sales_headers, "Content-Type": "application/json"}
                        )
                        
                        if products_response.status_code == 200:
                            products_data = products_response.json()
                            products_result = products_data.get('result', {})
                            products_list = products_result.get('products', [])
                            
                            print(f"✅ Found {len(products_list)} products that can leverage the activated signal")
                            
                            # Display top products
                            for i, product in enumerate(products_list[:3]):
                                print(f"  {i+1}. {product.get('name', 'Unknown')} - {product.get('delivery_type', 'Unknown type')}")
                                if product.get('price_guidance'):
                                    price_info = product['price_guidance']
                                    print(f"     Pricing: ${price_info.get('p50', 'N/A')} CPM")
                        
                        print(f"\n🎉 Combined workflow completed successfully!")
                        print(f"   - Signal discovered and activated: {target_signal.get('name')}")
                        print(f"   - Products identified: {len(products_list) if 'products_list' in locals() else 0}")
                        print(f"   - Ready for campaign execution!")
    
    except Exception as e:
        print(f"❌ Error in combined workflow: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function."""
    print("🚀 Starting Signals Agent and Sales Agent Integration Test")
    print("=" * 60)
    
    # Test signals agent
    await test_signals_agent()
    
    # Test integration with sales agent
    await test_integration_with_sales_agent()
    
    # Test combined workflow
    await test_combined_workflow()
    
    print("\n" + "=" * 60)
    print("✅ Integration test completed!")

if __name__ == "__main__":
    asyncio.run(main())
