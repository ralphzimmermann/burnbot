#!/usr/bin/env python3
"""
Camp parser utilities for extracting Burning Man camp directory data.

This module provides functions to:
- Extract camp detail links from index pages
- Extract camp fields (name, website, location, description) from detail pages

The parser favors resilient, label-based extraction with multiple fallbacks,
as the directory HTML can change subtly year-to-year.
"""

import re
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Optional


def extract_camp_links_from_index(html_content: str, base_url: str = "https://directory.burningman.org") -> List[str]:
    """
    Extract absolute camp detail page URLs from an index page.

    Args:
        html_content: HTML content of the directory index page
        base_url: Base URL to resolve relative links

    Returns:
        List of absolute camp detail page URLs
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    camp_links: List[str] = []

    # Find anchors linking to /camps/<id>/
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Accept both with and without trailing slash and optional query string
        if re.search(r"^/camps/\d+/?(?:[?#].*)?$", href):
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

            camp_links.append(abs_url)

    # De-duplicate while preserving order
    seen = set()
    unique_links: List[str] = []
    for url in camp_links:
        if url not in seen:
            seen.add(url)
            unique_links.append(url)

    return unique_links


def _clip_at_next_label(text: str) -> str:
    """Clip a value string at the start of the next known label."""
    if not text:
        return ""
    parts = re.split(r"\b(?:Website|Location|Description|Camp Events)\s*:", text, maxsplit=1, flags=re.IGNORECASE)
    return parts[0].strip()


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
        value = _clip_at_next_label(value)
        if value:
            return value

        # Else try next siblings' text
        parent = text_node.parent
        # Gather text from following siblings within the same container
        collected: List[str] = []
        for sib in parent.next_siblings:
            # Stop if we encounter another labeled section
            sib_text = getattr(sib, 'get_text', lambda **_: str(sib))().strip()
            if re.match(r"^(Website|Location|Description)\s*:?", sib_text, re.IGNORECASE):
                break
            if sib_text:
                collected.append(sib_text)
        if collected:
            return _clip_at_next_label(" ".join(collected).strip())

    # Strategy 2: Find an element that contains the label and then
    # look for a following sibling element's text
    container = soup.find(lambda tag: tag.get_text(strip=True).lower().startswith(label_text.lower()))
    if container:
        # Remove the label from the container's text
        container_text = container.get_text(" ", strip=True)
        value = re.sub(label_regex, "", container_text).strip()
        value = _clip_at_next_label(value)
        if value:
            return value

        # Or take the next sibling's text
        next_sib = container.find_next_sibling()
        if next_sib:
            return _clip_at_next_label(next_sib.get_text(" ", strip=True))

    return ""


def extract_camp_data(html_content: str, detail_url: str) -> Dict[str, str]:
    """
    Extract camp data from a camp detail page.

    Args:
        html_content: HTML content of the camp detail page
        detail_url: The absolute URL of the camp detail page (used for context)

    Returns:
        Dictionary with keys: name, website, location, description
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Name: prefer heading that starts with "Camp:"; otherwise, first h1/h2
    name = ""
    for tag_name in ['h1', 'h2']:
        for h in soup.find_all(tag_name):
            text = h.get_text(" ", strip=True)
            if text:
                # Remove "Camp:" prefix if present
                if text.lower().startswith('camp:'):
                    candidate = text.split(':', 1)[1].strip()
                else:
                    candidate = text
                # Heuristic: pick the first plausible heading
                name = candidate
                break
        if name:
            break

    if not name:
        # Fallback: search for a text that starts with "Camp: "
        match = soup.find(string=re.compile(r"^\s*Camp:\s*(.+)$", re.IGNORECASE))
        if match:
            name = re.sub(r"^\s*Camp:\s*", "", str(match)).strip()

    # Website: look for a labeled section or the first external URL in context
    website = ""
    # Prefer anchor near the Website label
    website_label = soup.find(string=re.compile(r"^\s*Website\s*:?\s*$", re.IGNORECASE)) or \
                    soup.find(string=re.compile(r"Website\s*:?", re.IGNORECASE))
    if website_label:
        # First look for a link in the same parent/container
        parent = website_label.parent
        link = parent.find('a', href=True) if parent else None
        if link and re.match(r"^https?://", link.get('href', '')):
            website = link['href']
        else:
            # Look ahead through siblings until another label appears
            collected_links: List[str] = []
            for sib in parent.next_siblings if parent else []:
                sib_text = getattr(sib, 'get_text', lambda **_: str(sib))().strip()
                if re.match(r"^(Website|Location|Description)\s*:", sib_text, re.IGNORECASE):
                    break
                a = sib.find('a', href=True) if isinstance(sib, Tag) else None
                if a and re.match(r"^https?://", a.get('href', '')):
                    collected_links.append(a['href'])
            if collected_links:
                website = collected_links[0]

    if not website:
        # Fallback to label text and extract first URL
        value = _find_text_after_label(soup, "Website:")
        m = re.search(r"https?://\S+", value)
        if m:
            website = m.group(0)
        elif value:
            website = value
    if not website:
        # Last resort: first external link on the page
        ext_link = soup.find('a', href=re.compile(r"^https?://"))
        if ext_link:
            website = ext_link['href']

    # Location
    location = _find_text_after_label(soup, "Location:")

    # Description: attempt to capture text after a Description label
    description = ""
    # Try label-based extraction first
    desc_label = soup.find(string=re.compile(r"^\s*Description\s*:?", re.IGNORECASE))
    if desc_label:
        # Collect text from following siblings until the next labeled section
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
        "website": website,
        "location": location,
        "description": description,
    }


__all__ = [
    "extract_camp_links_from_index",
    "extract_camp_data",
]


