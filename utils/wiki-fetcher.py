import csv
import requests
from bs4 import BeautifulSoup
import time
import os
import json
import re

def read_kpop_groups(csv_path):
    """Read the K-pop group names from CSV file."""
    groups = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            group_data = {
                'english': row['group (english)'],
                'korean': row['group (korean)'],
                'alternative': row.get('group (alternative)', '')  # Get alternative name if exists
            }
            groups.append(group_data)
    return groups

def fetch_wikipedia_content(group_name_english, group_name_alternative, group_name_korean):
    """Fetch the Wikipedia page for a given group name, trying English first, 
    then alternative (if available), then Korean."""
    
    # Try with English name first
    url_name = group_name_english.replace(' ', '_')
    url = f"https://en.wikipedia.org/wiki/{url_name}"
    
    try:
        response = requests.get(url)
        # If the page exists, return the content
        if response.status_code == 200:
            return response.text, 'english', url
        
        # If English name fails and alternative name exists, try with alternative name
        if group_name_alternative:
            url_name_alt = group_name_alternative.replace(' ', '_')
            url_alt = f"https://en.wikipedia.org/wiki/{url_name_alt}"
            
            response_alt = requests.get(url_alt)
            if response_alt.status_code == 200:
                return response_alt.text, 'alternative', url_alt
        
        # If both English and alternative (if available) fail, try with Korean name
        url_name_korean = group_name_korean.replace(' ', '_')
        url_korean = f"https://en.wikipedia.org/wiki/{url_name_korean}"
        
        response_korean = requests.get(url_korean)
        if response_korean.status_code == 200:
            return response_korean.text, 'korean', url_korean
        
        # If all fail, raise the exception for the English URL
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url} or alternatives: {e}")
        return None, None, None

def extract_group_info(html_content, group_name):
    """Extract the group information from Wikipedia HTML content.
    Gets all text between the infobox and the table of contents."""
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the main content div
    content_div = soup.find('div', {'id': 'mw-content-text'})
    
    if not content_div:
        return None
    
    # Find first article content div
    article_div = content_div.find('div', {'class': 'mw-parser-output'})
    if not article_div:
        return None
    
    # Find the infobox table
    infobox = article_div.find('table', {'class': 'infobox'})
    if not infobox:
        # If no infobox, just return the first paragraphs
        paragraphs = article_div.find_all('p', limit=3)
        return [p.get_text(strip=True) for p in paragraphs if p.text.strip()]
    
    # Find the table of contents or the first heading (which usually comes after intro)
    toc = article_div.find('meta', {'property': 'mw:PageProp/toc'})
    first_heading = article_div.find('h2')
    
    # All elements between infobox and TOC/first heading are part of the introduction
    intro_elements = []
    current = infobox.find_next_sibling()
    
    end_element = toc if toc else first_heading
    
    while current and current != end_element:
        # Only collect paragraph elements
        if current.name == 'p' and current.text.strip():
            intro_elements.append(current.get_text(strip=True))
        current = current.next_sibling
    
    # If we didn't find any paragraphs, look for paragraphs that might be after a hatnote or other elements
    if not intro_elements:
        # Try to find the first few paragraphs in the article
        for p in article_div.find_all('p'):
            if p.text.strip():
                intro_elements.append(p.get_text(strip=True))
                if len(intro_elements) >= 3:  # Limit to 3 paragraphs
                    break
    
    return intro_elements

def main():
    # Create output directory if it doesn't exist
    output_dir = "wikipedia_data"
    os.makedirs(output_dir, exist_ok=True)
    
    csv_path = "data-original/kpop-group.csv"
    groups = read_kpop_groups(csv_path)
    
    results = {}
    stats = {'english': 0, 'alternative': 0, 'korean': 0, 'failed': 0}
    
    for group in groups:
        english_name = group['english']
        alternative_name = group['alternative']
        korean_name = group['korean']
        
        print(f"Fetching info for {english_name}...")
        if alternative_name:
            print(f"  Alternative name: {alternative_name}")
            
        html_content, used_name, url_used = fetch_wikipedia_content(english_name, alternative_name, korean_name)
        
        if html_content:
            group_info = extract_group_info(html_content, english_name)
            results[english_name] = {
                'info': group_info,
                'name_used': used_name,
                'url': url_used
            }
            
            # Update stats
            stats[used_name] += 1
            
            # Save the raw HTML for debugging/reference
            with open(f"{output_dir}/{english_name.replace(' ', '_')}_wiki.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
        else:
            # Update failed stats
            stats['failed'] += 1
            results[english_name] = {
                'info': None,
                'name_used': None,
                'url': None
            }
        
        # Be respectful to Wikipedia's servers
        time.sleep(1)
    
    # Save all the extracted info to a JSON file
    with open(f"{output_dir}/kpop_group_info.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Completed! Data saved to {output_dir}")
    print(f"Stats: {stats['english']} found with English name, {stats['alternative']} with alternative name, {stats['korean']} with Korean name, {stats['failed']} failed")

if __name__ == "__main__":
    main()
