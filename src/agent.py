"""
Aspartame AI: Enhanced Health Research Agent with Academic Literature Integration
Now includes PubMed, arXiv, and scientific paper analysis
"""

import os
from typing import Dict, List, Any, TypedDict
from dataclasses import dataclass
import requests
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import Graph, StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.tools import tool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our academic tools
from academic_tools import PubMedSearcher, ArXivSearcher, AcademicPaper

# Enhanced State Schema with academic papers
class ResearchState(TypedDict):
    query: str
    research_plan: str
    academic_papers: List[Dict[str, Any]]  # NEW: Academic research papers
    web_sources: List[Dict[str, Any]]      # Renamed from 'sources'
    analysis: str
    medical_summary: str
    confidence_score: float
    current_step: str
    evidence_grade: str                    # NEW: GRADE framework assessment

@dataclass
class HealthSource:
    title: str
    url: str
    content: str
    source_type: str  # "academic", "medical_site", "news"
    credibility_score: float
    publish_date: str = ""

class AspartameAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        
        # Initialize academic searchers
        email = os.getenv("PUBMED_EMAIL", "research@example.com")
        self.pubmed = PubMedSearcher(email=email)
        self.arxiv = ArXivSearcher()
        
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the enhanced LangGraph state machine with academic search"""
        
        # Define the graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes - NEW academic search step
        workflow.add_node("research_planning", self.research_planning)
        workflow.add_node("academic_search", self.academic_search)  # NEW
        workflow.add_node("web_search", self.web_search)
        workflow.add_node("content_analysis", self.content_analysis)
        workflow.add_node("generate_summary", self.medical_summary)
        
        # Define the enhanced flow
        workflow.set_entry_point("research_planning")
        workflow.add_edge("research_planning", "academic_search")    # NEW
        workflow.add_edge("academic_search", "web_search")          # NEW
        workflow.add_edge("web_search", "content_analysis")
        workflow.add_edge("content_analysis", "generate_summary")
        workflow.add_edge("generate_summary", END)
        
        return workflow.compile()

    def research_planning(self, state: ResearchState) -> ResearchState:
        """Step 1: Plan the research approach"""
        
        planning_prompt = f"""
        You are a medical research planner. Given this query: "{state['query']}"
        
        Create a focused research plan that identifies:
        1. Key academic search terms for finding peer-reviewed studies
        2. Specific health aspects to investigate (safety, efficacy, mechanisms)
        3. Types of studies to prioritize (RCTs, meta-analyses, systematic reviews)
        4. Potential web sources for additional context
        
        Focus on evidence-based medicine approaches.
        """
        
        messages = [SystemMessage(content=planning_prompt)]
        response = self.llm.invoke(messages)
        
        return {
            **state,
            "research_plan": response.content,
            "current_step": "Research Planning Complete"
        }

    def academic_search(self, state: ResearchState) -> ResearchState:
        """NEW: Step 2: Search academic literature"""
        
        # Extract academic search terms from research plan
        academic_prompt = f"""
        Based on this research plan: {state['research_plan']}
        
        Generate 2 focused search queries for academic databases about: {state['query']}
        
        Focus on:
        - Main topic keywords only (e.g., "creatine safety", "vitamin D deficiency")
        - Keep queries simple and direct
        - Use AND to combine 2-3 key terms max
        
        Format as: query1|query2
        Examples:
        - "creatine supplementation"
        - "creatine safety"
        """
        
        messages = [SystemMessage(content=academic_prompt)]
        response = self.llm.invoke(messages)
        
        search_queries = response.content.split('|')
        academic_papers = []
        
        print(f"🔬 Academic search queries: {search_queries}")  # Debug
        
        # Search PubMed with each query
        for query in search_queries[:2]:
            clean_query = query.strip().strip('"')  # Remove quotes
            print(f"🔍 Searching PubMed for: '{clean_query}'")  # Debug
            
            papers = self.pubmed.search_papers(clean_query, max_results=3)
            print(f"📄 Found {len(papers)} papers for '{clean_query}'")  # Debug
            academic_papers.extend(papers)
        
        # Also search arXiv for recent preprints if we need more papers
        if len(academic_papers) < 3:
            print("🔍 Searching arXiv for additional papers...")
            arxiv_papers = self.arxiv.search_papers(search_queries[0].strip(), max_results=2)
            print(f"📄 Found {len(arxiv_papers)} arXiv papers")
            academic_papers.extend(arxiv_papers)
        
        # Convert to dict format for state
        papers_data = []
        for paper in academic_papers:
            papers_data.append({
                "title": paper.title,
                "authors": paper.authors,
                "abstract": paper.abstract,
                "journal": paper.journal,
                "publication_date": paper.publication_date,
                "url": paper.url,
                "study_type": paper.study_type,
                "sample_size": paper.sample_size,
                "quality_score": paper.quality_score,
                "peer_reviewed": paper.peer_reviewed,
                "pmid": getattr(paper, 'pmid', None)
            })
        
        print(f"✅ Total academic papers collected: {len(papers_data)}")  # Debug
        
        return {
            **state,
            "academic_papers": papers_data,
            "current_step": f"Found {len(papers_data)} academic papers"
        }

    def web_search(self, state: ResearchState) -> ResearchState:
        """Step 3: Search for additional web sources (now complementing academic papers)"""
        
        # Extract key terms from research plan
        search_prompt = f"""
        Based on this research plan: {state['research_plan']}
        
        Generate 2 specific search queries to find additional health information about: {state['query']}
        
        Focus on medical organizations, health agencies, and clinical guidelines.
        
        Format as: query1|query2
        """
        
        messages = [SystemMessage(content=search_prompt)]
        response = self.llm.invoke(messages)
        
        search_queries = response.content.split('|')
        sources = []
        
        print(f"🌐 Web search queries: {search_queries}")  # Debug
        
        # Search using Tavily
        for query in search_queries[:2]:  # Limit for speed
            clean_query = query.strip().strip('"')
            print(f"🔍 Web searching for: '{clean_query}'")  # Debug
            
            web_results = self._tavily_search(clean_query)
            print(f"📄 Found {len(web_results)} web sources for '{clean_query}'")  # Debug
            sources.extend(web_results)
        
        print(f"✅ Total web sources collected: {len(sources)}")  # Debug
        
        return {
            **state,
            "web_sources": sources,  # Make sure this field name matches
            "current_step": f"Found {len(sources)} web sources"
        }

    def content_analysis(self, state: ResearchState) -> ResearchState:
        """Step 4: Enhanced analysis including academic papers"""
        
        # Prepare academic papers for analysis
        academic_text = ""
        if state['academic_papers']:
            academic_text = "\n\n".join([
                f"ACADEMIC PAPER {i+1}:\n"
                f"Title: {paper['title']}\n"
                f"Journal: {paper['journal']} ({paper['publication_date']})\n"
                f"Study Type: {paper['study_type']}\n"
                f"Sample Size: {paper.get('sample_size', 'Not specified')}\n"
                f"Quality Score: {paper['quality_score']:.2f}/1.0\n"
                f"Abstract: {paper['abstract'][:300]}...\n"
                for i, paper in enumerate(state['academic_papers'][:3])
            ])
        
        # Prepare web sources
        web_text = ""
        if state['web_sources']:
            web_text = "\n\n".join([
                f"WEB SOURCE {i+1}: {src['title']}\n{src['content'][:300]}..."
                for i, src in enumerate(state['web_sources'][:3])
            ])
        
        analysis_prompt = f"""
        You are a medical research analyst. Analyze this evidence about: "{state['query']}"
        
        ACADEMIC RESEARCH:
        {academic_text}
        
        WEB SOURCES:
        {web_text}
        
        Provide a comprehensive analysis covering:
        
        1. **Evidence Hierarchy**: Rate the quality of evidence (academic papers > medical sites > general web)
        2. **Study Quality**: Assess methodology, sample sizes, and study types
        3. **Consensus vs Controversy**: Areas of agreement and disagreement
        4. **Risk Assessment**: Specific risks identified with confidence levels
        5. **Benefits Assessment**: Potential benefits with supporting evidence
        6. **Limitations**: What's missing or uncertain in the research
        7. **Clinical Significance**: Real-world implications
        
        Use evidence-based language and cite specific studies when making claims.
        """
        
        messages = [SystemMessage(content=analysis_prompt)]
        response = self.llm.invoke(messages)
        
        # Generate GRADE assessment
        evidence_grade = self._assess_evidence_grade(state['academic_papers'])
        
        return {
            **state,
            "analysis": response.content,
            "evidence_grade": evidence_grade,
            "current_step": "Enhanced analysis complete"
        }

    def medical_summary(self, state: ResearchState) -> ResearchState:
        """Step 5: Create enhanced doctor-like summary with academic backing"""
        
        summary_prompt = f"""
        You are a knowledgeable physician providing evidence-based medical advice.
        
        Query: "{state['query']}"
        Analysis: {state['analysis']}
        Evidence Grade: {state['evidence_grade']}
        Academic Papers Found: {len(state['academic_papers'])}
        
        Provide a comprehensive medical summary in this format:
        
        ## Bottom Line
        [Clear recommendation based on the best available evidence]
        
        ## Evidence Quality: {state['evidence_grade']}
        [Explain what this evidence grade means]
        
        ## What the Research Shows
        [Key findings from academic studies, cite specific study types]
        
        ## Potential Benefits
        - [List benefits with evidence quality indicators]
        
        ## Potential Risks  
        - [List risks with evidence quality indicators]
        
        ## Clinical Recommendations
        [Specific, actionable medical advice]
        
        ## Evidence Limitations
        [What we don't know, gaps in research]
        
        ## Confidence in Recommendation
        [How confident you are and why]
        
        Use medical terminology appropriately but explain complex concepts clearly.
        When citing evidence, mention study types (RCT, meta-analysis, etc.).
        """
        
        messages = [SystemMessage(content=summary_prompt)]
        response = self.llm.invoke(messages)
        
        # Enhanced confidence scoring
        confidence = self._calculate_confidence(state['academic_papers'], state['web_sources'])
        
        return {
            **state,
            "medical_summary": response.content,
            "confidence_score": confidence,
            "current_step": "Research Complete"
        }

    def _assess_evidence_grade(self, academic_papers: List[Dict]) -> str:
        """Assess evidence quality using GRADE framework"""
        if not academic_papers:
            return "Very Low - No academic studies found"
        
        # Count study types
        study_types = [paper.get('study_type', 'unknown') for paper in academic_papers]
        
        # Assess based on highest quality studies available
        if 'meta-analysis' in study_types:
            if len([p for p in academic_papers if p.get('quality_score', 0) > 0.8]) >= 2:
                return "High - Multiple high-quality meta-analyses"
            else:
                return "Moderate - Meta-analysis available but limited quality"
        elif 'rct' in study_types:
            rct_count = study_types.count('rct')
            if rct_count >= 3:
                return "Moderate - Multiple randomized controlled trials"
            else:
                return "Low - Limited randomized controlled trials"
        elif any(t in study_types for t in ['cohort', 'case-control']):
            return "Low - Observational studies only"
        else:
            return "Very Low - Limited study evidence"

    def _calculate_confidence(self, academic_papers: List[Dict], web_sources: List[Dict]) -> float:
        """Enhanced confidence calculation including academic papers"""
        if not academic_papers and not web_sources:
            return 0.2
        
        # Academic papers contribute more to confidence
        academic_confidence = 0.0
        if academic_papers:
            avg_quality = sum(p.get('quality_score', 0) for p in academic_papers) / len(academic_papers)
            study_diversity = len(set(p.get('study_type') for p in academic_papers)) / 5
            academic_confidence = avg_quality * 0.8 + study_diversity * 0.2
        
        # Web sources contribute less
        web_confidence = 0.0
        if web_sources:
            avg_credibility = sum(s.get("credibility_score", 0.5) for s in web_sources) / len(web_sources)
            web_confidence = avg_credibility * 0.5
        
        # Weighted combination (academic papers weighted more heavily)
        total_confidence = academic_confidence * 0.7 + web_confidence * 0.3
        
        return min(0.95, total_confidence)

    def _tavily_search(self, query: str) -> List[Dict[str, Any]]:
        """Search using Tavily API - real results only"""
        
        print(f"🔍 Tavily search for: '{query}'")  # Debug
        
        if not self.tavily_key:
            print("⚠️ No Tavily API key configured")
            return []
        
        try:
            headers = {"Authorization": f"Bearer {self.tavily_key}"}
            data = {
                "query": f"{query} health medical",
                "search_depth": "basic",
                "max_results": 3,
                "include_domains": [
                    "mayoclinic.org", "webmd.com", "healthline.com", 
                    "nih.gov", "cdc.gov", "who.int", "harvard.edu",
                    "clevelandclinic.org", "hopkinsmedicine.org"
                ]
            }
            
            print(f"📡 Making Tavily API request...")  # Debug
            response = requests.post(
                "https://api.tavily.com/search",
                headers=headers,
                json=data,
                timeout=10
            )
            
            print(f"📡 Tavily response status: {response.status_code}")  # Debug
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                print(f"📄 Tavily returned {len(results)} results")  # Debug
                
                if not results:
                    print("⚠️ Tavily returned empty results")
                    return []
                
                processed_results = []
                for r in results:
                    processed_results.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                        "source_type": self._classify_source(r.get("url", "")),
                        "credibility_score": self._score_credibility(r.get("url", ""))
                    })
                
                print(f"✅ Processed {len(processed_results)} web sources")
                return processed_results
            else:
                print(f"❌ Tavily API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Tavily search error: {e}")
            return []

    def _classify_source(self, url: str) -> str:
        """Classify source type based on URL"""
        if "pubmed" in url or "ncbi" in url:
            return "academic"
        elif any(domain in url for domain in ["mayoclinic", "nih.gov", "cdc.gov"]):
            return "medical_authority"
        elif any(domain in url for domain in ["webmd", "healthline"]):
            return "medical_site"
        else:
            return "news"

    def _score_credibility(self, url: str) -> float:
        """Score source credibility"""
        if "pubmed" in url or "ncbi" in url:
            return 0.95
        elif any(domain in url for domain in ["nih.gov", "cdc.gov"]):
            return 0.9
        elif "mayoclinic" in url:
            return 0.85
        elif any(domain in url for domain in ["webmd", "healthline"]):
            return 0.7
        else:
            return 0.5

    def research(self, query: str) -> Dict[str, Any]:
        """Main research method"""
        initial_state = ResearchState(
            query=query,
            research_plan="",
            academic_papers=[],
            web_sources=[],  # Make sure this is initialized
            analysis="",
            medical_summary="",
            confidence_score=0.0,
            current_step="Starting Research",
            evidence_grade=""
        )
        
        print(f"🚀 Starting research for: '{query}'")  # Debug
        
        # Run the enhanced graph
        result = self.graph.invoke(initial_state)
        
        print(f"✅ Research complete!")  # Debug
        print(f"   Academic papers: {len(result.get('academic_papers', []))}")
        print(f"   Web sources: {len(result.get('web_sources', []))}")
        print(f"   Confidence: {result.get('confidence_score', 0):.2f}")
        
        return result

# Test function
if __name__ == "__main__":
    agent = AspartameAgent()
    result = agent.research("Is drinking Diet Coke safe?")
    print("Research Complete!")
    print(f"Confidence: {result['confidence_score']:.2f}")
    print(f"Evidence Grade: {result['evidence_grade']}")
    print(f"Academic Papers: {len(result['academic_papers'])}")
    print("\nSummary:")
    print(result['medical_summary'])