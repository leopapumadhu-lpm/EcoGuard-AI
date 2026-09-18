# =============================================================================
# EcoGuard AI - Climate News Page
# =============================================================================
# Live climate and environmental news from NASA and NOAA
# =============================================================================

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests
import streamlit as st

from utils.ui_components import page_header, section_divider, footer


# =============================================================================
# Page Configuration
# =============================================================================

PAGE_TITLE = "Climate News"

PAGE_SUBTITLE = (
    "Live climate, environmental and sustainability news "
    "from trusted scientific sources."
)


NEWS_FEEDS = {
    "NASA": [
        "https://www.nasa.gov/rss/dyn/earth.rss",
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    ],
    "NOAA": [
        "https://www.noaa.gov/rss.xml",
    ],
}


# =============================================================================
# Keywords
# =============================================================================

CLIMATE_KEYWORDS = [
    # General climate
    "climate",
    "climate change",
    "global warming",
    "greenhouse gas",
    "greenhouse gases",
    "emissions",
    "carbon emissions",
    "carbon emission",
    "methane",
    "nitrous oxide",
    "carbon dioxide",
    "co2",
    "net zero",
    "climate risk",
    "climate resilience",
    "climate adaptation",
    "climate mitigation",
    "climate science",
    "climate policy",
    "climate action",
    "earth system",

    # Environment
    "environment",
    "environmental",
    "sustainability",
    "sustainable",
    "conservation",
    "pollution",
    "air quality",
    "water quality",
    "land degradation",

    # Oil and chemical pollution
    "oil spill",
    "oil spill response",
    "oil pollution",
    "petroleum pollution",
    "chemical spill",
    "hazardous spill",
    "spill response",
    "marine pollution",

    # Oceans and water
    "ocean",
    "ocean warming",
    "ocean temperature",
    "ocean heat",
    "ocean heat content",
    "ocean acidification",
    "marine",
    "sea level",
    "sea-level",
    "plastic pollution",
    "plastic waste",
    "coral reef",
    "coral reefs",
    "coastal",
    "coastline",

    # Ice and polar regions
    "glacier",
    "glaciers",
    "ice sheet",
    "ice sheets",
    "sea ice",
    "arctic",
    "antarctic",
    "antarctica",
    "polar ice",
    "ice melt",
    "ice melting",
    "snowpack",
    "permafrost",

    # Weather
    "heatwave",
    "heat wave",
    "extreme heat",
    "heavy rainfall",
    "extreme rainfall",
    "extreme weather",
    "flood",
    "flooding",
    "flood risk",
    "drought",
    "wildfire",
    "wildfires",
    "hurricane",
    "hurricanes",
    "cyclone",
    "cyclones",
    "tropical storm",
    "storm surge",
    "precipitation",
    "rainfall",
    "el niño",
    "el nino",
    "la niña",
    "la nina",

    # Biodiversity
    "biodiversity",
    "ecosystem",
    "ecosystems",
    "habitat",
    "habitats",
    "deforestation",
    "forest loss",
    "forest area",
    "reforestation",
    "afforestation",
    "wildlife",
    "wildlife conservation",
    "species conservation",
    "species",
    "marine ecosystems",
    "ocean ecosystems",

    # Renewable energy
    "renewable energy",
    "clean energy",
    "solar power",
    "solar energy",
    "wind power",
    "wind energy",
    "hydropower",
    "geothermal",
    "energy transition",
    "clean technology",
    "clean tech",
    "carbon capture",
    "carbon removal",
    "decarbonization",
    "decarbonisation",
]


EXCLUDED_KEYWORDS = [
    # Space and astronomy content
    "apod",
    "astronomy",
    "telescope",
    "galaxy",
    "nebula",
    "starfield",
    "black hole",
    "milky way",
    "artemis",
    "astronaut",
    "spacecraft",
    "rocket",
    "lunar",
    "moon mission",
    "mars mission",
    "planetary mission",

    # Non-news promotional or career content
    "football",
    "nfl",
    "scholarship",
    "job opportunity",
    "career",
    "recruitment",
    "hiring",
    "leadership",
    "administrator",
    "employee",
    "internship",
    "conference registration",
]


CATEGORY_KEYWORDS = {
    "Extreme Weather": [
        "heatwave",
        "heat wave",
        "extreme heat",
        "heavy rainfall",
        "extreme rainfall",
        "extreme weather",
        "flood",
        "flooding",
        "flood risk",
        "drought",
        "wildfire",
        "wildfires",
        "hurricane",
        "hurricanes",
        "cyclone",
        "cyclones",
        "tropical storm",
        "storm surge",
        "precipitation",
        "rainfall",
        "el niño",
        "el nino",
        "la niña",
        "la nina",
    ],
    "Ocean & Ice": [
        "sea level",
        "sea-level",
        "ocean warming",
        "ocean temperature",
        "ocean heat",
        "ocean heat content",
        "ocean acidification",
        "marine heatwave",
        "glacier",
        "glaciers",
        "ice sheet",
        "ice sheets",
        "sea ice",
        "arctic",
        "antarctic",
        "antarctica",
        "polar ice",
        "ice melt",
        "ice melting",
        "snowpack",
        "permafrost",
        "coastal",
        "coastline",
    ],
    "Biodiversity": [
        "biodiversity",
        "ecosystem",
        "ecosystems",
        "habitat",
        "habitats",
        "species",
        "deforestation",
        "forest loss",
        "forest area",
        "reforestation",
        "afforestation",
        "coral reef",
        "coral reefs",
        "wildlife",
        "wildlife conservation",
        "species conservation",
        "marine ecosystems",
        "ocean ecosystems",
    ],
    "Renewable Energy": [
        "renewable energy",
        "clean energy",
        "solar power",
        "solar energy",
        "wind power",
        "wind energy",
        "hydropower",
        "geothermal",
        "energy transition",
        "clean technology",
        "clean tech",
        "carbon capture",
        "carbon removal",
        "decarbonization",
        "decarbonisation",
        "net zero",
    ],
    "Sustainability": [
        "sustainability",
        "sustainable",
        "conservation",
        "pollution",
        "air quality",
        "water quality",
        "plastic pollution",
        "plastic waste",
        "oil spill",
        "oil spill response",
        "oil pollution",
        "petroleum pollution",
        "chemical spill",
        "hazardous spill",
        "spill response",
        "marine pollution",
        "land degradation",
        "environmental",
        "environment",
    ],
    "Climate Science": [
        "climate",
        "climate change",
        "global warming",
        "greenhouse gas",
        "greenhouse gases",
        "carbon emissions",
        "carbon emission",
        "emissions",
        "methane",
        "nitrous oxide",
        "carbon dioxide",
        "co2",
        "climate risk",
        "climate resilience",
        "climate adaptation",
        "climate mitigation",
        "climate science",
        "climate policy",
        "climate action",
        "earth system",
    ],
}


# =============================================================================
# HTTP Session
# =============================================================================

@st.cache_resource
def get_http_session():
    """
    Create one reusable HTTP session for feed requests.
    """
    session = requests.Session()

    session.headers.update(
        {
            "User-Agent": (
                "EcoGuard-AI/1.0 "
                "(Climate and Environmental News Reader)"
            )
        }
    )

    return session


# =============================================================================
# Text Helpers
# =============================================================================

def clean_text(value):
    """
    Convert HTML or XML text into clean readable text.
    """
    if value is None:
        return ""

    value = str(value)

    value = html.unescape(value)

    value = re.sub(r"<[^>]+>", " ", value)

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_text(value):
    """
    Normalize text for keyword matching.
    """
    return clean_text(value).lower()


def contains_keyword(text, keyword):
    """
    Check whether a keyword exists in text.
    """
    text = normalize_text(text)
    keyword = normalize_text(keyword)

    if not text or not keyword:
        return False

    return keyword in text


# =============================================================================
# Date Helpers
# =============================================================================

def parse_date(value):
    """
    Parse RSS date formats into a timezone-aware datetime.
    """
    if not value:
        return None

    value = clean_text(value)

    try:
        parsed = parsedate_to_datetime(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    except Exception:
        pass

    date_formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]

    for date_format in date_formats:
        try:
            parsed = datetime.strptime(value, date_format)

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc)

        except Exception:
            continue

    return None


def format_date(value):
    """
    Format article date for display.
    """
    parsed = parse_date(value)

    if parsed is None:
        return "Date unavailable"

    return parsed.strftime("%d %b %Y")


# =============================================================================
# XML Helpers
# =============================================================================

def get_element_text(element, names):
    """
    Return the first matching child element's text.
    """
    for name in names:
        child = element.find(name)

        if child is not None:
            text = "".join(child.itertext())

            if text.strip():
                return clean_text(text)

    return ""


def get_link(element):
    """
    Extract article link from RSS or Atom entry.
    """
    # Standard RSS link
    link_element = element.find("link")

    if link_element is not None:
        href = link_element.attrib.get("href")

        if href:
            return href.strip()

        if link_element.text:
            return link_element.text.strip()

    # Atom link
    for child in element:
        tag_name = child.tag.lower()

        if tag_name.endswith("link"):
            href = child.attrib.get("href")

            if href:
                return href.strip()

            if child.text:
                return child.text.strip()

    return ""


# =============================================================================
# Feed Parsing
# =============================================================================

def parse_feed(xml_content, source_name):
    """
    Parse RSS or Atom feed content.
    """
    articles = []

    try:
        root = ET.fromstring(xml_content)

    except ET.ParseError:
        return articles

    # RSS items
    rss_items = root.findall(".//item")

    # Atom entries
    atom_entries = [
        element
        for element in root.iter()
        if element.tag.lower().endswith("entry")
    ]

    feed_items = rss_items if rss_items else atom_entries

    for item in feed_items:
        title = get_element_text(
            item,
            [
                "title",
                "{http://www.w3.org/2005/Atom}title",
            ],
        )

        description = get_element_text(
            item,
            [
                "description",
                "summary",
                "content",
                "{http://www.w3.org/2005/Atom}summary",
                "{http://www.w3.org/2005/Atom}content",
            ],
        )

        link = get_link(item)

        date_value = get_element_text(
            item,
            [
                "pubDate",
                "published",
                "updated",
                "date",
                "{http://www.w3.org/2005/Atom}published",
                "{http://www.w3.org/2005/Atom}updated",
            ],
        )

        if not title or not link:
            continue

        articles.append(
            {
                "title": clean_text(title),
                "description": clean_text(description),
                "link": link.strip(),
                "date": date_value,
                "source": source_name,
            }
        )

    return articles


# =============================================================================
# Article Filtering
# =============================================================================

def get_excluded_matches(article):
    """
    Find excluded keywords in the article.
    """
    combined_text = " ".join(
        [
            article.get("title", ""),
            article.get("description", ""),
        ]
    )

    matches = []

    for keyword in EXCLUDED_KEYWORDS:
        if contains_keyword(combined_text, keyword):
            matches.append(keyword)

    return matches


def get_climate_matches(article):
    """
    Find climate-related keywords in the article.
    """
    title = article.get("title", "")
    description = article.get("description", "")

    title_matches = [
        keyword
        for keyword in CLIMATE_KEYWORDS
        if contains_keyword(title, keyword)
    ]

    description_matches = [
        keyword
        for keyword in CLIMATE_KEYWORDS
        if contains_keyword(description, keyword)
    ]

    return title_matches, description_matches


def is_relevant_climate_article(article):
    """
    Keep only climate, environment and sustainability-related articles.
    """
    excluded_matches = get_excluded_matches(article)

    if excluded_matches:
        return False

    title_matches, description_matches = get_climate_matches(article)

    # A climate keyword in the title is enough.
    if title_matches:
        return True

    # Otherwise require at least two unique description matches.
    unique_description_matches = set(description_matches)

    return len(unique_description_matches) >= 2


# =============================================================================
# Article Classification
# =============================================================================

def classify_article(article):
    """
    Classify an article into the most relevant category.

    Pollution and oil-spill stories are explicitly classified as
    Sustainability before general keyword scoring.
    """
    title = normalize_text(article.get("title", ""))
    description = normalize_text(article.get("description", ""))
    combined_text = f"{title} {description}"

    # Strong category override for pollution and spill-related stories.
    sustainability_priority_terms = [
        "oil spill",
        "oil spill response",
        "oil pollution",
        "petroleum pollution",
        "chemical spill",
        "hazardous spill",
        "spill response",
        "marine pollution",
        "plastic pollution",
        "plastic waste",
        "pollution",
        "water quality",
        "air quality",
    ]

    if any(
        contains_keyword(combined_text, keyword)
        for keyword in sustainability_priority_terms
    ):
        return "Sustainability"

    category_scores = {}

    category_priority = [
        "Extreme Weather",
        "Ocean & Ice",
        "Biodiversity",
        "Renewable Energy",
        "Sustainability",
        "Climate Science",
    ]

    for category in category_priority:
        score = 0

        for keyword in CATEGORY_KEYWORDS[category]:
            if contains_keyword(title, keyword):
                score += 5

            if contains_keyword(description, keyword):
                score += 1

        category_scores[category] = score

    best_category = max(
        category_scores,
        key=category_scores.get,
    )

    if category_scores[best_category] <= 0:
        return "Climate Science"

    return best_category


# =============================================================================
# Article Preparation
# =============================================================================

def prepare_article(article):
    """
    Clean and enrich an article.
    """
    prepared = {
        "title": clean_text(article.get("title", "")),
        "description": clean_text(article.get("description", "")),
        "link": article.get("link", "").strip(),
        "date": article.get("date", ""),
        "source": clean_text(article.get("source", "Unknown")),
    }

    prepared["category"] = classify_article(prepared)

    return prepared


def article_key(article):
    """
    Create a unique key for deduplication.
    """
    link = normalize_text(article.get("link", ""))

    if link:
        return link

    title = normalize_text(article.get("title", ""))

    return title


def deduplicate_articles(articles):
    """
    Remove duplicate articles.
    """
    unique_articles = []
    seen_keys = set()

    for article in articles:
        key = article_key(article)

        if not key or key in seen_keys:
            continue

        seen_keys.add(key)
        unique_articles.append(article)

    return unique_articles


def sort_articles(articles):
    """
    Sort newest articles first.
    """
    return sorted(
        articles,
        key=lambda article: parse_date(article.get("date", ""))
        or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )


# =============================================================================
# Fetch Live News
# =============================================================================

@st.cache_data(ttl=900, show_spinner=False)
def fetch_live_news():
    """
    Fetch live news from NASA and NOAA RSS feeds.

    Returns:
        articles, errors
    """
    session = get_http_session()

    all_articles = []
    errors = []

    for source_name, feed_urls in NEWS_FEEDS.items():
        source_loaded = False

        for feed_url in feed_urls:
            try:
                response = session.get(
                    feed_url,
                    timeout=20,
                )

                response.raise_for_status()

                parsed_articles = parse_feed(
                    response.content,
                    source_name,
                )

                if parsed_articles:
                    all_articles.extend(parsed_articles)
                    source_loaded = True

            except requests.RequestException as error:
                errors.append(
                    f"{source_name}: {type(error).__name__}"
                )

            except Exception as error:
                errors.append(
                    f"{source_name}: {type(error).__name__}"
                )

        if not source_loaded:
            errors.append(f"{source_name}: No articles available")

    prepared_articles = [
        prepare_article(article)
        for article in all_articles
        if is_relevant_climate_article(article)
    ]

    prepared_articles = deduplicate_articles(prepared_articles)

    prepared_articles = sort_articles(prepared_articles)

    return prepared_articles, errors


# =============================================================================
# Article Card
# =============================================================================

def render_article_card(article):
    """
    Render one article card.

    Uses st.html instead of st.markdown so the HTML is rendered
    as a proper card rather than displayed as raw source code.
    """
    title = html.escape(article.get("title", "Untitled article"))

    description = html.escape(
        article.get(
            "description",
            "No description available.",
        )
    )

    link = html.escape(
        article.get("link", "#"),
        quote=True,
    )

    source = html.escape(
        article.get("source", "Unknown source")
    )

    category = html.escape(
        article.get("category", "Climate Science")
    )

    article_date = html.escape(
        format_date(article.get("date", ""))
    )

    card_html = f"""
    <div style="
        border: 1px solid #d9e6df;
        border-radius: 16px;
        padding: 20px;
        margin: 14px 0;
        background: #ffffff;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        ">
            <span style="
                font-size: 13px;
                font-weight: 700;
                color: #176b45;
                background: #e8f5ee;
                padding: 5px 10px;
                border-radius: 999px;
            ">
                {source}
            </span>

            <span style="
                font-size: 12px;
                color: #66756d;
            ">
                {article_date}
            </span>
        </div>

        <div style="
            display: inline-block;
            font-size: 12px;
            font-weight: 600;
            color: #386b56;
            background: #f0f7f3;
            border: 1px solid #d7eadf;
            padding: 4px 9px;
            border-radius: 999px;
            margin-bottom: 10px;
        ">
            {category}
        </div>

        <h3 style="
            margin: 4px 0 10px 0;
            color: #173b2a;
            font-size: 21px;
            line-height: 1.35;
        ">
            {title}
        </h3>

        <p style="
            margin: 0 0 16px 0;
            color: #526158;
            font-size: 15px;
            line-height: 1.65;
        ">
            {description}
        </p>

        <a href="{link}"
           target="_blank"
           rel="noopener noreferrer"
           style="
                display: inline-block;
                text-decoration: none;
                background: #176b45;
                color: white;
                padding: 9px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
           ">
            Read full article ↗
        </a>
    </div>
    """

    st.html(card_html)


# =============================================================================
# Main Page
# =============================================================================

def show():
    """
    Display the Climate News page.
    """
    page_header(
        PAGE_TITLE,
        PAGE_SUBTITLE,
    )

    st.success(
        "Live climate and environmental news from NASA and NOAA."
    )

    st.caption(
        "News is retrieved from trusted scientific sources. "
        "Article content belongs to the original publisher."
    )

    section_divider()

    controls_col1, controls_col2 = st.columns(
        [3, 1]
    )

    with controls_col1:
        selected_category = st.selectbox(
            "Filter by category",
            [
                "All Categories",
                "Extreme Weather",
                "Ocean & Ice",
                "Biodiversity",
                "Renewable Energy",
                "Sustainability",
                "Climate Science",
            ],
            key="climate_news_category",
        )

    with controls_col2:
        st.write("")

        refresh_clicked = st.button(
            "Refresh News",
            width="stretch",
            key="refresh_climate_news",
        )

    if refresh_clicked:
        fetch_live_news.clear()
        st.rerun()

    with st.spinner("Fetching live climate news..."):
        articles, errors = fetch_live_news()

    if errors:
        st.warning(
            "Some news feeds could not be reached. "
            "Available articles are still shown."
        )

    if selected_category == "All Categories":
        filtered_articles = articles
    else:
        filtered_articles = [
            article
            for article in articles
            if article.get("category") == selected_category
        ]

    source_count = len(
        {
            article.get("source")
            for article in filtered_articles
        }
    )

    st.markdown(
        f"""
        **{len(filtered_articles)} climate-related articles**
        from **{source_count} trusted source(s)**.
        """
    )

    section_divider()

    if not filtered_articles:
        st.info(
            "No articles are available for this category right now. "
            "Try another category or refresh the news."
        )

    else:
        for article in filtered_articles:
            render_article_card(article)

    st.caption(
        "EcoGuard AI filters feed content for climate and environmental "
        "relevance. Classification is automated and may occasionally "
        "be imperfect."
    )

    footer()


# =============================================================================
# Page Entry Point
# =============================================================================

show()