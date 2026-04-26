#!/bin/bash
# LLM Version Manager Demo
# This script demonstrates the tool's capabilities

echo "🤖 LLM Version Manager - Demo"
echo "================================"
echo ""

echo "1️⃣  Listing configured projects..."
echo ""
python cli.py list-projects
echo ""
read -p "Press Enter to continue..."
echo ""

echo "2️⃣  Scanning Medcore API for model references..."
echo ""
python cli.py scan --project medcore-api
echo ""
read -p "Press Enter to continue..."
echo ""

echo "3️⃣  Generating comprehensive report..."
echo ""
python cli.py report
echo ""

echo "✅ Demo complete!"
echo ""
echo "To use this tool:"
echo "  1. Set API keys: export OPENAI_API_KEY=... ANTHROPIC_API_KEY=..."
echo "  2. Run: python cli.py check --project medcore-api"
echo "  3. Fix any issues found"
echo "  4. Add to your CI/CD pipeline"
echo ""
