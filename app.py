import streamlit as st
import anthropic
import base64
import json
from datetime import datetime

st.set_page_config(page_title="Vinted Price Scout", layout="wide")

# Custom CSS
st.markdown("""
<style>
    :root {
        --ink:     #1a1a1a;
        --paper:   #faf8f4;
        --cream:   #f0ece4;
        --accent:  #09b1a4;
        --accent2: #e8533f;
        --gold:    #c8922a;
        --muted:   #888;
        --border:  #ddd8ce;
        --card:    #ffffff;
    }

    body {
        background-color: var(--paper);
        color: var(--ink);
    }

    .price-box {
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }

    .price-box.highlight {
        background-color: #e8faf8;
        border-color: var(--accent);
    }

    .price-amount {
        font-size: 28px;
        font-weight: bold;
        color: #1a1a1a;
    }

    .price-box.highlight .price-amount {
        color: var(--accent);
    }

    .margin-good { color: #1a6b3c; }
    .margin-ok { color: var(--gold); }
    .margin-bad { color: var(--accent2); }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "Clothing"
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# Header
st.markdown("# Vinted **_Price Scout_**")
st.markdown("*RESALE LOOKUP TOOL*")

# Get API key from secrets or environment
api_key = st.secrets.get("ANTHROPIC_API_KEY") if hasattr(st, "secrets") and "ANTHROPIC_API_KEY" in st.secrets else None

if not api_key:
    st.error("⚠️ **API Key Required**: Please set `ANTHROPIC_API_KEY` in Streamlit Secrets")
    st.info("For deployment: Add your key in Streamlit Cloud → App settings → Secrets")
    st.stop()

# Search card
st.markdown("### Search")

col1, col2, col3, col4 = st.columns(4)
categories = {
    "👗 Clothing": "Clothing",
    "👟 Shoes": "Shoes",
    "👜 Bags": "Bags & Accessories",
    "💍 Jewellery": "Jewellery & Watches",
    "📱 Electronics": "Electronics",
    "🏺 Home & Decor": "Home & Decor",
    "📚 Books": "Books & Collectibles",
    "🏛️ Vintage": "Vintage & Antiques"
}

with col1:
    if st.button("👗 Clothing", use_container_width=True, key="cat_clothing"):
        st.session_state.selected_category = "Clothing"
with col2:
    if st.button("👟 Shoes", use_container_width=True, key="cat_shoes"):
        st.session_state.selected_category = "Shoes"
with col3:
    if st.button("👜 Bags", use_container_width=True, key="cat_bags"):
        st.session_state.selected_category = "Bags & Accessories"
with col4:
    if st.button("💍 Jewellery", use_container_width=True, key="cat_jewellery"):
        st.session_state.selected_category = "Jewellery & Watches"

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📱 Electronics", use_container_width=True, key="cat_electronics"):
        st.session_state.selected_category = "Electronics"
with col2:
    if st.button("🏺 Home & Decor", use_container_width=True, key="cat_home"):
        st.session_state.selected_category = "Home & Decor"
with col3:
    if st.button("📚 Books", use_container_width=True, key="cat_books"):
        st.session_state.selected_category = "Books & Collectibles"
with col4:
    if st.button("🏛️ Vintage", use_container_width=True, key="cat_vintage"):
        st.session_state.selected_category = "Vintage & Antiques"

st.markdown(f"**Selected:** {st.session_state.selected_category}")

# Item input
item_input = st.text_input(
    "Item description",
    placeholder="e.g. Levi's 501 jeans, Nike Air Max, Zara coat…"
)

# Image upload
uploaded_file = st.file_uploader(
    "Photo of item (optional — improves accuracy)",
    type=["jpg", "jpeg", "png", "gif", "webp"]
)

if uploaded_file:
    st.session_state.uploaded_image = uploaded_file
    st.image(uploaded_file, width=200)

# Lookup button
if st.button("🔍 Get Price Estimate", type="primary", use_container_width=True):
    if not item_input.strip():
        st.error("Please enter an item description")
    else:
        with st.spinner("Analysing item and condition…"):
            try:
                client = anthropic.Anthropic(api_key=api_key)

                # Prepare message content
                user_content = []

                # Add image if present
                if st.session_state.uploaded_image:
                    image_data = st.session_state.uploaded_image.read()
                    image_base64 = base64.standard_b64encode(image_data).decode("utf-8")
                    image_type = st.session_state.uploaded_image.type
                    user_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_type,
                            "data": image_base64
                        }
                    })

                # Add text prompt
                user_content.append({
                    "type": "text",
                    "text": f"""You are an expert second-hand resale pricing assistant specialising in Vinted (Spain/Europe market).

A reseller found this item at a charity shop or flea market in Madrid and wants to know what price to list it for on Vinted.

Item: "{item_input}"
Category: {st.session_state.selected_category}
{"An image of the item has been provided. Assess its condition carefully from the photo." if st.session_state.uploaded_image else "No image provided — estimate based on typical condition for charity shop finds."}

Respond ONLY with a JSON object — no preamble, no markdown, no backticks. Use this exact structure:
{{
  "item_name": "cleaned up item name",
  "brand_detected": "brand name or null",
  "condition": "New with tags | Like New | Good | Fair | Poor",
  "condition_score": 1-5,
  "condition_notes": "brief 1-2 sentence description of visible condition",
  "price_low": number in euros,
  "price_mid": number in euros,
  "price_high": number in euros,
  "price_reasoning": "2-3 sentences explaining the price range based on brand, category, condition, and current Vinted Spain demand",
  "sell_factors": [
    {{"icon": "✅", "text": "positive factor 1"}},
    {{"icon": "✅", "text": "positive factor 2"}},
    {{"icon": "⚠️", "text": "challenge or negative factor"}},
    {{"icon": "💡", "text": "tip to maximise sale price"}}
  ],
  "best_listing_tip": "One specific actionable tip for this exact item to sell faster on Vinted",
  "demand_level": "High | Medium | Low",
  "avg_days_to_sell": number
}}"""
                })

                # Call Claude
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": user_content}
                    ]
                )

                # Parse response
                raw_text = response.content[0].text
                clean_text = raw_text.replace("```json", "").replace("```", "").strip()
                result = json.loads(clean_text)

                # Display results
                st.markdown("---")
                st.markdown("### Price Estimate")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="price-box">
                        <div style="font-size: 12px; color: #888; text-transform: uppercase; margin-bottom: 10px;">Conservative</div>
                        <div class="price-amount">€{result['price_low']}</div>
                        <div style="font-size: 12px; color: #888; margin-top: 5px;">Quick sale</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="price-box highlight">
                        <div style="font-size: 12px; color: #888; text-transform: uppercase; margin-bottom: 10px;">Recommended</div>
                        <div class="price-amount">€{result['price_mid']}</div>
                        <div style="font-size: 12px; color: #888; margin-top: 5px;">Best value</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="price-box">
                        <div style="font-size: 12px; color: #888; text-transform: uppercase; margin-bottom: 10px;">Optimistic</div>
                        <div class="price-amount">€{result['price_high']}</div>
                        <div style="font-size: 12px; color: #888; margin-top: 5px;">If patient</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Item details
                st.markdown(f"**{result['item_name']}**")
                if result.get('brand_detected'):
                    st.markdown(f"_Brand:_ {result['brand_detected']}")

                badge_color = {
                    "New with tags": "#d4edda",
                    "Like New": "#cce5ff",
                    "Good": "#cce5ff",
                    "Fair": "#fff3cd",
                    "Poor": "#f8d7da"
                }
                st.markdown(f"Condition: **{result['condition']}**")

                # Analysis sections
                st.markdown("#### Condition assessment")
                st.markdown(result['condition_notes'])

                st.markdown("#### Pricing rationale")
                st.markdown(result['price_reasoning'])

                st.markdown("#### Sell factors")
                for factor in result['sell_factors']:
                    st.markdown(f"{factor['icon']} {factor['text']}")

                st.markdown(f"#### 💡 Listing tip")
                st.info(result['best_listing_tip'])

                # Margin and demand
                col1, col2 = st.columns(2)
                with col1:
                    avg_buy_price = 3
                    margin = result['price_mid'] - avg_buy_price
                    margin_pct = round((margin / result['price_mid']) * 100)
                    margin_class = "margin-good" if margin_pct > 60 else "margin-ok" if margin_pct > 30 else "margin-bad"
                    st.markdown(f"""
                    **Est. profit margin** (vs avg €{avg_buy_price} charity shop buy)

                    <div class="{margin_class}">+€{margin:.0f} · {margin_pct}%</div>
                    """, unsafe_allow_html=True)

                with col2:
                    demand_color = "#1a6b3c" if result['demand_level'] == "High" else "#856404" if result['demand_level'] == "Medium" else "#c62828"
                    st.markdown(f"""
                    **Demand:** {result['demand_level']}

                    ~{result['avg_days_to_sell']} days to sell
                    """)

                # Save to history
                st.session_state.search_history.insert(0, {
                    "search": item_input,
                    "item": result['item_name'],
                    "brand": result.get('brand_detected'),
                    "price": result['price_mid'],
                    "condition": result['condition'],
                    "ts": datetime.now().isoformat()
                })

                # Limit history to 8 items
                if len(st.session_state.search_history) > 8:
                    st.session_state.search_history = st.session_state.search_history[:8]

                # Reset image
                st.session_state.uploaded_image = None

            except json.JSONDecodeError as e:
                st.error(f"Failed to parse API response: {e}")
            except anthropic.APIError as e:
                st.error(f"API Error: {e}")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

# History section
if st.session_state.search_history:
    st.markdown("---")
    st.markdown("### Recent lookups")
    for i, h in enumerate(st.session_state.search_history):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{h['item']}**" + (f" · {h['brand']}" if h.get('brand') else ""))
            st.caption(f"{h['condition']} · {h.get('ts', '')[:10]}")
        with col2:
            st.markdown(f"**€{h['price']}**")
