"""
Academic Research Tools for Aspartame AI
Integrates with PubMed, arXiv, and other scientific databases
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import time

@dataclass
class AcademicPaper:
    """Structured representation of an academic paper"""
    title: str
    authors: List[str]
    abstract: str
    publication_date: str
    journal: str
    pmid: Optional[str] = None
    doi: Optional[str] = None
    url: str = ""
    study_type: str = "unknown"  # "rct", "meta-analysis", "observational", etc.
    sample_size: Optional[int] = None
    peer_reviewed: bool = True
    impact_factor: Optional[float] = None
    conflicts_disclosed: bool = False
    funding_source: str = ""
    quality_score: float = 0.0

class PubMedSearcher:
    """Search and analyze PubMed research papers"""
    
    def __init__(self, email: str = "research@example.com"):
        self.email = email
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
    def search_papers(self, query: str, max_results: int = 10) -> List[AcademicPaper]:
        """Search PubMed for research papers - real results only"""
        try:
            print(f"🔬 PubMed search for: '{query}'")  # Debug
            
            # Step 1: Search for paper IDs
            pmids = self._search_pmids(query, max_results)
            print(f"📋 Found {len(pmids)} PMIDs: {pmids[:3]}...")  # Debug
            
            if not pmids:
                print(f"No PMIDs found for '{query}', trying simplified search...")
                # Try simplified search - just first word
                simple_query = query.split()[0] if query.split() else query
                pmids = self._search_pmids(simple_query, max_results)
                print(f"📋 Simplified search found {len(pmids)} PMIDs")
            
            if not pmids:
                print("❌ No academic papers found")
                return []
            
            # Step 2: Get detailed paper information
            print(f"📄 Fetching details for {len(pmids)} papers...")
            papers = self._fetch_paper_details(pmids)
            print(f"✅ Got {len(papers)} papers with full details")
            
            # Step 3: Assess quality for each paper
            for paper in papers:
                paper.quality_score = self._assess_paper_quality(paper)
            
            # Sort by quality score (highest first)
            return sorted(papers, key=lambda p: p.quality_score, reverse=True)
            
        except Exception as e:
            print(f"❌ PubMed search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _create_mock_papers(self, query: str) -> List[AcademicPaper]:
        """Create mock papers for demo when PubMed fails"""
        print("Creating mock academic papers for demo...")
        
        mock_papers = [
            AcademicPaper(
                title=f"Systematic Review of {query.title()} Safety and Efficacy",
                authors=["Smith, J.", "Johnson, A.", "Williams, B."],
                abstract=f"Background: {query} supplementation has gained popularity. Methods: We conducted a systematic review of randomized controlled trials. Results: Evidence suggests generally positive safety profile with some considerations. Conclusion: More research needed for optimal dosing guidelines.",
                publication_date="2023",
                journal="Journal of Sports Medicine",
                pmid="12345678",
                url="https://pubmed.ncbi.nlm.nih.gov/12345678/",
                study_type="meta-analysis",
                sample_size=1250,
                peer_reviewed=True,
                quality_score=0.85
            ),
            AcademicPaper(
                title=f"Randomized Controlled Trial: {query.title()} Effects in Healthy Adults", 
                authors=["Brown, C.", "Davis, M."],
                abstract=f"Objective: To assess the effects of {query} supplementation. Design: Double-blind RCT with 12-week intervention. Participants: 180 healthy adults. Results: Significant improvements observed with minimal side effects reported.",
                publication_date="2022",
                journal="Clinical Nutrition Research",
                pmid="87654321", 
                url="https://pubmed.ncbi.nlm.nih.gov/87654321/",
                study_type="rct",
                sample_size=180,
                peer_reviewed=True,
                quality_score=0.78
            )
        ]
        
        return mock_papers
    
    def _search_pmids(self, query: str, max_results: int) -> List[str]:
        """Search for PubMed IDs using the query"""
        search_url = f"{self.base_url}/esearch.fcgi"
        
        # Simplified query - remove complex filters for now
        # enhanced_query = f"{query} AND (systematic review[pt] OR meta analysis[pt] OR randomized controlled trial[pt] OR clinical trial[pt])"
        
        params = {
            "db": "pubmed",
            "term": query,  # Use simple query first
            "retmax": max_results,
            "retmode": "xml",
            "sort": "relevance",
            "tool": "aspartame_ai",
            "email": self.email
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            print(f"PubMed search status: {response.status_code}")  # Debug
            
            if response.status_code != 200:
                print(f"PubMed API error: {response.status_code}")
                return []
            
            # Parse XML response
            root = ET.fromstring(response.content)
            pmids = [id_elem.text for id_elem in root.findall(".//Id")]
            print(f"Found {len(pmids)} PMIDs for '{query}'")  # Debug
            
            return pmids
            
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []
    
    def _fetch_paper_details(self, pmids: List[str]) -> List[AcademicPaper]:
        """Fetch detailed information for given PMIDs"""
        if not pmids:
            return []
        
        fetch_url = f"{self.base_url}/efetch.fcgi"
        
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "tool": "aspartame_ai",
            "email": self.email
        }
        
        try:
            print(f"🔄 Fetching details for PMIDs: {pmids}")
            response = requests.get(fetch_url, params=params, timeout=15)
            print(f"📡 Fetch response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Fetch failed with status {response.status_code}")
                return []
            
            papers = []
            
            root = ET.fromstring(response.content)
            articles = root.findall(".//PubmedArticle")
            print(f"📄 Found {len(articles)} articles to parse")
            
            for i, article in enumerate(articles):
                try:
                    paper = self._parse_paper_xml(article)
                    if paper:
                        papers.append(paper)
                        print(f"✅ Parsed paper {i+1}: {paper.title[:50]}...")
                    else:
                        print(f"⚠️ Failed to parse paper {i+1}")
                except Exception as e:
                    print(f"❌ Error parsing paper {i+1}: {e}")
                    continue
                        
            print(f"✅ Successfully parsed {len(papers)} papers")
            return papers
            
        except ET.ParseError as e:
            print(f"❌ XML parsing error: {e}")
            return []
        except Exception as e:
            print(f"❌ Fetch error: {e}")
            return []
    
    def _parse_paper_xml(self, article_xml) -> Optional[AcademicPaper]:
        """Parse individual paper XML into AcademicPaper object"""
        try:
            # Extract PMID
            pmid_elem = article_xml.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else None
            
            # Extract title
            title_elem = article_xml.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else "No title"
            
            # Extract abstract
            abstract_elem = article_xml.find(".//AbstractText")
            abstract = abstract_elem.text if abstract_elem is not None else ""
            
            # Extract authors
            authors = []
            for author in article_xml.findall(".//Author"):
                last_name = author.find("LastName")
                first_name = author.find("ForeName")
                if last_name is not None and first_name is not None:
                    authors.append(f"{first_name.text} {last_name.text}")
            
            # Extract journal
            journal_elem = article_xml.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else "Unknown Journal"
            
            # Extract publication date
            year_elem = article_xml.find(".//PubDate/Year")
            month_elem = article_xml.find(".//PubDate/Month")
            pub_date = ""
            if year_elem is not None:
                pub_date = year_elem.text
                if month_elem is not None:
                    pub_date = f"{month_elem.text} {pub_date}"
            
            # Extract DOI
            doi = None
            for id_elem in article_xml.findall(".//ArticleId"):
                if id_elem.get("IdType") == "doi":
                    doi = id_elem.text
                    break
            
            # Build URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
            
            # Extract study type from title/abstract
            study_type = self._classify_study_type(title, abstract)
            
            # Extract sample size
            sample_size = self._extract_sample_size(abstract)
            
            # Check for funding/conflicts
            funding_source = self._extract_funding(article_xml)
            conflicts_disclosed = self._check_conflicts_disclosed(article_xml)
            
            return AcademicPaper(
                title=title,
                authors=authors,
                abstract=abstract,
                publication_date=pub_date,
                journal=journal,
                pmid=pmid,
                doi=doi,
                url=url,
                study_type=study_type,
                sample_size=sample_size,
                peer_reviewed=True,  # PubMed is peer-reviewed
                conflicts_disclosed=conflicts_disclosed,
                funding_source=funding_source
            )
            
        except Exception as e:
            print(f"Error parsing paper: {e}")
            return None
    
    def _classify_study_type(self, title: str, abstract: str) -> str:
        """Classify the type of study based on title and abstract"""
        text = f"{title} {abstract}".lower()
        
        if any(term in text for term in ["meta-analysis", "meta analysis", "systematic review"]):
            return "meta-analysis"
        elif any(term in text for term in ["randomized controlled trial", "rct", "randomized"]):
            return "rct"
        elif any(term in text for term in ["cohort study", "longitudinal", "prospective"]):
            return "cohort"
        elif any(term in text for term in ["case-control", "case control"]):
            return "case-control"
        elif any(term in text for term in ["cross-sectional", "survey"]):
            return "cross-sectional"
        elif any(term in text for term in ["review", "narrative review"]):
            return "review"
        else:
            return "observational"
    
    def _extract_sample_size(self, abstract: str) -> Optional[int]:
        """Extract sample size from abstract"""
        if not abstract:
            return None
        
        # Look for patterns like "n=123", "N=123", "123 patients", "123 subjects"
        patterns = [
            r'[nN]\s*=\s*(\d+)',
            r'(\d+)\s+(?:patients|subjects|participants|individuals|people)',
            r'total\s+of\s+(\d+)',
            r'sample\s+size\s+of\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, abstract)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _extract_funding(self, article_xml) -> str:
        """Extract funding information"""
        grants = article_xml.findall(".//Grant")
        if grants:
            agencies = []
            for grant in grants:
                agency = grant.find("Agency")
                if agency is not None and agency.text:
                    agencies.append(agency.text)
            return ", ".join(agencies) if agencies else "Grant funded"
        return ""
    
    def _check_conflicts_disclosed(self, article_xml) -> bool:
        """Check if conflicts of interest are disclosed"""
        # Look for conflict disclosure sections
        for text_elem in article_xml.findall(".//AbstractText"):
            if text_elem.get("Label") and "conflict" in text_elem.get("Label").lower():
                return True
        return False
    
    def _assess_paper_quality(self, paper: AcademicPaper) -> float:
        """Assess overall quality score (0-1) based on multiple factors"""
        score = 0.0
        
        # Study type scoring (higher for more rigorous designs)
        type_scores = {
            "meta-analysis": 1.0,
            "rct": 0.9,
            "cohort": 0.7,
            "case-control": 0.6,
            "cross-sectional": 0.4,
            "review": 0.3,
            "observational": 0.5
        }
        score += type_scores.get(paper.study_type, 0.3) * 0.4
        
        # Sample size scoring
        if paper.sample_size:
            if paper.sample_size >= 1000:
                score += 0.3
            elif paper.sample_size >= 100:
                score += 0.2
            elif paper.sample_size >= 50:
                score += 0.1
        
        # Journal quality (simplified - in real version you'd use impact factors)
        high_impact_journals = [
            "new england journal of medicine", "lancet", "jama", "bmj", 
            "nature", "science", "cochrane"
        ]
        if any(journal.lower() in paper.journal.lower() for journal in high_impact_journals):
            score += 0.2
        
        # Recent publication bonus
        try:
            if paper.publication_date and len(paper.publication_date) >= 4:
                year = int(paper.publication_date[-4:])
                current_year = datetime.now().year
                if current_year - year <= 5:  # Within 5 years
                    score += 0.1
        except (ValueError, IndexError):
            pass
        
        # Conflict disclosure bonus
        if paper.conflicts_disclosed:
            score += 0.05
        
        return min(1.0, score)

class ArXivSearcher:
    """Search arXiv for preprints and early research"""
    
    def search_papers(self, query: str, max_results: int = 5) -> List[AcademicPaper]:
        """Search arXiv for papers"""
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            return self._parse_arxiv_response(response.content)
            
        except Exception as e:
            print(f"arXiv search error: {e}")
            return []
    
    def _parse_arxiv_response(self, xml_content: bytes) -> List[AcademicPaper]:
        """Parse arXiv XML response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Handle namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            for entry in root.findall('atom:entry', namespaces):
                title_elem = entry.find('atom:title', namespaces)
                title = title_elem.text.strip() if title_elem is not None else "No title"
                
                summary_elem = entry.find('atom:summary', namespaces)
                abstract = summary_elem.text.strip() if summary_elem is not None else ""
                
                # Extract authors
                authors = []
                for author in entry.findall('atom:author', namespaces):
                    name_elem = author.find('atom:name', namespaces)
                    if name_elem is not None:
                        authors.append(name_elem.text)
                
                # Extract publication date
                published_elem = entry.find('atom:published', namespaces)
                pub_date = published_elem.text[:10] if published_elem is not None else ""
                
                # Extract URL
                url_elem = entry.find('atom:id', namespaces)
                url = url_elem.text if url_elem is not None else ""
                
                paper = AcademicPaper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    publication_date=pub_date,
                    journal="arXiv preprint",
                    url=url,
                    study_type="preprint",
                    peer_reviewed=False,  # arXiv is not peer-reviewed
                    quality_score=0.3  # Lower score for preprints
                )
                
                papers.append(paper)
                
        except ET.ParseError as e:
            print(f"arXiv XML parsing error: {e}")
        
        return papers

# Usage example
if __name__ == "__main__":
    pubmed = PubMedSearcher()
    papers = pubmed.search_papers("aspartame safety health effects", max_results=5)
    
    for paper in papers:
        print(f"Title: {paper.title}")
        print(f"Journal: {paper.journal}")
        print(f"Quality Score: {paper.quality_score:.2f}")
        print(f"Study Type: {paper.study_type}")
        print("---")