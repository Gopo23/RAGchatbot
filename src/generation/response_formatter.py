def format_final_response(response_text: str, citations: list[dict]) -> str:
    """
    Appends the citation links and last updated footers to the response text.
    """
    if not citations:
        return response_text
        
    formatted_citations = []
    # Deduplicate citations just in case
    seen = set()
    
    for citation in citations:
        source_url = citation.get('source_url', '')
        fund_name = citation.get('fund_name', 'Source')
        last_updated = citation.get('last_updated', '')
        
        cite_str = f"- [{fund_name}]({source_url})"
        if last_updated:
            cite_str += f" (Last Updated: {last_updated})"
            
        if cite_str not in seen:
            seen.add(cite_str)
            formatted_citations.append(cite_str)
        
    if formatted_citations:
        citations_section = "\n\n**Sources:**\n" + "\n".join(formatted_citations)
        return response_text + citations_section
        
    return response_text
