# Vinted Price Scout

An AI-powered price lookup tool for Vinted resellers. Get smart pricing recommendations for items you find at charity shops and flea markets.

## Features

- 📸 **Image analysis** - Upload a photo for accurate condition assessment
- 🎯 **Smart pricing** - Get conservative, recommended, and optimistic price ranges
- 📊 **Demand insights** - See estimated sell time and demand level
- 💡 **Listing tips** - Get actionable advice to sell faster
- 📈 **Profit margins** - Calculate expected margins vs charity shop cost

## Setup

### 1. Get an API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Create an API key (free tier available, then pay-per-use)
4. Copy your API key

### 2. Deploy to Streamlit Cloud

1. Push this repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/vinted-price-scout.git
   git push -u origin main
   ```

2. Go to [streamlit.io/cloud](https://share.streamlit.io/)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository and `app.py`
6. Click "Advanced settings"
7. Under "Secrets", paste your API key:
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
8. Click "Deploy"

### 3. Share with Your Girlfriend

Once deployed, you'll get a public URL like `https://share.streamlit.io/YOUR_USERNAME/vinted-price-scout/main/app.py`. Share this link!

## Local Development

To run locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then set your API key in `.streamlit/secrets.toml`:
```
ANTHROPIC_API_KEY = "sk-ant-..."
```

## Pricing

- Streamlit Cloud: Free
- Claude API: Free tier, then ~$0.01-0.02 per lookup depending on image size

## Notes

- The app stores search history in your browser session (cleared when you refresh)
- Images improve accuracy significantly
- Works best with items sold on Vinted Spain/Europe market
