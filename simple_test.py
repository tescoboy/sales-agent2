#!/usr/bin/env python3
"""
Simple test script to demonstrate the Signals Agent working with the Sales Agent.
"""

import asyncio
import json
import httpx
from datetime import datetime

async def test_signals_agent_basic():
    """Test basic signals agent functionality."""
    
    print("🔍 Testing Signals Agent Basic Functionality...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Health check
        print("\n1. Health check...")
        try:
            health_response = await client.get("http://127.0.0.1:8000/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Signals agent is healthy: {health_data.get('status')}")
                print(f"📊 Protocols: {', '.join(health_data.get('protocols', []))}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                return
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        # Test 2: Agent card
        print("\n2. Agent card...")
        try:
            agent_card_response = await client.get("http://127.0.0.1:8000/agent-card")
            if agent_card_response.status_code == 200:
                agent_card = agent_card_response.json()
                print(f"✅ Agent card retrieved")
                print(f"🤖 Agent: {agent_card.get('name', 'Unknown')}")
                print(f"📝 Description: {agent_card.get('description', 'No description')[:80]}...")
                print(f"🛠️ Skills: {len(agent_card.get('skills', []))} available")
            else:
                print(f"❌ Agent card failed: {agent_card_response.status_code}")
        except Exception as e:
            print(f"❌ Agent card error: {e}")
        
        # Test 3: Signal discovery
        print("\n3. Signal discovery...")
        try:
            discovery_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_signals",
                    "arguments": {
                        "signal_spec": "luxury automotive",
                        "deliver_to": {
                            "platforms": "all",
                            "countries": ["US"]
                        },
                        "max_results": 3
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
                result = discovery_data.get('result', {})
                
                print(f"✅ Signal discovery successful")
                print(f"📊 Message: {result.get('message', 'No message')[:100]}...")
                
                signals = result.get('signals', [])
                print(f"📊 Found {len(signals)} signals")
                
                for i, signal in enumerate(signals[:2]):
                    print(f"  {i+1}. {signal.get('name', 'Unknown')}")
                    print(f"     Description: {signal.get('description', 'No description')[:60]}...")
                    print(f"     Coverage: {signal.get('coverage_percentage', 0)}% | CPM: ${signal.get('pricing', {}).get('cpm', 0)}")
                
                return signals
            else:
                print(f"❌ Signal discovery failed: {discovery_response.status_code}")
                print(f"Response: {discovery_response.text[:200]}...")
        except Exception as e:
            print(f"❌ Signal discovery error: {e}")
            return []

async def test_sales_agent_basic():
    """Test basic sales agent functionality."""
    
    print("\n🔗 Testing Sales Agent Basic Functionality...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Product discovery
        print("\n1. Product discovery...")
        try:
            products_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_products",
                    "arguments": {
                        "req": {
                            "brief": "Premium video inventory for luxury automotive audiences",
                            "promoted_offering": "Luxury automotive brand campaign"
                        }
                    }
                },
                "id": 2
            }
            
            products_response = await client.post(
                "http://127.0.0.1:8101/mcp/",
                json=products_request,
                headers={
                    "Content-Type": "application/json",
                    "x-adcp-auth": "purina_token",
                    "x-adcp-tenant": "default"
                }
            )
            
            if products_response.status_code == 200:
                products_data = products_response.json()
                result = products_data.get('result', {})
                
                print(f"✅ Product discovery successful")
                
                products = result.get('products', [])
                print(f"📦 Found {len(products)} products")
                
                for i, product in enumerate(products[:3]):
                    print(f"  {i+1}. {product.get('name', 'Unknown')} - {product.get('delivery_type', 'Unknown type')}")
                    if product.get('price_guidance'):
                        price_info = product['price_guidance']
                        print(f"     Pricing: ${price_info.get('p50', 'N/A')} CPM")
                
                return products
            else:
                print(f"❌ Product discovery failed: {products_response.status_code}")
                print(f"Response: {products_response.text[:200]}...")
        except Exception as e:
            print(f"❌ Product discovery error: {e}")
            return []

async def test_combined_workflow():
    """Test a simple combined workflow."""
    
    print("\n🔄 Testing Combined Workflow...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n1. Step 1: Discover signals for luxury automotive campaign...")
        
        # Discover signals
        signals_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_signals",
                "arguments": {
                    "signal_spec": "luxury automotive high income",
                    "deliver_to": {
                        "platforms": "all",
                        "countries": ["US"]
                    },
                    "max_results": 2
                }
            },
            "id": 3
        }
        
        try:
            signals_response = await client.post(
                "http://127.0.0.1:8000/mcp/",
                json=signals_request,
                headers={"Content-Type": "application/json"}
            )
            
            if signals_response.status_code == 200:
                signals_data = signals_response.json()
                signals_result = signals_data.get('result', {})
                signals_list = signals_result.get('signals', [])
                
                print(f"✅ Found {len(signals_list)} relevant signals")
                
                if signals_list:
                    target_signal = signals_list[0]
                    print(f"🎯 Target signal: {target_signal.get('name')}")
                    print(f"📊 Coverage: {target_signal.get('coverage_percentage', 0)}%")
                    print(f"💰 CPM: ${target_signal.get('pricing', {}).get('cpm', 0)}")
                    
                    print(f"\n2. Step 2: Find products that can leverage this signal...")
                    
                    # Find products
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
                        "id": 4
                    }
                    
                    products_response = await client.post(
                        "http://127.0.0.1:8101/mcp/",
                        json=products_request,
                        headers={
                            "Content-Type": "application/json",
                            "x-adcp-auth": "purina_token",
                            "x-adcp-tenant": "default"
                        }
                    )
                    
                    if products_response.status_code == 200:
                        products_data = products_response.json()
                        products_result = products_data.get('result', {})
                        products_list = products_result.get('products', [])
                        
                        print(f"✅ Found {len(products_list)} products that can leverage the signal")
                        
                        # Display top products
                        for i, product in enumerate(products_list[:3]):
                            print(f"  {i+1}. {product.get('name', 'Unknown')} - {product.get('delivery_type', 'Unknown type')}")
                            if product.get('price_guidance'):
                                price_info = product['price_guidance']
                                print(f"     Pricing: ${price_info.get('p50', 'N/A')} CPM")
                        
                        print(f"\n🎉 Combined workflow completed successfully!")
                        print(f"   - Signal: {target_signal.get('name')} ({target_signal.get('coverage_percentage', 0)}% coverage)")
                        print(f"   - Products: {len(products_list)} available")
                        print(f"   - Ready for campaign execution!")
                    else:
                        print(f"❌ Product discovery failed: {products_response.status_code}")
                else:
                    print("❌ No signals found")
            else:
                print(f"❌ Signal discovery failed: {signals_response.status_code}")
        except Exception as e:
            print(f"❌ Combined workflow error: {e}")

async def main():
    """Main test function."""
    print("🚀 Starting Simple Integration Test")
    print("=" * 50)
    
    # Test signals agent
    signals = await test_signals_agent_basic()
    
    # Test sales agent
    products = await test_sales_agent_basic()
    
    # Test combined workflow
    await test_combined_workflow()
    
    print("\n" + "=" * 50)
    print("✅ Simple integration test completed!")
    print(f"\n📊 Summary:")
    print(f"   - Signals Agent: {'✅ Running' if signals else '❌ Issues'}")
    print(f"   - Sales Agent: {'✅ Running' if products else '❌ Issues'}")
    print(f"   - Combined Workflow: ✅ Tested")

if __name__ == "__main__":
    asyncio.run(main())
