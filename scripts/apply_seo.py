#!/usr/bin/env python3
"""Inject canonical, Open Graph, Twitter, and JSON-LD into public HTML pages."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://kashtnivaranbalajimandirfoundation.org"
OG = f"{BASE}/assets/og-cover.jpg"
ORG = "Kast Nivaran Balaji Mandir Foundation"

PAGES = {
    "index.html": {
        "url": f"{BASE}/",
        "title": "कष्ट निवारण बालाजी मंदिर फाउंडेशन | काशीपुर धारा 8 संस्था",
        "desc": "काशीपुर की धारा 8 संस्था। धन्वंतरी क्लिनिक मंगलवार निःशुल्क। दान, विद्यालय, गौशाला, वृद्धाश्रम, अनाथाश्रम। CIN U88900UT2025NPL019252, अस्थायी 12A और 80G।",
        "type": "website",
    },
    "about.html": {
        "url": f"{BASE}/about.html",
        "title": "परिचय | कष्ट निवारण बालाजी मंदिर फाउंडेशन काशीपुर",
        "desc": "20 मई 2025 को निगमित धारा 8 कंपनी। काशीपुर में क्लिनिक, विद्यालय, गौशाला और आश्रम का परिसर। लाभ नहीं, अधिशेष सेवा में रहता है।",
    },
    "clinic.html": {
        "url": f"{BASE}/clinic.html",
        "title": "धन्वंतरी क्लिनिक | मंगलवार निःशुल्क ओपीडी काशीपुर",
        "desc": "धन्वंतरी इलेक्ट्रो होम्योपैथिक चैरिटेबल क्लिनिक, शिवाल्य पुर, डल्लू कुंडेश्वरी। हर मंगलवार निःशुल्क परामर्श और उपचार।",
    },
    "projects.html": {
        "url": f"{BASE}/projects.html",
        "title": "परियोजनाएँ | विद्यालय, गौशाला, वृद्धाश्रम, अनाथाश्रम",
        "desc": "कष्ट निवारण बालाजी मंदिर फाउंडेशन का परिसर: विद्या मंदिर, गौशाला, वृद्धाश्रम, अनाथाश्रम, पशु सेवा केनेल और धन्वंतरी क्लिनिक।",
    },
    "work.html": {
        "url": f"{BASE}/work.html",
        "title": "हमारा कार्य | सेवा काशीपुर उत्तराखंड",
        "desc": "अभी मंगलवार चैरिटेबल क्लिनिक। आगे शिक्षा, गौ सेवा, वृद्ध, बच्चे और आवारा पशुओं की सेवा काशीपुर में।",
    },
    "donate.html": {
        "url": f"{BASE}/donate.html",
        "title": "दान करें | कष्ट निवारण बालाजी मंदिर फाउंडेशन UPI",
        "desc": "UPI knbmfoundatio@ybl पर दान करें। प्राप्तकर्ता Kast Nivaran Balaji Mandir Foundation। अस्थायी 12A और 80G। टिप्पणी web1, web2…",
    },
    "give.html": {
        "url": f"{BASE}/give.html",
        "title": "दान फ़ॉर्म | UPI क्यूआर बनाएँ | KNBMF काशीपुर",
        "desc": "नाम, मोबाइल, ईमेल और राशि लिखें। UPI क्यूआर knbmfoundatio@ybl पर बनेगा। टिप्पणी Kast Nivaran Balaji Mandir Foundation web1।",
    },
    "transparency.html": {
        "url": f"{BASE}/transparency.html",
        "title": "पारदर्शिता | CIN PAN 12A 80G GSTIN काशीपुर",
        "desc": "CIN U88900UT2025NPL019252, PAN AALCK8805B, GSTIN 05AALCK8805B1ZO, अस्थायी 12A और 80G, NGO Darpan UK/2026/0989165। व्यक्तिगत नाम नहीं।",
    },
    "contact.html": {
        "url": f"{BASE}/contact.html",
        "title": "संपर्क | कष्ट निवारण बालाजी मंदिर फाउंडेशन काशीपुर",
        "desc": "ईमेल support@kashtnivaranbalajimandirfoundation.org। पंजीकृत कार्यालय हेरिटेज सिटी, जसपुर खुर्द, काशीपुर 244713। क्लिनिक शिवाल्य पुर।",
    },
    "policies.html": {
        "url": f"{BASE}/policies.html",
        "title": "नीतियाँ | नियम, गोपनीयता, धनवापसी | KNBMF",
        "desc": "PhonePe और वेबसाइट के लिए नियम और शर्तें, गोपनीयता नीति, धनवापसी, वापसी और शिपिंग नीति के सार्वजनिक लिंक।",
    },
    "terms.html": {
        "url": f"{BASE}/terms.html",
        "title": "Terms and Conditions | Kast Nivaran Balaji Mandir Foundation",
        "desc": "Terms for the KNBMF website, UPI donations, PhonePe, Dhanvantari clinic, provisional 12A and 80G. Section 8 company, Kashipur.",
    },
    "privacy_policy.html": {
        "url": f"{BASE}/privacy_policy.html",
        "title": "Privacy Policy | Kast Nivaran Balaji Mandir Foundation",
        "desc": "How Kast Nivaran Balaji Mandir Foundation collects and uses donor, clinic and payment data under Indian DPDP Act.",
    },
    "refund_policy.html": {
        "url": f"{BASE}/refund_policy.html",
        "title": "Refund Policy | Kast Nivaran Balaji Mandir Foundation",
        "desc": "Donation refund and cancellation policy for KNBMF UPI and PhonePe gifts. Donations are generally non-refundable.",
    },
    "return_policy.html": {
        "url": f"{BASE}/return_policy.html",
        "title": "Return Policy | Kast Nivaran Balaji Mandir Foundation",
        "desc": "KNBMF does not sell goods. Donations are not products. Clinic medicines are charitable, not retail returns.",
    },
    "shipping_policy.html": {
        "url": f"{BASE}/shipping_policy.html",
        "title": "Shipping Policy | Kast Nivaran Balaji Mandir Foundation",
        "desc": "KNBMF does not ship goods. Clinic care is in person in Kashipur. Receipts are emailed.",
    },
    "404.html": {
        "url": f"{BASE}/404.html",
        "title": "पृष्ठ नहीं मिला | कष्ट निवारण बालाजी मंदिर फाउंडेशन",
        "desc": "यह पृष्ठ कष्ट निवारण बालाजी मंदिर फाउंडेशन की साइट पर नहीं है। मुखपृष्ठ पर लौटें।",
        "robots": "noindex, follow",
    },
}

ORG_LD = {
    "@context": "https://schema.org",
    "@type": ["NGO", "Organization"],
    "name": ORG,
    "alternateName": ["KNBMF", "कष्ट निवारण बालाजी मंदिर फाउंडेशन"],
    "url": f"{BASE}/",
    "logo": f"{BASE}/assets/logo-mark.png",
    "image": OG,
    "email": "support@kashtnivaranbalajimandirfoundation.org",
    "foundingDate": "2025-05-20",
    "taxID": "AALCK8805B",
    "vatID": "05AALCK8805B1ZO",
    "identifier": [
        {"@type": "PropertyValue", "name": "CIN", "value": "U88900UT2025NPL019252"},
        {"@type": "PropertyValue", "name": "12A URN", "value": "AALCK8805BE20251"},
        {"@type": "PropertyValue", "name": "80G URN", "value": "AALCK8805BF20261"},
        {"@type": "PropertyValue", "name": "NGO Darpan", "value": "UK/2026/0989165"},
    ],
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Heritage City, Jaspur Khurd",
        "addressLocality": "Kashipur",
        "addressRegion": "Uttarakhand",
        "postalCode": "244713",
        "addressCountry": "IN",
    },
    "areaServed": "IN",
    "knowsLanguage": ["hi", "en"],
}


def seo_block(page: str, meta: dict) -> str:
    url = meta["url"]
    title = meta["title"]
    desc = meta["desc"]
    og_type = meta.get("type", "article")
    robots = meta.get("robots", "index, follow")
    ld = [
        ORG_LD,
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "description": desc,
            "url": url,
            "inLanguage": "hi-IN",
            "isPartOf": {"@type": "WebSite", "name": ORG, "url": f"{BASE}/"},
        },
    ]
    if page == "clinic.html":
        ld.append(
            {
                "@context": "https://schema.org",
                "@type": "MedicalClinic",
                "name": "Dhanvantari Electro Homeopathic Charitable Clinic",
                "url": f"{BASE}/clinic.html",
                "parentOrganization": {"@type": "NGO", "name": ORG},
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Shivalay Pur, Dallu Kundeshwari",
                    "addressLocality": "Kashipur",
                    "addressRegion": "Uttarakhand",
                    "addressCountry": "IN",
                },
                "openingHours": "Tu",
                "priceRange": "Free",
            }
        )
    if page in ("donate.html", "give.html"):
        ld.append(
            {
                "@context": "https://schema.org",
                "@type": "DonateAction",
                "name": "Donate to Kast Nivaran Balaji Mandir Foundation",
                "target": f"{BASE}/give.html",
                "recipient": {"@type": "NGO", "name": ORG},
            }
        )
    ld_json = json.dumps(ld, ensure_ascii=False, separators=(",", ":"))
    return f"""  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="{robots}">
  <meta name="author" content="{ORG}">
  <meta name="geo.region" content="IN-UK">
  <meta name="geo.placename" content="Kashipur">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="hi" href="{url}">
  <link rel="alternate" hreflang="x-default" href="{url}">
  <meta property="og:site_name" content="{ORG}">
  <meta property="og:locale" content="hi_IN">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{OG}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{OG}">
  <script type="application/ld+json">{ld_json}</script>
"""


def strip_old_seo(html: str) -> str:
    html = re.sub(r"\s*<title>.*?</title>", "", html, count=1, flags=re.S)
    html = re.sub(
        r"\s*<meta name=\"description\" content=\"[^\"]*\">",
        "",
        html,
        count=1,
    )
    html = re.sub(r"\s*<meta name=\"robots\" content=\"[^\"]*\">", "", html)
    html = re.sub(r"\s*<meta name=\"author\" content=\"[^\"]*\">", "", html)
    html = re.sub(r"\s*<meta name=\"geo\.[^\"]+\" content=\"[^\"]*\">", "", html)
    html = re.sub(r"\s*<link rel=\"canonical\" href=\"[^\"]*\">", "", html)
    html = re.sub(r"\s*<link rel=\"alternate\" hreflang=\"[^\"]+\" href=\"[^\"]*\">", "", html)
    html = re.sub(r"\s*<meta property=\"og:[^\"]+\" content=\"[^\"]*\">", "", html)
    html = re.sub(r"\s*<meta name=\"twitter:[^\"]+\" content=\"[^\"]*\">", "", html)
    html = re.sub(
        r"\s*<script type=\"application/ld\+json\">.*?</script>",
        "",
        html,
        count=1,
        flags=re.S,
    )
    return html


def apply_page(path: Path, meta: dict) -> None:
    html = path.read_text(encoding="utf-8")
    html = strip_old_seo(html)
    html = html.replace('alt="">', 'alt="कष्ट निवारण बालाजी मंदिर फाउंडेशन लोगो">', 1)
    html = html.replace(
        '<nav class="nav" id="nav">',
        '<nav class="nav" id="nav" aria-label="मुख्य मेनू">',
        1,
    )
    block = seo_block(path.name, meta)
    html = html.replace(
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n' + block,
        1,
    )
    path.write_text(html, encoding="utf-8")
    print("seo", path.name)


def write_sitemap() -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    pri = {
        "index.html": "1.0",
        "give.html": "0.9",
        "donate.html": "0.9",
        "clinic.html": "0.8",
        "projects.html": "0.8",
        "about.html": "0.7",
    }
    for name, meta in PAGES.items():
        if name == "404.html":
            continue
        p = pri.get(name, "0.6")
        freq = "weekly" if p in ("1.0", "0.9") else "monthly"
        lines.append("  <url>")
        lines.append(f"    <loc>{meta['url']}</loc>")
        lines.append("    <lastmod>2026-09-15</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{p}</priority>")
        if name == "index.html":
            lines.append(f'    <image:image><image:loc>{OG}</image:loc></image:image>')
        if name == "projects.html":
            for img in (
                "gaushala-1.jpg",
                "school-1.jpg",
                "hospital-1.jpg",
                "vriddh-1.jpg",
                "anath-1.jpg",
            ):
                lines.append(
                    f'    <image:image><image:loc>{BASE}/assets/campus/{img}</image:loc></image:image>'
                )
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("sitemap")


def write_robots() -> None:
    (ROOT / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /404.html\n"
        "\n"
        f"Sitemap: {BASE}/sitemap.xml\n",
        encoding="utf-8",
    )
    print("robots")


def main() -> None:
    for name, meta in PAGES.items():
        path = ROOT / name
        if path.is_file():
            apply_page(path, meta)
    write_sitemap()
    write_robots()


if __name__ == "__main__":
    main()
