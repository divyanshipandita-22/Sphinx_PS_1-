"""
Green-Truth Auditor - AI-Powered Sustainability Checker
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import our AI modules
from ai_buzzword_detector import AIBuzzwordDetector
from ai_classifier import GreenwashingClassifier
from ai_rag_system import SustainabilityRAG
from web_scraper import ProductScraper

# Page configuration
st.set_page_config(
    page_title="Genuinity",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2e7d32;
        text-align: center;
        margin-bottom: 0;
    }
    .ai-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
        margin-left: 10px;
    }
    .verdict-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .pass {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        border-left: 5px solid #2e7d32;
    }
    .fail {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-left: 5px solid #c62828;
    }
    .warning {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize AI components with caching
@st.cache_resource
def init_ai_components():
    """Load all AI models (cached for performance)"""
    with st.spinner("Loading AI models... (first time takes 1-2 minutes)"):
        buzzword_detector = AIBuzzwordDetector()
        classifier = GreenwashingClassifier()
        rag_system = SustainabilityRAG()
        scraper = ProductScraper()
        
    return buzzword_detector, classifier, rag_system, scraper

# Title
st.markdown('<h1 class="main-header"> Genuinity</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center;"><span class="ai-badge"> AI-Powered with Open-Source Models</span></p>', unsafe_allow_html=True)

st.markdown("""
<p style="text-align: center; font-size: 1.1rem;">
    Stop greenwashing! AI analyzes product descriptions to detect vague marketing claims<br>
    and verify legitimate sustainability certifications.
</p>
""", unsafe_allow_html=True)

st.divider()

# Load AI components
try:
    buzzword_detector, classifier, rag_system, scraper = init_ai_components()
    models_loaded = True
except Exception as e:
    st.error(f"Error loading AI models: {str(e)}")
    st.info("Please make sure all packages are installed: `pip install -r requirements.txt`")
    models_loaded = False

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    **What is Greenwashing?**
    
    Greenwashing is when brands use misleading marketing to appear more environmentally friendly than they actually are.
    
    **How Our AI Works:**
    
    1. **Semantic Analysis** - Detects vague buzzwords
    2. **AI Classification** - Identifies greenwashing patterns
    3. **RAG Verification** - Checks against certification database
    4. **Smart Reasoning** - Explains the verdict
    
    **What Makes a Claim Credible?**
    - Third-party certifications (GOTS, B Corp, etc.)
    - Specific data (percentages, measurements)
    - Verifiable supply chain information
    """)
    
    st.divider()
    
    st.header("Test Products")
    
    test_products = {
        "Suspicious Product": "Our eco-friendly natural t-shirt is sustainably made with organic materials. We care about the planet! Green manufacturing helps reduce environmental impact.",
        "Verified Product": "GOTS certified organic cotton t-shirt. 100% organic fibers, Fair Trade certified factory. Carbon neutral shipping with verified offsets. B Corporation certified.",
        "Mixed Claims": "Our sustainable hoodie uses recycled materials and eco-friendly packaging. We partner with ethical factories. Working towards carbon neutrality."
    }
    
    for name, text in test_products.items():
        if st.button(name, use_container_width=True, key=f"test_{name}"):
            st.session_state.test_text = text
            st.rerun()

# Main input area
st.header("Enter Product Information")

col1, col2 = st.columns([2, 1])

with col1:
    input_type = st.radio(
        "Choose input method:",
        ["Paste Text : ", " Enter URL : "],
        horizontal=True,
        key="input_type"
    )
    
    text_to_analyze = ""
    url_used = None
    
    if input_type == "Paste Text : ":
        text_to_analyze = st.text_area(
            "Product Description",
            value=st.session_state.get('test_text', ''),
            height=150,
            placeholder="Example: 'Our organic cotton shirt is GOTS certified and made in a Fair Trade factory...'",
            key="text_input"
        )
    else:
        url_input = st.text_input(
            "Product URL",
            placeholder="https://www.example.com/product-page",
            key="url_input"
        )
        if url_input and st.button("Scrape Product Page", key="scrape_btn"):
            if models_loaded:
                with st.spinner("Scraping product information..."):
                    text_to_analyze = scraper.scrape(url_input)
                    url_used = url_input
                if text_to_analyze and "Error" not in text_to_analyze:
                    st.success("✓ Product information extracted successfully!")
                    with st.expander("View extracted text"):
                        st.write(text_to_analyze[:500] + "...")
                else:
                    st.error(text_to_analyze)
            else:
                st.error("AI models not loaded properly")

with col2:
    st.markdown("### Quick Tips")
    st.info("""
    **Look for:**
    - Specific certifications (GOTS, B Corp, FSC)
    - Concrete data (e.g., '50% recycled')
    - Third-party verification
    
    **Watch out for:**
    - Vague terms (eco-friendly, natural)
    - No specific claims
    - Missing verification details
    """)

# Analyze button
if st.button(" Run AI Audit", type="primary", use_container_width=True, key="analyze_btn"):
    if not models_loaded:
        st.error("AI models not loaded. Please check your installation.")
    elif not text_to_analyze or len(text_to_analyze.strip()) < 20:
        st.warning("Please provide a product description (at least 20 characters)")
    else:
        with st.spinner(" AI analyzing product claims..."):
            try:
                # Step 1: Semantic buzzword detection
                semantic_results = buzzword_detector.detect_with_similarity(text_to_analyze)
                
                # Step 2: AI Classification
                category, confidence = classifier.classify(text_to_analyze)
                
                # Step 3: RAG Verification
                rag_results = rag_system.verify_claims_with_rag(text_to_analyze)
                certified_brands = rag_system.check_brand(text_to_analyze)
                
                # Step 4: Generate reasoning
                analysis_summary = {
                    'vague_terms': semantic_results['vague_critical'] + semantic_results['vague_warning'],
                    'certifications': certified_brands
                }
                reasoning = classifier.generate_reasoning(text_to_analyze, analysis_summary)
                
                # Display Results
                st.divider()
                st.header("AI Audit Results")
                
                # Calculate verdict
                has_certifications = len(certified_brands) > 0 or len(rag_results) > 0
                has_vague_terms = len(semantic_results['vague_critical']) > 0
                vague_count = len(semantic_results['vague_critical']) + len(semantic_results['vague_warning'])
                
                if has_certifications:
                    verdict = "PASS"
                    verdict_class = "pass"
                    verdict_icon = "✅"
                    verdict_message = "This product shows legitimate sustainability credentials!"
                elif has_vague_terms and vague_count > 2:
                    verdict = "FAIL"
                    verdict_class = "fail"
                    verdict_icon = "❌"
                    verdict_message = "Multiple vague marketing terms detected with no verification."
                elif has_vague_terms:
                    verdict = "WARNING"
                    verdict_class = "warning"
                    verdict_icon = "⚠️"
                    verdict_message = "Suspicious marketing language found. Verify claims."
                else:
                    verdict = "UNCLEAR"
                    verdict_class = "warning"
                    verdict_icon = "❓"
                    verdict_message = "No clear sustainability claims found."
                
                # Verdict box
                st.markdown(f"""
                <div class="verdict-box {verdict_class}">
                    <h2 style="margin: 0;">{verdict_icon} Verdict: {verdict}</h2>
                    <p style="margin: 10px 0 0 0; font-size: 1.1rem;">{verdict_message}</p>
                    <p style="margin: 10px 0 0 0;">{reasoning}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{vague_count}</h3>
                        <p>Vague Terms Found</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{len(certified_brands) + len(rag_results)}</h3>
                        <p>Verifications Found</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{len(text_to_analyze.split())}</h3>
                        <p>Words Analyzed</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    confidence_color = "green" if confidence > 0.7 else "orange"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: {confidence_color};">{confidence:.0%}</h3>
                        <p>AI Confidence</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Detailed Analysis Tabs
                tab1, tab2, tab3 = st.tabs(["🔍 Suspicious Terms", "📚 Verified Info", "💡 AI Analysis"])
                
                with tab1:
                    st.subheader("Suspicious Marketing Terms Detected")
                    
                    if semantic_results['vague_critical']:
                        st.warning("🚨 Highly Suspicious Terms:")
                        for item in semantic_results['vague_critical'][:5]:
                            st.markdown(f"- **'{item['matched_term']}'** (confidence: {item['similarity']:.0%})")
                            st.caption(f"  Context: \"{item['sentence'][:150]}...\"")
                    
                    if semantic_results['vague_warning']:
                        st.info("⚠️ Suspicious Terms (Needs Verification):")
                        for item in semantic_results['vague_warning'][:5]:
                            st.markdown(f"- **'{item['matched_term']}'** (confidence: {item['similarity']:.0%})")
                    
                    if not semantic_results['vague_critical'] and not semantic_results['vague_warning']:
                        st.success("✅ No suspicious marketing terms detected!")
                    
                    if semantic_results['legitimate']:
                        st.success("✅ Legitimate Sustainability Language Found:")
                        for item in semantic_results['legitimate'][:3]:
                            st.markdown(f"- **'{item['matched_term']}'**")
                
                with tab2:
                    st.subheader("Verified Sustainability Information")
                    
                    if certified_brands:
                        st.success(f"🏢 Certified Brands Detected:")
                        for brand in certified_brands:
                            st.markdown(f"- **{brand}** (Verified in our database)")
                    
                    if rag_results:
                        for i, result in enumerate(rag_results[:3]):
                            with st.expander(f"Claim {i+1}: {result['claim'][:100]}..."):
                                st.markdown("**What our knowledge base says:**")
                                for knowledge in result['relevant_knowledge']:
                                    st.write(f"📖 {knowledge}")
                    
                    if not certified_brands and not rag_results:
                        st.info("No verified certifications or brands found in this product description.")
                        st.markdown("""
                        **Legitimate certifications to look for:**
                        - GOTS (Global Organic Textile Standard)
                        - B Corp Certification
                        - Fair Trade Certified
                        - FSC (Forest Stewardship Council)
                        - OEKO-TEX
                        """)
                
                with tab3:
                    st.subheader("AI Analysis & Recommendations")
                    st.markdown(f"**Classification:** {category}")
                    st.markdown(f"**Confidence Score:** {confidence:.1%}")
                    
                    st.divider()
                    
                    st.subheader("Recommendations")
                    if verdict == "FAIL":
                        st.markdown("""
                        **⚠️ This product shows signs of greenwashing:**
                        - Uses vague marketing terms without verification
                        - No legitimate certifications mentioned
                        - Lacks specific data or evidence
                        
                        **What to do:**
                        - Look for products with third-party certifications
                        - Check for specific percentages (e.g., "70% recycled content")
                        - Verify claims on the company's sustainability page
                        """)
                    elif verdict == "WARNING":
                        st.markdown("""
                        **⚠️ This product needs verification:**
                        - Contains marketing language but lacks evidence
                        - Consider checking the company's website for sustainability reports
                        - Look for certification logos on packaging
                        """)
                    elif verdict == "PASS":
                        st.markdown("""
                        **✅ This product shows good sustainability practices:**
                        - Contains legitimate certifications or verifiable claims
                        - Uses specific, evidence-based language
                        
                        **Still be mindful:**
                        - No single certification covers everything
                        - Check if certifications are current
                        - Look for multiple credentials for best assurance
                        """)
            
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.info("Please try with a different text or check your internet connection for model downloads.")

# Footer
st.divider()
st.markdown("""
<p style="text-align: center; font-size: 0.8rem; color: gray;">
    🌿 Genuinity | Powered by Open-Source AI<br>
    ClimateBERT • BART • Sentence Transformers • RAG with ChromaDB<br>
    This tool is for informational purposes. Always verify with official sources.
</p>
""", unsafe_allow_html=True)