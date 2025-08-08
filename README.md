# 🚀 AdCP Agent Platform - Campaign Generator

A modern web application for generating comprehensive campaign strategies using AI-powered signals and sales agents.

## ✨ Features

- **Modern UI/UX**: Clean, responsive design with Bootstrap 5 and Font Awesome icons
- **Campaign Generation**: Input campaign briefs and get comprehensive strategies
- **Real-time Integration**: Connects with both Sales Agent and Signals Agent
- **Multi-tab Results**: View results in Overview, Signals, Products, Strategy, and JSON tabs
- **Export Capabilities**: Copy results to clipboard or download as JSON
- **Mobile Responsive**: Works perfectly on mobile devices

## 🏗️ Architecture

```
Frontend (HTML/CSS/JS) → Flask Backend → Sales Agent + Signals Agent
```

### Components

1. **Frontend**: Modern web interface built with Bootstrap 5
2. **Backend**: Flask API server that orchestrates agent calls
3. **Agents**: 
   - **Sales Agent**: Handles product discovery and media buy creation
   - **Signals Agent**: Manages audience signals and targeting

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for development)
- Both Sales Agent and Signals Agent running

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sales-agent2
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the agents** (in separate terminals)
   ```bash
   # Terminal 1 - Sales Agent
   cd salesagent
   uv run python run_server.py
   
   # Terminal 2 - Signals Agent
   cd signals-agent
   uv run python unified_server.py
   ```

4. **Start the Flask backend**
   ```bash
   python app.py
   ```

5. **Open the application**
   - Navigate to `http://localhost:5000` in your browser
   - Or open `index.html` directly for frontend-only testing

## 📋 Usage

### Creating a Campaign

1. **Fill in campaign details**:
   - Advertiser Name (e.g., "FreshBake Co.")
   - Campaign Name (e.g., "Breaking Bread - Politics & News")
   - Campaign Brief (detailed description of objectives, target audience, etc.)
   - Budget (minimum $1,000)
   - Start and End Dates

2. **Generate Strategy**:
   - Click "Generate Campaign Strategy"
   - Wait for the system to process your request
   - View results in the interactive tabs

3. **Review Results**:
   - **Overview**: Campaign summary and key metrics
   - **Signals**: Discovered audience signals and targeting options
   - **Products**: Available inventory and pricing
   - **Strategy**: Campaign strategy and recommendations
   - **JSON**: Raw data for technical analysis

### Example Campaign Brief

```
Advertiser: FreshBake Co.
Campaign: Breaking Bread - Politics & News
Brief: Sell premium bread to people who like politics and news. 
Target audience includes political news readers, current events enthusiasts, 
and people who consume political content regularly. Budget: $25,000 for 
a 30-day campaign focusing on US audiences.
```

## 🎨 UI Components

### Navigation
- Clean navbar with branding and navigation links
- Responsive mobile menu

### Form Section
- Multi-step form with validation
- Real-time feedback and error handling
- Modern input styling with icons

### Results Section
- Tabbed interface for organized results
- Interactive cards with hover effects
- Copy and download functionality

### Responsive Design
- Mobile-first approach
- Optimized for all screen sizes
- Touch-friendly interface

## 🔧 Configuration

### Backend Configuration

Edit `app.py` to configure:
- Sales Agent URL (default: `http://127.0.0.1:8101`)
- Signals Agent URL (default: `http://127.0.0.1:8000`)
- API tokens and authentication

### Frontend Configuration

Edit `js/app.js` to configure:
- API base URL (default: `http://localhost:5000/api`)
- Request timeouts and retry logic

## 📊 API Endpoints

### Health Check
```
GET /api/health
```
Returns the health status of all services.

### Generate Campaign
```
POST /api/generate-campaign
```
Generates a campaign strategy using both agents.

**Request Body:**
```json
{
  "advertiserName": "FreshBake Co.",
  "campaignName": "Breaking Bread - Politics & News",
  "campaignBrief": "Sell premium bread to people who like politics and news...",
  "budget": 25000,
  "startDate": "2025-01-15",
  "endDate": "2025-02-15"
}
```

**Response:**
```json
{
  "test_metadata": {...},
  "signals_agent": {...},
  "sales_agent": {...},
  "combined_workflow": {...},
  "final_results": {...}
}
```

## 🎯 Key Features

### Campaign Generation
- **Intelligent Brief Processing**: Analyzes campaign briefs for targeting opportunities
- **Multi-Agent Integration**: Combines signals and sales agent capabilities
- **Real-time Results**: Instant feedback and progress updates

### Data Visualization
- **Interactive Tabs**: Organized results presentation
- **Rich Cards**: Detailed information with visual hierarchy
- **Export Options**: Multiple output formats

### User Experience
- **Loading States**: Clear feedback during processing
- **Error Handling**: Graceful error messages and recovery
- **Mobile Optimization**: Touch-friendly interface

## 🔍 Troubleshooting

### Common Issues

1. **Agents Not Responding**
   - Ensure both agents are running on correct ports
   - Check agent health endpoints
   - Verify network connectivity

2. **CORS Issues**
   - Ensure Flask-CORS is properly configured
   - Check browser console for CORS errors

3. **API Errors**
   - Check backend logs for detailed error messages
   - Verify API endpoints are accessible
   - Ensure proper JSON formatting

### Debug Mode

Enable debug mode in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🚀 Deployment

### Production Setup

1. **Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SALES_AGENT_URL=http://your-sales-agent-url
   export SIGNALS_AGENT_URL=http://your-signals-agent-url
   ```

2. **WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Reverse Proxy**
   - Configure Nginx or Apache
   - Set up SSL certificates
   - Configure static file serving

## 📈 Performance

### Optimization Tips

1. **Frontend**
   - Minify CSS and JavaScript
   - Optimize images and assets
   - Use CDN for external libraries

2. **Backend**
   - Implement caching for agent responses
   - Use connection pooling
   - Optimize database queries

3. **Agents**
   - Ensure agents are properly configured
   - Monitor resource usage
   - Implement rate limiting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review agent documentation
- Open an issue on GitHub

---

**🎯 Ready to generate your next campaign strategy?**
