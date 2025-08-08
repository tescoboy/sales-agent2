#!/bin/bash

# Script to push FitGear Pro test results to your GitHub repository

echo "🚀 Pushing FitGear Pro test results to your GitHub repository..."

# Check if the remote exists
if git remote get-url mygithub > /dev/null 2>&1; then
    echo "✅ Remote 'mygithub' found"
else
    echo "❌ Remote 'mygithub' not found. Creating it..."
    git remote add mygithub https://github.com/harvingupta/signals-agent.git
fi

# Check if we have commits to push
if git log --oneline -1 | grep -q "Add FitGear Pro brief test"; then
    echo "✅ Found FitGear Pro test commit"
else
    echo "❌ FitGear Pro test commit not found. Please commit your changes first."
    exit 1
fi

# Try to push to GitHub
echo "📤 Pushing to GitHub..."
if git push mygithub main; then
    echo "🎉 Successfully pushed to GitHub!"
    echo "📊 Your FitGear Pro test results are now available at:"
    echo "   https://github.com/harvingupta/signals-agent"
else
    echo "❌ Failed to push to GitHub."
    echo "💡 Make sure you:"
    echo "   1. Created the repository at https://github.com/harvingupta/signals-agent"
    echo "   2. Have the correct permissions"
    echo "   3. Are authenticated with GitHub"
fi
