"""
Aspartame AI - Enhanced Streamlit Frontend with Academic Research Display
"""

import streamlit as st
import sys
import os
from datetime import datetime
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import AspartameAgent

# Page config
st.set_page_config(
    page_title="Aspartame AI - Academic Health Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for academic display
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
    
    .evidence-high { background: #d4edda; border-left: 4px solid #28a745; padding: 0.5rem; }
    .evidence-moderate { background: #fff3cd; border-left: 4px solid #ffc107; padding: 0.5rem; }
    .evidence-low { background: #f8d7da; border-left: 4px solid #dc3545; padding: 0.5rem; }
    
    .academic-paper {
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }
    
    .academic-paper:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .paper-title {
        font-weight: bold;
        color: #2c3e50;
        font-size: 1.1em;
        margin-bottom: 0.5rem;
    }
    
    .paper-meta {
        color: #666;
        font-size: 0.9em;
        margin-bottom: 0.5rem;
    }
    
    .quality-score {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
    }
    
    .quality-high { background: #d4edda; color: #155724; }
    .quality-medium { background: #fff3cd; color: #856404; }
    .quality-low { background: #f8d7da; color: #721c24; }
    
    .study-type {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8em;
        margin-left: 0.5rem;
    }
    
    .study-meta-analysis { background: #e7f3ff; color: #0056b3; }
    .study-rct { background: #e6f7ff; color: #0050b3; }
    .study-cohort { background: #f0f5ff; color: #1d39c4; }
    .study-other { background: #f5f5f5; color: #666; }
    
    .research-progress {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .step-complete {
        color: #28a745;
        font-weight: bold;
    }
    
    .step-current {
        color: #007bff;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .source-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    
    .stat-box {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #007bff;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'research_result' not in st.session_state:
    st.session_state.research_result = None
if 'research_history' not in st.session_state:
    st.session_state.research_history = []

def init_agent():
    """Initialize the agent with error handling"""
    try:
        if st.session_state.agent is None:
            with st.spinner("🔬 Initializing Aspartame AI with PubMed integration..."):
                st.session_state.agent = AspartameAgent()
        return True
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        st.info("Please check your API keys in the .env file")
        return False

def format_confidence(confidence: float) -> str:
    """Format confidence score with color coding"""
    if confidence >= 0.8:
        return f'<span class="confidence-high">High ({confidence:.1%})</span>'
    elif confidence >= 0.6:
        return f'<span class="confidence-medium">Medium ({confidence:.1%})</span>'
    else:
        return f'<span class="confidence-low">Low ({confidence:.1%})</span>'

def format_evidence_grade(grade: str) -> str:
    """Format evidence grade with appropriate styling"""
    if "High" in grade:
        return f'<div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 0.75rem; margin: 0.5rem 0;"><strong style="color: #155724;">Evidence Quality:</strong> <span style="color: #155724;">{grade}</span></div>'
    elif "Moderate" in grade:
        return f'<div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; padding: 0.75rem; margin: 0.5rem 0;"><strong style="color: #856404;">Evidence Quality:</strong> <span style="color: #856404;">{grade}</span></div>'
    else:
        return f'<div style="background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 6px; padding: 0.75rem; margin: 0.5rem 0;"><strong style="color: #721c24;">Evidence Quality:</strong> <span style="color: #721c24;">{grade}</span></div>'

def format_quality_score(score: float) -> str:
    """Format paper quality score"""
    if score >= 0.8:
        return f'<span class="quality-score quality-high">{score:.2f}/1.0</span>'
    elif score >= 0.6:
        return f'<span class="quality-score quality-medium">{score:.2f}/1.0</span>'
    else:
        return f'<span class="quality-score quality-low">{score:.2f}/1.0</span>'

def format_study_type(study_type: str) -> str:
    """Format study type with appropriate styling"""
    type_classes = {
        "meta-analysis": "study-meta-analysis",
        "rct": "study-rct", 
        "cohort": "study-cohort",
        "case-control": "study-cohort",
        "cross-sectional": "study-other",
        "review": "study-other",
        "observational": "study-other",
        "preprint": "study-other"
    }
    
    class_name = type_classes.get(study_type, "study-other")
    display_name = study_type.replace("-", " ").title()
    
    return f'<span class="study-type {class_name}">{display_name}</span>'

def display_academic_paper(paper: dict, index: int):
    """Display a single academic paper with clean formatting"""
    
    quality_score = paper.get('quality_score', 0)
    
    # Clean quality score formatting
    if quality_score >= 0.8:
        quality_badge = f'<span style="background: #d4edda; color: #155724; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8em; font-weight: bold;">{quality_score:.2f}/1.0</span>'
    elif quality_score >= 0.6:
        quality_badge = f'<span style="background: #fff3cd; color: #856404; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8em; font-weight: bold;">{quality_score:.2f}/1.0</span>'
    else:
        quality_badge = f'<span style="background: #f8d7da; color: #721c24; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8em; font-weight: bold;">{quality_score:.2f}/1.0</span>'
    
    # Clean study type formatting
    study_type = paper.get('study_type', 'unknown')
    if study_type == 'meta-analysis':
        type_badge = f'<span style="background: #e7f3ff; color: #0056b3; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8em; margin-left: 0.5rem;">Meta Analysis</span>'
    elif study_type == 'rct':
        type_badge = f'<span style="background: #e6f7ff; color: #0050b3; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8em; margin-left: 0.5rem;">RCT</span>'
    else:
        type_badge = f'<span style="background: #f5f5f5; color: #666; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8em; margin-left: 0.5rem;">{study_type.title()}</span>'
    
    # Clean peer review status
    peer_status = "🔒 Peer Reviewed" if paper.get('peer_reviewed', False) else "⚠️ Preprint"
    
    st.markdown(f"""
    <div style="border: 1px solid #e9ecef; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; background: #f8f9fa;">
        <div style="font-weight: bold; color: #2c3e50; font-size: 1.1em; margin-bottom: 0.5rem;">
            {index}. {paper.get('title', 'Untitled')}
        </div>
        <div style="color: #666; font-size: 0.9em; margin-bottom: 0.5rem;">
            <strong>Journal:</strong> {paper.get('journal', 'Unknown')} ({paper.get('publication_date', 'Unknown date')})<br>
            <strong>Authors:</strong> {', '.join(paper.get('authors', ['Unknown'])[:3])}{' et al.' if len(paper.get('authors', [])) > 3 else ''}<br>
            <strong>Sample Size:</strong> {paper.get('sample_size', 'Not specified')}
        </div>
        <div style="margin: 0.5rem 0;">
            {quality_badge}
            {type_badge}
            <span style="margin-left: 0.5rem; font-size: 0.9em;">{peer_status}</span>
        </div>
        <div style="margin-top: 0.5rem;">
            <strong>Abstract:</strong> {paper.get('abstract', 'No abstract available')[:200]}...
        </div>
        {f'<div style="margin-top: 0.5rem;"><a href="{paper.get("url", "#")}" target="_blank" style="color: #007bff; text-decoration: none;">🔗 View Paper</a></div>' if paper.get('url') else ''}
    </div>
    """, unsafe_allow_html=True)

def display_research_stats(result):
    """Display research statistics"""
    academic_count = len(result.get('academic_papers', []))
    web_count = len(result.get('web_sources', []))
    
    # Calculate average quality
    avg_quality = 0
    if academic_count > 0:
        total_quality = sum(p.get('quality_score', 0) for p in result.get('academic_papers', []))
        avg_quality = total_quality / academic_count
    
    # Count study types
    study_types = {}
    for paper in result.get('academic_papers', []):
        study_type = paper.get('study_type', 'unknown')
        study_types[study_type] = study_types.get(study_type, 0) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{academic_count}</div>
            <div class="stat-label">Academic Papers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color = "#007bff" if web_count > 0 else "#999"
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number" style="color: {color};">{web_count}</div>
            <div class="stat-label">Web Sources</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{avg_quality:.2f}</div>
            <div class="stat-label">Avg Quality Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rct_count = study_types.get('rct', 0) + study_types.get('meta-analysis', 0)
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{rct_count}</div>
            <div class="stat-label">High-Quality Studies</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🔬 Aspartame AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your AI research assistant for evidence-based health decisions</p>', unsafe_allow_html=True)
    
    # Sidebar with enhanced info
    with st.sidebar:
        st.header("🧬 About Aspartame AI")
        st.write("""
        **Advanced LangGraph Agent** that conducts comprehensive health research:
        
        🎯 **Research Process:**
        1. **Strategic Planning** - Develops research methodology
        2. **Academic Search** - Queries PubMed & arXiv databases  
        3. **Web Research** - Searches medical authorities
        4. **Evidence Analysis** - Grades quality using GRADE framework
        5. **Medical Summary** - Provides doctor-level recommendations
        
        🏆 **What Makes It Special:**
        - Real peer-reviewed research papers
        - Study quality assessment
        - Evidence grading (High/Moderate/Low)
        - Confidence scoring
        - Professional medical advice
        """)
        
        st.header("🎯 Try These Queries")
        example_queries = [
            "Is creatine safe to supplement?",
            "Should I take vitamin D supplements?", 
            "Is intermittent fasting healthy?",
            "Are artificial sweeteners harmful?",
            "What are the health effects of coffee?",
            "Is the Mediterranean diet effective?",
            "Are probiotics beneficial for health?"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.current_query = query

    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Ask Your Health Question")
        
        # Query input
        query = st.text_area(
            "What would you like to research?",
            value=st.session_state.get('current_query', ''),
            height=100,
            placeholder="e.g., Is creatine safe to supplement? What are the health benefits of omega-3?"
        )
        
        # Research button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            research_clicked = st.button("🔬 Research", type="primary", disabled=not query.strip())
        
        with col_btn2:
            if st.button("🗑️ Clear"):
                st.session_state.research_result = None
                st.rerun()
        
        # Research execution with simple progress
        if research_clicked and query.strip():
            if not init_agent():
                return
                
            # Simple progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Planning
                status_text.text("🧠 Planning research strategy...")
                progress_bar.progress(20)
                time.sleep(0.5)
                
                # Step 2: Academic Search
                status_text.text("🔍 Searching PubMed & academic databases...")
                progress_bar.progress(40)
                time.sleep(0.5)
                
                # Step 3: Web Search
                status_text.text("🌐 Gathering additional medical sources...")
                progress_bar.progress(60)
                
                # Run the actual research
                result = st.session_state.agent.research(query)
                
                # Step 4: Analysis
                status_text.text("📊 Analyzing evidence quality...")
                progress_bar.progress(80)
                time.sleep(0.5)
                
                # Step 5: Summary
                status_text.text("✍️ Generating medical summary...")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Store result
                st.session_state.research_result = result
                st.session_state.research_result['timestamp'] = datetime.now()
                st.session_state.research_result['query'] = query
                
                # Add to history
                st.session_state.research_history.insert(0, {
                    'query': query,
                    'timestamp': datetime.now(),
                    'confidence': result['confidence_score'],
                    'academic_count': len(result.get('academic_papers', [])),
                    'evidence_grade': result.get('evidence_grade', 'Unknown')
                })
                
                # Clear progress
                progress_bar.empty()
                status_text.empty()
                st.success("✅ Research completed!")
                
            except Exception as e:
                st.error(f"Research failed: {str(e)}")
                progress_bar.empty()
                status_text.empty()
    
    with col2:
        st.header("📚 Research History")
        
        if st.session_state.research_history:
            for i, item in enumerate(st.session_state.research_history[:5]):
                with st.expander(f"🕒 {item['timestamp'].strftime('%H:%M')} - {item['query'][:25]}..."):
                    st.write(f"**Query:** {item['query']}")
                    st.write(f"**Confidence:** {format_confidence(item['confidence'])}", unsafe_allow_html=True)
                    st.write(f"**Academic Papers:** {item.get('academic_count', 0)}")
                    st.write(f"**Evidence Grade:** {item.get('evidence_grade', 'Unknown')}")
                    st.write(f"**Time:** {item['timestamp'].strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No research history yet. Start by asking a health question!")

    # Enhanced results display
    if st.session_state.research_result:
        st.divider()
        result = st.session_state.research_result
        
        # Header with clean confidence display
        st.header(f"📋 Research Results: {result.get('query', 'Health Query')}")
        
        # Stats overview
        display_research_stats(result)
        
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Evidence grade and confidence - better layout
        col_conf1, col_conf2 = st.columns([1, 1])
        with col_conf1:
            if result.get('evidence_grade'):
                st.markdown(format_evidence_grade(result['evidence_grade']), unsafe_allow_html=True)
        with col_conf2:
            confidence_html = format_confidence(result['confidence_score'])
            st.markdown(f"""
            <div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 0.75rem; margin: 0.5rem 0;">
                <strong>Research Confidence:</strong> {confidence_html}
            </div>
            """, unsafe_allow_html=True)
        
        # Medical Summary (main content)
        if result.get('medical_summary'):
            st.markdown("### 🏥 Medical Summary")
            st.markdown(result['medical_summary'])
        
        # Expandable sections with enhanced academic display
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Academic Papers (NEW - Enhanced Display)
            if result.get('academic_papers'):
                with st.expander(f"🎓 Academic Papers ({len(result['academic_papers'])})", expanded=True):
                    st.markdown("**Peer-reviewed research from PubMed & arXiv:**")
                    
                    for i, paper in enumerate(result['academic_papers'][:5], 1):
                        display_academic_paper(paper, i)
            
            # Research Plan
            if result.get('research_plan'):
                with st.expander("🎯 Research Strategy"):
                    st.write(result['research_plan'])
        
        with col_right:
            # Web Sources - only show if we have real sources
            if result.get('web_sources') and len(result['web_sources']) > 0:
                with st.expander(f"🌐 Web Sources ({len(result['web_sources'])})"):
                    st.markdown("**Medical websites and authorities:**")
                    for i, source in enumerate(result['web_sources'][:5]):
                        st.markdown(f"""
                        **{i+1}. {source.get('title', 'Untitled')}**  
                        Type: {source.get('source_type', 'unknown')} | Credibility: {source.get('credibility_score', 0):.1f}/1.0  
                        [🔗 View Source]({source.get('url', '#')})
                        """)
            else:
                with st.expander("🌐 Web Sources (0)"):
                    if not os.getenv("TAVILY_API_KEY"):
                        st.warning("⚠️ **Tavily API key not configured.** Add TAVILY_API_KEY to your .env file to enable web search.")
                        st.info("💡 Get a free API key at [tavily.com](https://tavily.com)")
                    else:
                        st.info("No additional web sources found for this query. The academic papers above provide the primary evidence.")
            
            # Detailed Analysis
            if result.get('analysis'):
                with st.expander("📊 Evidence Analysis"):
                    st.write(result['analysis'])
        
        # Download/Share options
        st.divider()
        col_download, col_share = st.columns(2)
        
        with col_download:
            # Create enhanced downloadable report
            academic_section = ""
            if result.get('academic_papers'):
                academic_section = "\n## Academic Papers\n"
                for i, paper in enumerate(result['academic_papers'], 1):
                    academic_section += f"""
{i}. **{paper.get('title', 'Untitled')}**
   - Journal: {paper.get('journal', 'Unknown')} ({paper.get('publication_date', 'Unknown')})
   - Authors: {', '.join(paper.get('authors', ['Unknown'])[:3])}
   - Study Type: {paper.get('study_type', 'Unknown')}
   - Quality Score: {paper.get('quality_score', 0):.2f}/1.0
   - URL: {paper.get('url', 'N/A')}
"""
            
            report = f"""
# Health Research Report
**Query:** {result.get('query', 'N/A')}
**Date:** {result.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M')}
**Evidence Grade:** {result.get('evidence_grade', 'Unknown')}
**Confidence:** {result['confidence_score']:.1%}

## Medical Summary
{result.get('medical_summary', 'N/A')}

{academic_section}

## Evidence Analysis  
{result.get('analysis', 'N/A')}

## Web Sources
{chr(10).join([f"- {s.get('title', 'Untitled')}: {s.get('url', 'N/A')}" for s in result.get('web_sources', [])])}

---
Generated by Aspartame AI - Academic Health Research Agent
Powered by LangGraph with PubMed Integration
            """
            
            st.download_button(
                "📄 Download Full Report",
                report,
                file_name=f"health_research_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )
        
        with col_share:
            st.info("💡 **Tip:** Save this research for your doctor or healthcare provider!")

if __name__ == "__main__":
    main()