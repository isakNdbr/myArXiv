"""
Adapted from http://arxiv.org/help/api/examples/python_arXiv_parsing_example.txt, https://github.com/mpi-astronomy/XarXiv

with modifications by Alex Breitweiser and enhanced HTML styling
"""

######## ---------------------------------- ########
####################################################
base_cat = "astro-ph.*"
cross_cats = {"cs.LG", # Machine Learning
              "cs.AI",  # AI
              "stat.*", # all of stats 
              "astro-ph.GA", # Galaxy Astrophysics
              "astro-ph.SR"
              #"physics.data-an" # Data Analysis in Physics
              }
# buzzwords for the abstract filtering
buzzwords = {
    "star formation", 
    "ScoCen", "Local Bubble", "Radcliffe Wave", 
    "stellar association", "stellar cluster", "open cluster",
    "tracebacks", "ISM", 
    "dust mapping", "dust extinction", "molecular cloud",
    
    # DS and Methods
    #"machine learning", "neural network", 
    "HDBSCAN", "bayesian model", "gaussian mixture model", "information field theory",
}

exclude_keywords = {
    "exoplanet", "exoplanets", "planet", "planetary", 
    "agn", "active galactic nuclei", "active galactic nucleus",
    "gravitational wave", "gravitational waves", "ligo", "virgo",
    "black hole", "neutron star", "pulsar",
    "cosmology", "dark matter", "dark energy",
    "galaxy formation", "galaxy evolution", 'cosmic reionization', 'galaxy merger',
    "astroseismology",
}

######## ---------------------------------- ########
####################################################


import urllib.request, urllib.parse, urllib.error
import feedparser
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Base api query url
base_url = 'http://export.arxiv.org/api/query?';

# Search parameters
today = date.today()
yesterday = date.today() - timedelta(1)
dby = yesterday - timedelta(5)
oneweek_ago = date.today() - timedelta(7)
threedays_ago = date.today() - timedelta(3)

start_date = dby.strftime("%Y%m%d")+"2000"
end_date = today.strftime("%Y%m%d") + "2000"

search_query = 'cat:%s+AND+lastUpdatedDate:[%s+TO+%s]' % (base_cat,
                              start_date,
                              end_date)
start = 0                    
max_results = 10_000

query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                     start,
                                                     max_results)
print(query)

# Opensearch metadata such as totalResults, startIndex, 
# and itemsPerPage live in the opensearch namespase.
# Some entry metadata lives in the arXiv namespace.
# This is a hack to expose both of these namespaces in
# feedparser v4.1
feedparser.mixin._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
feedparser.mixin._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

# perform a GET request using the base_url and query
response = urllib.request.urlopen(base_url+query).read()

# parse the response using feedparser
feed = feedparser.parse(response)

title = f"New {base_cat} submissions cross listed on {', '.join(cross_cats)} from {oneweek_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"

# Prepare HTML content
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #ffffff;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: #ffffff;
        }}
        
        .header {{
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 30px;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 2rem;
            font-weight: 400;
            margin-bottom: 8px;
            color: #000;
        }}
        
        .header .subtitle {{
            font-size: 0.9rem;
            color: #666;
            font-weight: 400;
        }}
        
        .content {{
            padding: 0;
        }}
        
        .paper-card {{
            margin-bottom: 50px;
            padding-bottom: 50px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .paper-card:last-child {{
            border-bottom: none;
        }}
        
        .paper-title {{
            font-size: 1.3rem;
            font-weight: 500;
            color: #000;
            text-decoration: none;
            display: block;
            margin-bottom: 20px;
            transition: color 0.2s ease;
        }}
        
        .paper-title:hover {{
            color: #666;
        }}
        
        .paper-body {{
            padding: 0;
        }}
        
        .paper-meta {{
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .meta-item {{
            display: flex;
            flex-direction: row;
            align-items: baseline;
            gap: 15px;
        }}
        
        .meta-label {{
            font-weight: 500;
            color: #666;
            font-size: 0.9rem;
            min-width: 120px;
            flex-shrink: 0;
        }}
        
        .meta-value {{
            color: #000;
            font-size: 0.9rem;
            flex: 1;
        }}
        
        .categories {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .category-tag {{
            background: #f5f5f5;
            color: #333;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8rem;
            font-weight: 400;
        }}
        
        .primary-category {{
            background: #000;
            color: #fff;
        }}
        
        .abstract {{
            color: #333;
            margin-top: 25px;
            font-size: 0.95rem;
            line-height: 1.7;
        }}
        
        .footer {{
            border-top: 1px solid #e0e0e0;
            padding-top: 30px;
            margin-top: 40px;
            text-align: center;
            font-size: 0.85rem;
            color: #999;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}
        
        .no-results h2 {{
            font-size: 1.5rem;
            margin-bottom: 15px;
            font-weight: 400;
            color: #000;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 20px 15px;
            }}
            
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .meta-item {{
                flex-direction: column;
                gap: 5px;
            }}
            
            .meta-label {{
                min-width: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Superb arXiv Selection 🐻 </h1>
            <div class="subtitle">Cross-listed {base_cat} submissions</div>
            <div class="subtitle">Feed last updated: {feed.feed.updated}</div>
        </div>
        
        <div class="content">
"""

paper_count = 0

# Run through each entry, and add to HTML
for entry in feed.entries:
    all_categories = [t['term'] for t in entry.tags]
    if not any(cat in cross_cats for cat in all_categories) or not any(buzzword in entry.summary.lower() for buzzword in buzzwords):
    #
        continue
    arxiv_id = entry.id.split('/abs/')[-1]
    if arxiv_id[-2:] != 'v1':
        continue

    # Filter out papers with excluded keywords in title or abstract
    title_abstract = (entry.title + " " + entry.summary).lower()
    if any(keyword.lower() in title_abstract for keyword in exclude_keywords):
        continue
    
    paper_count += 1
    pdf_link = ''
    for link in entry.links:
        if link.rel == 'alternate':
            continue
        elif link.title == 'pdf':
            pdf_link = link.href

    # Authors
    try:
        authors = ', '.join(author.name for author in entry.authors)
    except AttributeError:
        authors = 'Unknown'

    # Comment
    try:
        comment = entry.arxiv_comment
    except AttributeError:
        comment = 'No comment found'

    # Primary category
    primary_category = entry.tags[0]['term']

    # All categories
    all_categories = [t['term'] for t in entry.tags]
    
    html_content += f"""
            <div class="paper-card">
                <a href="{pdf_link}" class="paper-title" target="_blank">
                    {entry.title}
                </a>
                
                <div class="paper-body">
                    <div class="paper-meta">
                        <div class="meta-item">
                            <div class="meta-label">Authors</div>
                            <div class="meta-value">{authors}</div>
                        </div>
                        
                        <div class="meta-item">
                            <div class="meta-label">Comments</div>
                            <div class="meta-value">{comment}</div>
                        </div>
                        
                        <div class="meta-item">
                            <div class="meta-label">Primary</div>
                            <div class="meta-value">
                                <span class="category-tag primary-category">{primary_category}</span>
                            </div>
                        </div>
                        
                        <div class="meta-item">
                            <div class="meta-label">Categories</div>
                            <div class="categories">
                                {' '.join(f'<span class="category-tag">{cat}</span>' for cat in all_categories)}
                            </div>
                        </div>
                    </div>
                    
                    <div class="abstract">
                        {entry.summary}
                    </div>
                </div>
            </div>
    """

if paper_count == 0:
    html_content += """
            <div class="no-results">
                <h2>No Results Found</h2>
                <p>No papers found matching the cross-listing criteria for the specified date range.</p>
                <p>Try adjusting the date range or categories.</p>
            </div>
    """

html_content += f"""
        </div>
        
        <div class="footer">
            Generated on {today.strftime('%Y-%m-%d')} • Found {paper_count} papers • not affiliated with arXiv, just shenanigans with their API
        </div>
    </div>
</body>
</html>
"""

# Save to file
with open('arxiv_papers.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML file generated: arxiv_papers.html")
print(f"Found {paper_count} papers")
print(html_content)
