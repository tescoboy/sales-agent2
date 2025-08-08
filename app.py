#!/usr/bin/env python3
"""
AdCP Agent Platform - Backend API
Flask server that integrates with sales and signals agents
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import json
import httpx
from datetime import datetime
import os
import sys

# Add the salesagent and signals-agent directories to the path
sys.path.append('salesagent')
sys.path.append('signals-agent')

app = Flask(__name__)
CORS(app)

# Configuration
SALES_AGENT_URL = "http://127.0.0.1:8101"
SIGNALS_AGENT_URL = "http://127.0.0.1:8000"
SALES_AGENT_TOKEN = "purina_token"
SALES_AGENT_TENANT = "default"

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    return send_from_directory('js', filename)

@app.route('/styles/<path:filename>')
def serve_styles(filename):
    """Serve CSS files"""
    return send_from_directory('styles', filename)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "sales_agent": check_sales_agent_health(),
            "signals_agent": check_signals_agent_health()
        }
    })

@app.route('/api/generate-campaign', methods=['POST'])
def generate_campaign():
    """Generate campaign strategy using both agents"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['advertiserName', 'campaignName', 'campaignBrief', 'budget', 'startDate', 'endDate']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Generate campaign strategy
        results = asyncio.run(generate_campaign_strategy(data))
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error generating campaign: {e}")
        return jsonify({"error": str(e)}), 500

async def generate_campaign_strategy(form_data):
    """Generate campaign strategy using both agents"""
    print(f"Generating campaign strategy for: {form_data}")
    
    # Call both agents
    signals_results = await call_signals_agent(form_data)
    sales_results = await call_sales_agent(form_data)
    
    # Combine results
    combined_results = {
        "test_metadata": {
            "advertiser": form_data['advertiserName'],
            "campaign_name": form_data['campaignName'],
            "test_timestamp": datetime.now().isoformat(),
            "brief_summary": form_data['campaignBrief']
        },
        "signals_agent": signals_results,
        "sales_agent": sales_results,
        "combined_workflow": {
            "signals_found": len(signals_results.get('discovery', {}).get('signals', [])),
            "signals_activated": len(signals_results.get('activations', [])),
            "products_found": len(sales_results.get('products', {}).get('products', [])),
            "media_buy_created": bool(sales_results.get('media_buy')),
            "workflow_status": "complete"
        },
        "final_results": {
            "campaign_ready": bool(sales_results.get('media_buy')),
            "signals_available": len(signals_results.get('discovery', {}).get('signals', [])),
            "products_available": len(sales_results.get('products', {}).get('products', [])),
            "budget_allocation": float(form_data['budget']),
            "flight_dates": f"{form_data['startDate']} to {form_data['endDate']}",
            "targeting_summary": extract_targeting_summary(form_data['campaignBrief']),
            "recommendations": generate_recommendations(signals_results, sales_results)
        }
    }
    
    return combined_results

async def call_signals_agent(form_data):
    """Call the signals agent"""
    print("Calling signals agent...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Health check
            health_response = await client.get(f"{SIGNALS_AGENT_URL}/health")
            if health_response.status_code != 200:
                return {"error": "Signals agent not available"}
            
            # Signal discovery
            discovery_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "get_signals",
                    "arguments": {
                        "signal_spec": form_data['campaignBrief'][:200],  # Limit length
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
                f"{SIGNALS_AGENT_URL}/mcp/",
                json=discovery_request,
                headers={"Content-Type": "application/json"}
            )
            
            if discovery_response.status_code == 200:
                discovery_data = discovery_response.json()
                signals_results = discovery_data.get('result', {})
                
                # Activate signals
                activations = []
                signals = signals_results.get('signals', [])
                
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
                        f"{SIGNALS_AGENT_URL}/mcp/",
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
                
                return {
                    "health": {"status": "healthy"},
                    "discovery": signals_results,
                    "activations": activations
                }
            else:
                return {"error": f"Signals agent error: {discovery_response.status_code}"}
                
    except Exception as e:
        print(f"Error calling signals agent: {e}")
        return {"error": str(e)}

async def call_sales_agent(form_data):
    """Call the sales agent"""
    print("Calling sales agent...")
    
    try:
        # For now, return mock data since we need to set up the FastMCP client properly
        # In a real implementation, you would use the FastMCP client here
        
        return {
            "products": {
                "products": [
                    {
                        "product_id": "homepage_takeover",
                        "name": "Homepage Takeover",
                        "description": "Premium guaranteed placement on homepage with high viewability.",
                        "delivery_type": "guaranteed",
                        "cpm": 25.0,
                        "formats": [
                            {
                                "format_id": "display_970x250",
                                "name": "Display 970X250",
                                "type": "display"
                            }
                        ]
                    },
                    {
                        "product_id": "mobile_interstitial",
                        "name": "Mobile Interstitial",
                        "description": "Full-screen mobile interstitial ads with frequency capping.",
                        "delivery_type": "guaranteed",
                        "cpm": 15.0,
                        "formats": [
                            {
                                "format_id": "display_320x480",
                                "name": "Display 320X480",
                                "type": "display"
                            }
                        ]
                    },
                    {
                        "product_id": "contextual_display",
                        "name": "Contextual Display",
                        "description": "Display advertising with contextual targeting based on page content.",
                        "delivery_type": "non_guaranteed",
                        "price_guidance": {"p50": 12.0},
                        "formats": [
                            {
                                "format_id": "display_300x250",
                                "name": "Display 300X250",
                                "type": "display"
                            }
                        ]
                    }
                ]
            },
            "media_buy": {
                "media_buy_id": f"mb_{int(datetime.now().timestamp())}",
                "status": "created",
                "message": "Media buy created successfully",
                "product_ids": ["homepage_takeover", "mobile_interstitial", "contextual_display"],
                "total_budget": float(form_data['budget']),
                "flight_start_date": form_data['startDate'],
                "flight_end_date": form_data['endDate']
            }
        }
        
    except Exception as e:
        print(f"Error calling sales agent: {e}")
        return {"error": str(e)}

def extract_targeting_summary(brief):
    """Extract targeting summary from brief"""
    brief_lower = brief.lower()
    targeting = []
    
    if 'politics' in brief_lower or 'news' in brief_lower:
        targeting.append('Politics and news enthusiasts')
    if 'sports' in brief_lower or 'fitness' in brief_lower:
        targeting.append('Sports and fitness enthusiasts')
    if 'luxury' in brief_lower or 'premium' in brief_lower:
        targeting.append('Luxury and premium audiences')
    if 'mobile' in brief_lower or 'app' in brief_lower:
        targeting.append('Mobile-first users')
    
    return ', '.join(targeting) if targeting else 'General audience'

def generate_recommendations(signals_results, sales_results):
    """Generate recommendations based on results"""
    recommendations = []
    
    if signals_results.get('discovery', {}).get('signals'):
        recommendations.append("✅ Signals discovered and activated for target audience")
    
    if sales_results.get('products', {}).get('products'):
        recommendations.append("✅ Premium inventory identified for campaign objectives")
    
    if sales_results.get('media_buy'):
        recommendations.append("✅ Campaign created successfully with allocated budget")
    
    recommendations.append("🎯 Ready for campaign execution")
    
    return recommendations

def check_sales_agent_health():
    """Check sales agent health"""
    try:
        response = httpx.get(f"{SALES_AGENT_URL}/health", timeout=5)
        return {"status": "healthy" if response.status_code == 200 else "unhealthy"}
    except:
        return {"status": "unavailable"}

def check_signals_agent_health():
    """Check signals agent health"""
    try:
        response = httpx.get(f"{SIGNALS_AGENT_URL}/health", timeout=5)
        return {"status": "healthy" if response.status_code == 200 else "unhealthy"}
    except:
        return {"status": "unavailable"}

if __name__ == '__main__':
    print("Starting AdCP Agent Platform...")
    print(f"Sales Agent URL: {SALES_AGENT_URL}")
    print(f"Signals Agent URL: {SIGNALS_AGENT_URL}")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
