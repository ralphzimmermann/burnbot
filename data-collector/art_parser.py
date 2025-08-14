#!/usr/bin/env python3
"""
Art parser utilities for extracting Burning Man artwork directory data.

This module provides functions to:
- Extract artwork detail links from index pages
- Extract artwork fields (name, location, description) from detail pages

The parser favors resilient, label-based extraction with multiple fallbacks,
as the directory HTML can change subtly year-to-year.
"""

import re
from bs4 import BeautifulSoup
from typing import List, Dict


def extract_art_links_from_index(html_content: str, base_url: str = "https://directory.burningman.org") -> List[str]:
    """
    Extract absolute artwork detail page URLs from an index page.

    Args:
        html_content: HTML content of the directory index page
        base_url: Base URL to resolve relative links

    Returns:
        List of absolute artwork detail page URLs
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    art_links: List[str] = []

    # Find anchors linking to /artwork/<id>/
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Accept both with and without trailing slash and optional query string
        if re.search(r"^/artwork/\d+/?(?:[?#].*)?$", href):
            # Normalize and build absolute URL
            # Remove any query/fragment for canonical detail URL
            canonical = re.sub(r"[?#].*$", "", href)
            if not canonical.endswith('/'):
                canonical += '/'
            # Ensure absolute
            if canonical.startswith('http'):
                abs_url = canonical
            else:
                abs_url = base_url.rstrip('/') + canonical

            art_links.append(abs_url)

    # De-duplicate while preserving order
    seen = set()
    unique_links: List[str] = []
    for url in art_links:
        if url not in seen:
            seen.add(url)
            unique_links.append(url)

    return unique_links


def _find_text_after_label(soup: BeautifulSoup, label_text: str) -> str:
    """
    Find text value that follows a given label (e.g., "Location:").

    This function searches for any element whose text contains the label
    (case-insensitive), then returns the text of the nearest following sibling
    or the remaining text in that container after the label.
    """
    # Case-insensitive match for label (with optional trailing whitespace)
    label_regex = re.compile(rf"^{re.escape(label_text)}\s*", re.IGNORECASE)

    # Strategy 1: Direct text node that starts with label
    for text_node in soup.find_all(string=label_regex):
        # Try to extract the tail (text after the label) on the same node
        full_text = text_node.strip()
        value = label_regex.sub("", full_text).strip()
        if value:
            return value

        # Else try next siblings' text
        parent = text_node.parent
        # Gather text from following siblings within the same container
        collected: List[str] = []
        for sib in parent.next_siblings:
            # Stop if we encounter another labeled section
            sib_text = getattr(sib, 'get_text', lambda **_: str(sib))().strip()
            if re.match(r"^(Website|Location|Description|Artwork)\s*:?", sib_text, re.IGNORECASE):
                break
            if sib_text:
                collected.append(sib_text)
        if collected:
            return " ".join(collected).strip()

    # Strategy 2: Find an element that contains the label and then
    # look for a following sibling element's text
    container = soup.find(lambda tag: tag.get_text(strip=True).lower().startswith(label_text.lower()))
    if container:
        # Remove the label from the container's text
        container_text = container.get_text(" ", strip=True)
        value = re.sub(label_regex, "", container_text).strip()
        if value:
            return value

        # Or take the next sibling's text
        next_sib = container.find_next_sibling()
        if next_sib:
            return next_sib.get_text(" ", strip=True)

    return ""


def extract_art_data(html_content: str, detail_url: str) -> Dict[str, str]:
    """
    Extract artwork data from an artwork detail page.

    Args:
        html_content: HTML content of the artwork detail page
        detail_url: The absolute URL of the artwork detail page (for context if needed)

    Returns:
        Dictionary with keys: name, location, description
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Name: prefer heading that starts with "Artwork:"; otherwise, first h1/h2
    name = ""
    for tag_name in ['h1', 'h2']:
        for h in soup.find_all(tag_name):
            text = h.get_text(" ", strip=True)
            if text:
                # Remove "Artwork:" prefix if present
                if text.lower().startswith('artwork:'):
                    candidate = text.split(':', 1)[1].strip()
                else:
                    candidate = text
                name = candidate
                break
        if name:
            break

    if not name:
        # Fallback: search for direct text pattern
        match = soup.find(string=re.compile(r"^\s*Artwork:\s*(.+)$", re.IGNORECASE))
        if match:
            name = re.sub(r"^\s*Artwork:\s*", "", str(match)).strip()

    # Location
    location = _find_text_after_label(soup, "Location:")

    # Description: attempt to capture text after a Description label
    description = ""
    desc_label = soup.find(string=re.compile(r"^\s*Description\s*:?", re.IGNORECASE))
    if desc_label:
        collected: List[str] = []
        parent = desc_label.parent
        # Prefer the next sibling block's text
        next_block = parent.find_next_sibling()
        if next_block:
            text = next_block.get_text(" ", strip=True)
            collected.append(text)
        else:
            # Fallback: remaining text in the same container after the label
            container_text = parent.get_text(" ", strip=True)
            container_text = re.sub(r"^\s*Description\s*:?\s*", "", container_text, flags=re.IGNORECASE)
            if container_text:
                collected.append(container_text)
        description = " ".join([t for t in collected if t]).strip()

    if not description:
        # Fallback: try meta description if available
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            description = meta['content'].strip()

    return {
        "name": name,
        "location": location,
        "description": description,
    }


__all__ = [
	"extract_art_links_from_index",
	"extract_art_data",
]



