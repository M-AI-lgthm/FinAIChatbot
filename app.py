import os
import streamlit as st
import google.generativeai as gen_ai

# Set up Google AI model
gen_ai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = gen_ai.GenerativeModel('models/gemini-2.5-flash')

# --- Product Catalog (Your RAG Data Source) ---
products = {
    "budget-pro": {
        "name": "Budget Pro",
        "description": "An advanced tool for managing personal and small business finances.",
        "features": ["Expense tracking", "Income categorization", "Monthly reports"],
    },
    "invest-wise": {
        "name": "InvestWise",
        "description": "AI-powered platform for stock market analysis and portfolio management.",
        "features": ["Real-time data", "Risk assessment", "Diversification advice"],
    },
    "tax-master": {
        "name": "Tax Master",
        "description": "Simplifies tax preparation and filing for individuals and businesses.",
        "features": ["Automated forms", "Audit protection", "Deduction finder"],
    }
}

# --- Website Styling and Layout ---
st.set_page_config(
    page_title="Demo Financial Software",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

# --- Use native Streamlit components for menu bar ---
pages = ["Home", "Platform", "Solutions", "Developer", "Resource", "Company", "Sign in", "Contact us"]

# Create a container for the menu bar to style it
st.markdown('<div class="menu-bar">', unsafe_allow_html=True)
cols = st.columns(len(pages))
for col, page in zip(cols, pages):
    with col:
        if st.button(page, key=page):
            st.session_state.current_page = page
st.markdown('</div>', unsafe_allow_html=True)

# Add a horizontal line to separate the menu from the content
st.markdown("---")


# --- Page Content based on selected menu item ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if st.session_state.current_page == "Home":
    st.title("Demo Financial Software Products & Solutions")
    st.markdown("### Secure your financial future with our demo innovative software.")
    st.image("https://images.unsplash.com/photo-1542831371-29b0f74f9713?q=80&w=2940&auto=format&fit=crop", width=800)
    st.write("---")
    st.header("Our Services")
    st.write("Explore our range of financial tools, from budgeting and tax preparation to investment analysis.")
    st.write("---")
elif st.session_state.current_page == "Solutions":
    st.header("Solutions")
    st.write("This page will show our different financial solutions.")
elif st.session_state.current_page == "Contact us":
    st.header("Contact Us")
    st.write("You can contact us via this page.")
# Add more elif blocks for other pages

# Custom CSS for the page layout
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #1f013d, #52168f);
        color: white;
    }

    /* New styling for chat bubbles and sidebar */
    .st-emotion-cache-1wiv36a { /* Sidebar background */
        background-color: #1f013d !important;
    }
    .st-emotion-cache-1j8gq1d { /* Sidebar content */
        color: white;
    }
    .st-emotion-cache-1830v4l { /* Streamlit header/sub-header */
        color: white;
    }

    .st-emotion-cache-1c7y2n2 { /* Assistant message bubble */
        background-color: #3b0e5e !important;
        border-radius: 10px;
    }
    .st-emotion-cache-1m74h1w { /* User message bubble */
        background-color: #7b299e !important;
        border-radius: 10px;
    }
    .st-emotion-cache-1g82m8q {
        background-color: transparent !important;
    }
    .st-emotion-cache-1q5b94 {
        background-color: transparent !important;
    }
    .st-emotion-cache-1r6500c {
        background-color: #2c0847 !important;
        border-top: 1px solid #52168f;
    }

    /* Menu bar styling */
    .menu-bar {
        display: flex;
        justify-content: flex-start;
        padding: 10px 0;
        gap: 10px;
    }
    .stButton>button {
        background-color: #4f1d6b !important;
        color: white !important;
        border: 1px solid #7b299e !important;
        border-radius: 8px;
        padding: 10px 15px;
    }
    .stButton>button:hover {
        background-color: #7b299e !important;
        border-color: #7b299e !important;
        color: white !important;
    }
    .stButton>button:active {
        background-color: #52168f !important;
        border-color: #52168f !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Chatbot UI using Streamlit Sidebar ---
with st.sidebar:
    st.header("Fin-AI Sales Assistant")

    # Use st.expander to create a collapsible chat window
    with st.expander("Click to chat", expanded=True):
        def translate_role_for_streamlit(user_role):
            if user_role == "model":
                return "assistant"
            else:
                return user_role

        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[{
                "role": "user",
                "parts": "You are a helpful and professional financial software assistant for the company 'Fin-Tech Solutions'. Your goal is to guide customers, offer product information, and, if they are interested, collect their details to schedule an appointment with a sales representative."
            }])
            st.session_state.chat_session.send_message("Hello! I'm your virtual financial assistant. How can I help you today?")

        chat_history_container = st.container(height=380, border=False)

        with chat_history_container:
            for message in st.session_state.chat_session.history:
                with st.chat_message(translate_role_for_streamlit(message.role), avatar='👤'):
                    st.markdown(message.parts[0].text)

        user_prompt = st.chat_input("Ask about our products...")

        if user_prompt:
            retrieved_info = ""
            keywords = user_prompt.lower().split()

            for key, product in products.items():
                if any(keyword in key.lower() or keyword in product['name'].lower() for keyword in keywords):
                    retrieved_info += (
                        f"Product Name: {product['name']}\n"
                        f"Description: {product['description']}\n"
                        f"Features: {', '.join(product['features'])}\n\n"
                    )

            augmented_prompt = f"""
            You are a helpful financial software assistant. You have access to the following product information:
            ---
            {retrieved_info if retrieved_info else 'No relevant product information found.'}
            ---
            Based on the information above, respond to the user's question. If the information is not relevant, use your own knowledge to respond.
            User's Question: {user_prompt}
            """

            try:
                gemini_response = st.session_state.chat_session.send_message(augmented_prompt)
                with chat_history_container:
                    st.chat_message("user", avatar='👤').markdown(user_prompt)
                    with st.chat_message("assistant", avatar='👤'):
                        st.markdown(gemini_response.text)
            except Exception as e:
                with chat_history_container:
                    with st.chat_message("assistant", avatar='👤'):
                        st.error(f"An error occurred: {e}")
