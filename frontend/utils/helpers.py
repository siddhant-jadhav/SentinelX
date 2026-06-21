"""
SentinelX UI Helper Utilities
Color mappings, formatters, and HTML generators for the Streamlit frontend.
"""
from datetime import datetime


# ── Severity Colors ──────────────────────────────────────────────

SEVERITY_COLORS = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#D97706",
    "Low": "#2563EB",
    "Info": "#6B7280",
}

SEVERITY_BG = {
    "Critical": "#FEF2F2",
    "High": "#FFF7ED",
    "Medium": "#FFFBEB",
    "Low": "#EFF6FF",
    "Info": "#F3F4F6",
}

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Info"]

SOURCE_COLORS = {
    "OTX": {"bg": "#E8F4FD", "text": "#0A84FF"},
    "Community": {"bg": "#E6FBF5", "text": "#059669"},
}

STATUS_COLORS = {
    "Pending": {"bg": "#FEF3C7", "text": "#D97706"},
    "Approved": {"bg": "#D1FAE5", "text": "#059669"},
    "Rejected": {"bg": "#FEE2E2", "text": "#DC2626"},
}

INDICATOR_TYPE_ICONS = {
    "IPv4": "🌐",
    "IPv6": "🌐",
    "Domain": "🔗",
    "Hostname": "🖥️",
    "URL": "🔗",
    "FileHash-MD5": "📄",
    "FileHash-SHA1": "📄",
    "FileHash-SHA256": "📄",
    "Email": "📧",
    "CIDR": "🌐",
}

CHART_COLORS = [
    "#0A84FF", "#00D4AA", "#F59E0B", "#EF4444", "#8B5CF6",
    "#06B6D4", "#EC4899", "#10B981", "#F97316", "#6366F1",
]


# ── Badge Generators ─────────────────────────────────────────────

def severity_badge(severity: str) -> str:
    """Generate HTML for a severity badge."""
    color = SEVERITY_COLORS.get(severity, "#6B7280")
    bg = SEVERITY_BG.get(severity, "#F3F4F6")
    return (
        f'<span style="display:inline-block;padding:2px 10px;border-radius:20px;'
        f'font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;'
        f'background:{bg};color:{color}">{severity}</span>'
    )


def source_badge(source: str) -> str:
    """Generate HTML for a source badge."""
    colors = SOURCE_COLORS.get(source, {"bg": "#F3F4F6", "text": "#6B7280"})
    icon = "🛡️" if source == "OTX" else "👥"
    return (
        f'<span style="display:inline-block;padding:2px 10px;border-radius:20px;'
        f'font-size:0.7rem;font-weight:600;letter-spacing:0.03em;'
        f'background:{colors["bg"]};color:{colors["text"]}">{icon} {source}</span>'
    )


def status_badge(status: str) -> str:
    """Generate HTML for a status badge."""
    colors = STATUS_COLORS.get(status, {"bg": "#F3F4F6", "text": "#6B7280"})
    return (
        f'<span style="display:inline-block;padding:2px 10px;border-radius:20px;'
        f'font-size:0.7rem;font-weight:600;'
        f'background:{colors["bg"]};color:{colors["text"]}">{status}</span>'
    )


def indicator_display(indicator: str, indicator_type: str = "") -> str:
    """Generate HTML for an indicator value in monospace."""
    icon = INDICATOR_TYPE_ICONS.get(indicator_type, "🔍")
    return (
        f'{icon} <code style="font-family:\'JetBrains Mono\',monospace;font-size:0.85rem;'
        f'color:#1B2A4A;background:#F0F2F6;padding:2px 8px;border-radius:4px;'
        f'font-weight:500">{indicator}</code>'
    )


# ── Formatters ───────────────────────────────────────────────────

def format_date(date_str) -> str:
    """Format a date string or datetime to human-readable format."""
    if not date_str:
        return "N/A"
    if isinstance(date_str, str):
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return date_str
    elif isinstance(date_str, datetime):
        dt = date_str
    else:
        return str(date_str)

    return dt.strftime("%b %d, %Y %H:%M")


def format_relative_time(date_str) -> str:
    """Format a date as relative time (e.g., '2 hours ago')."""
    if not date_str:
        return "N/A"
    if isinstance(date_str, str):
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return date_str
    elif isinstance(date_str, datetime):
        dt = date_str
    else:
        return str(date_str)

    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 30:
        return f"{days}d ago"
    months = days // 30
    return f"{months}mo ago"


def risk_score_color(score: float) -> str:
    """Get color for a risk score value."""
    if score >= 9.0:
        return "#DC2626"
    elif score >= 7.0:
        return "#EA580C"
    elif score >= 4.0:
        return "#D97706"
    elif score >= 2.0:
        return "#2563EB"
    return "#6B7280"


def risk_score_bar(score: float) -> str:
    """Generate HTML for a risk score progress bar."""
    color = risk_score_color(score)
    width = min(score * 10, 100)
    return (
        f'<div style="display:flex;align-items:center;gap:8px">'
        f'<div style="flex:1;background:#E2E8F0;border-radius:4px;height:8px;overflow:hidden">'
        f'<div style="width:{width}%;background:{color};height:100%;border-radius:4px;'
        f'transition:width 0.5s ease"></div></div>'
        f'<span style="font-weight:700;color:{color};font-size:0.85rem;min-width:30px">'
        f'{score:.1f}</span></div>'
    )


# ── Page Header ──────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "", icon: str = "") -> str:
    """Generate HTML for a styled page header — light mode."""
    return (
        f'<div style="background:white;border:1px solid #E2E8F0;'
        f'border-left:4px solid #0A84FF;padding:1.25rem 1.75rem;border-radius:12px;'
        f'margin-bottom:1.5rem;box-shadow:0 2px 4px rgba(0,0,0,0.04)">'
        f'<h1 style="color:#1B2A4A!important;margin:0!important;font-size:1.4rem!important;'
        f'font-weight:800!important">{icon} {title}</h1>'
        f'<p style="color:#94A3B8!important;margin:0.25rem 0 0 0!important;'
        f'font-size:0.85rem!important">{subtitle}</p></div>'
    )


# ── Metric Card HTML ─────────────────────────────────────────────

def metric_card_html(label: str, value, icon: str, color: str = "#0A84FF", delta: str = "") -> str:
    """Generate HTML for a styled metric card."""
    delta_html = ""
    if delta:
        delta_color = "#10B981" if not delta.startswith("-") else "#EF4444"
        delta_html = (
            f'<div style="font-size:0.75rem;color:{delta_color};font-weight:600;margin-top:4px">'
            f'{delta}</div>'
        )

    return (
        f'<div style="background:white;border:1px solid #E2E8F0;border-radius:16px;'
        f'padding:1.25rem 1.5rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.07);'
        f'position:relative;overflow:hidden;transition:all 0.25s ease">'
        f'<div style="position:absolute;top:0;left:0;right:0;height:4px;'
        f'background:linear-gradient(90deg,{color},rgba(255,255,255,0))"></div>'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
        f'<div>'
        f'<div style="font-size:0.75rem;color:#64748B;font-weight:600;text-transform:uppercase;'
        f'letter-spacing:0.05em">{label}</div>'
        f'<div style="font-size:2rem;font-weight:800;color:#1B2A4A;line-height:1.2;'
        f'margin-top:4px">{value}</div>'
        f'{delta_html}'
        f'</div>'
        f'<div style="font-size:2rem;opacity:0.2">{icon}</div>'
        f'</div></div>'
    )
