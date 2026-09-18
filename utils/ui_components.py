# =============================================================================
# EcoGuard AI - Reusable UI Components
# =============================================================================

import streamlit as st

RISK_COLORS = {
    "LOW":       ("#1a7a4a", "#e6f4ed"),
    "MODERATE":  ("#b45309", "#fef3c7"),
    "HIGH":      ("#c2410c", "#fff0e6"),
    "VERY HIGH": ("#991b1b", "#fee2e2"),
    "CRITICAL":  ("#6b21a8", "#f3e8ff"),
    "UNKNOWN":   ("#374151", "#f3f4f6"),
}

RISK_EMOJIS = {
    "LOW":       "🟢",
    "MODERATE":  "🟡",
    "HIGH":      "🟠",
    "VERY HIGH": "🔴",
    "CRITICAL":  "🔴",
    "UNKNOWN":   "⚪",
}

GLOBAL_CSS = """
<style>
body, .stApp { font-family: -apple-system, "Segoe UI", system-ui, sans-serif; }

.eco-metric-card {
    background: #f8fffe;
    border: 1.5px solid #d1fae5;
    border-radius: 12px;
    padding: 18px 16px 14px 16px;
    text-align: center;
    min-height: 110px;
}
.eco-metric-card .metric-icon { font-size: 1.6rem; line-height: 1.2; }
.eco-metric-card .metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #6b7280;
    margin: 4px 0 2px 0;
}
.eco-metric-card .metric-value {
    font-size: 1.55rem;
    font-weight: 700;
    color: #065f46;
    line-height: 1.15;
}
.eco-metric-card .metric-sub {
    font-size: 0.72rem;
    color: #9ca3af;
    margin-top: 2px;
}
.risk-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}
.eco-card {
    background: #ffffff;
    border: 1.5px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px 20px 16px 20px;
    margin-bottom: 12px;
}
.eco-card h4 { margin: 0 0 8px 0; font-size: 1.0rem; color: #1f2328; }
.eco-card p  { margin: 0; font-size: 0.9rem; color: #374151; line-height: 1.55; }
.rec-card {
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.rec-card .rec-title { font-weight: 600; font-size: 0.9rem; color: #14532d; margin-bottom: 4px; }
.rec-card .rec-body  { font-size: 0.85rem; color: #374151; line-height: 1.5; }
.risk-overview-card {
    background: #ffffff;
    border: 1.5px solid #e5e7eb;
    border-radius: 14px;
    padding: 22px 20px 18px 20px;
    text-align: center;
    transition: box-shadow 0.2s;
    min-height: 200px;
}
.risk-overview-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.risk-overview-card .risk-icon { font-size: 2.4rem; }
.risk-overview-card h4 { font-size: 1.05rem; margin: 10px 0 6px 0; color: #1f2328; }
.risk-overview-card p  { font-size: 0.82rem; color: #6b7280; line-height: 1.5; margin: 0 0 12px 0; }
.news-card {
    background: #ffffff;
    border: 1.5px solid #e5e7eb;
    border-radius: 12px;
    padding: 18px 18px 14px 18px;
    margin-bottom: 14px;
}
.news-card .news-cat {
    display: inline-block;
    background: #dcfce7;
    color: #14532d;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 8px;
}
.news-card h4 { margin: 0 0 6px 0; font-size: 0.98rem; color: #1f2328; }
.news-card p  { margin: 0 0 8px 0; font-size: 0.84rem; color: #6b7280; line-height: 1.5; }
.news-card .news-meta { font-size: 0.75rem; color: #9ca3af; }
.chat-user {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 14px 14px 4px 14px;
    padding: 10px 14px;
    margin: 6px 0 6px 60px;
    font-size: 0.9rem;
    color: #1f2328;
}
.chat-bot {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px 14px 14px 4px;
    padding: 10px 14px;
    margin: 6px 60px 6px 0;
    font-size: 0.9rem;
    color: #1f2328;
    line-height: 1.55;
}
.eco-section-header {
    border-left: 4px solid #059669;
    padding-left: 12px;
    margin: 24px 0 14px 0;
}
.eco-section-header h3 { margin: 0; font-size: 1.15rem; color: #1f2328; }
.eco-section-header p  { margin: 4px 0 0 0; font-size: 0.83rem; color: #6b7280; }
.demo-notice {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.8rem;
    color: #92400e;
    margin-bottom: 16px;
}
.global-card {
    background: #f8fffe;
    border: 1.5px solid #d1fae5;
    border-radius: 12px;
    padding: 18px 16px;
    text-align: center;
}
.global-card .g-icon { font-size: 2rem; }
.global-card h5 { margin: 8px 0 6px 0; font-size: 0.92rem; color: #1f2328; }
.global-card p  { font-size: 0.8rem; color: #6b7280; line-height: 1.5; margin: 0 0 10px 0; }
.eco-footer {
    text-align: center;
    padding: 24px 0 16px 0;
    border-top: 1px solid #e5e7eb;
    margin-top: 40px;
    color: #9ca3af;
    font-size: 0.78rem;
    line-height: 1.8;
}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    html = f"""
    <div class="eco-section-header">
        <h3>{icon} {title}</h3>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def metric_card(icon: str, label: str, value: str, sub: str = ""):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="eco-metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(level: str) -> str:
    level_upper = level.upper()
    text_color, bg_color = RISK_COLORS.get(level_upper, RISK_COLORS["UNKNOWN"])
    emoji = RISK_EMOJIS.get(level_upper, "⚪")
    return (
        f'<span class="risk-badge" style="background:{bg_color};color:{text_color};">'
        f'{emoji} {level_upper}</span>'
    )


def risk_metric_card(icon: str, label: str, level: str):
    badge = risk_badge(level)
    st.markdown(
        f"""
        <div class="eco-metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div style="margin-top:6px;">{badge}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_card(title: str, body: str):
    st.markdown(
        f'<div class="eco-card"><h4>{title}</h4><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def recommendation_card(icon: str, title: str, body: str):
    st.markdown(
        f"""
        <div class="rec-card">
            <div class="rec-title">{icon} {title}</div>
            <div class="rec-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_divider(label: str = ""):
    if label:
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:12px;margin:20px 0 14px 0;'>"
            f"<hr style='flex:1;border:none;border-top:1px solid #e5e7eb;margin:0;'>"
            f"<span style='font-size:0.75rem;color:#9ca3af;white-space:nowrap;'>{label}</span>"
            f"<hr style='flex:1;border:none;border-top:1px solid #e5e7eb;margin:0;'></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<hr style='border:none;border-top:1px solid #e5e7eb;margin:20px 0;'>",
            unsafe_allow_html=True,
        )


def demo_notice(text: str = "📊 Sample data shown. Live data will be connected in a future phase."):
    st.markdown(
        f'<div class="demo-notice">⚠️ {text}</div>',
        unsafe_allow_html=True,
    )


def news_card(category: str, headline: str, description: str, date: str, source: str):
    st.markdown(
        f"""
        <div class="news-card">
            <span class="news-cat">{category}</span>
            <h4>{headline}</h4>
            <p>{description}</p>
            <div class="news-meta">🗓️ {date} &nbsp;·&nbsp; 📰 {source}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chat_user(message: str):
    st.markdown(f'<div class="chat-user">🧑 {message}</div>', unsafe_allow_html=True)


def chat_bot(message: str):
    st.markdown(f'<div class="chat-bot">🤖 {message}</div>', unsafe_allow_html=True)


def global_indicator_card(icon: str, title: str, body: str, explore_label: str = ""):
    st.markdown(
        f"""
        <div class="global-card">
            <div class="g-icon">{icon}</div>
            <h5>{title}</h5>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if explore_label:
        st.button(explore_label, key=f"gc_{title}", width="stretch")


def footer():
    st.markdown(
        """
        <div class="eco-footer">
            🌍 <strong>EcoGuard AI</strong><br>
            Climate Intelligence &nbsp;•&nbsp; Sustainability &nbsp;•&nbsp; Awareness<br>
            SDG 13 &nbsp;•&nbsp; SDG 11 &nbsp;•&nbsp; SDG 12 &nbsp;•&nbsp; SDG 15<br>
            <span style="font-size:0.72rem;">
                Educational Project &nbsp;·&nbsp;
                1M1B AI for Sustainability Internship &nbsp;·&nbsp;
                IBM SkillsBuild &amp; AICTE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
