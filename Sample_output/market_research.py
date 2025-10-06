from datetime import datetime

market_research = f"""
# [Business Idea Name] - Live Market Analysis Report
        *Generated on: {datetime.now().strftime('%B %d, %Y')} using real-time web search*

        ## 1. Executive Summary
        [5-7 sentences with key findings from web search, market opportunity, and competitive landscape overview]

        ## 2. Live Competitor Analysis
        ### Direct Competitors (From Web Search)
        | Company | Key Features | Market Position | Recent Developments | Source URL |
        |---------|-------------|----------------|-------------------|------------|
        [Table with 5-8 competitors found via web search]

        ### Competitive Landscape Insights
        [Key findings from competitor web search with source citations]

        ## 3. Current Market Size & Growth (Web Search Data)
        ### Market Metrics (Latest Available)
        - **Total Addressable Market (TAM):** [Amount with web source]
        - **Serviceable Addressable Market (SAM):** [Amount with web source]
        - **Market Growth Rate (CAGR):** [Percentage with web source]

        ### Market Segments Analysis
        [Based on web search results]

        ## 4. Latest Industry Trends 
        ### Emerging Trends (From Web Search)
        [List 5-7 key trends with web source citations]

        ### Recent Market Developments
        [Latest news and developments from web search]

        ## 5. Strategic Positioning Recommendations
        ### Market Opportunities Identified
        [Based on web search gap analysis]

        ### Competitive Differentiation
        [Recommendations based on competitor web search]

        ## 6. Recent News & Funding Activity
        ### Industry Developments
        [Latest news from web search]

        ### Investment Trends
        [Funding patterns from web search]

        ## 7. Data Sources & Citations
        [List all web sources used with URLs]

        ---

        **FOLLOW-UP QUESTION:**
        "Based on this live market research, would you like me to:
        1. Deep dive into specific competitors found?
        2. Perform a SWOT analysis using this web data?
        3. Generate feature recommendations based on market gaps?
        4. Research specific geographic markets?"
"""