#!/bin/bash
echo "🌿 ArogyaMitra Setup Script"
echo "================================"

echo ""
echo "📦 Setting up Backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "⚙️  Creating .env file..."
cp .env.example .env
echo "⚠️  IMPORTANT: Edit backend/.env and add your GROQ_API_KEY"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd backend && source venv/bin/activate && python main.py"
echo ""
echo "To start the frontend:"
echo "  Open frontend/index.html in your browser"
echo "  OR: cd frontend && npx serve ."
