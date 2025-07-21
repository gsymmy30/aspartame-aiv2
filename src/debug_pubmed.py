"""
Debug PubMed integration to see what's happening
"""

import sys


from academic_tools import PubMedSearcher
import requests

def test_pubmed_direct():
    """Test PubMed API directly"""
    print("🔬 Testing PubMed API directly...")
    
    # Direct API test
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": "creatine supplementation safety",
        "retmax": 5,
        "retmode": "xml"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response length: {len(response.content)}")
        print(f"First 500 chars: {response.text[:500]}")
        
        if "pmid" in response.text.lower():
            print("✅ Found PMIDs in response!")
        else:
            print("❌ No PMIDs found")
            
    except Exception as e:
        print(f"❌ Direct API error: {e}")

def test_pubmed_searcher():
    """Test our PubMed searcher class"""
    print("\n🔬 Testing PubMed Searcher Class...")
    
    searcher = PubMedSearcher()
    
    # Test different queries
    queries = [
        "creatine supplementation safety",
        "creatine monohydrate health effects", 
        "creatine",
        "creatine AND safety"
    ]
    
    for query in queries:
        print(f"\n📝 Testing query: '{query}'")
        try:
            papers = searcher.search_papers(query, max_results=3)
            print(f"   Found {len(papers)} papers")
            
            for i, paper in enumerate(papers[:2]):
                print(f"   Paper {i+1}: {paper.title[:60]}...")
                print(f"   Journal: {paper.journal}")
                print(f"   PMID: {paper.pmid}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_search_step_by_step():
    """Test each step of the search process"""
    print("\n🔬 Testing Search Step by Step...")
    
    searcher = PubMedSearcher()
    query = "creatine supplementation"
    
    # Step 1: Search for PMIDs
    print("Step 1: Searching for PMIDs...")
    try:
        pmids = searcher._search_pmids(query, 5)
        print(f"Found PMIDs: {pmids}")
        
        if pmids:
            # Step 2: Fetch details
            print("Step 2: Fetching paper details...")
            papers = searcher._fetch_paper_details(pmids[:2])
            print(f"Got {len(papers)} papers with details")
            
            for paper in papers:
                print(f"- {paper.title}")
                print(f"  Quality: {paper.quality_score}")
        else:
            print("❌ No PMIDs found!")
            
    except Exception as e:
        print(f"❌ Error in step-by-step: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting PubMed Debug Session\n")
    
    test_pubmed_direct()
    test_pubmed_searcher() 
    test_search_step_by_step()
    
    print("\n✅ Debug session complete!")