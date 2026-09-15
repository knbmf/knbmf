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
        "desc": "काशीपुर की धारा 8 संस्था। धन्वंतरी क्लिनिक मंगलवार निःशुल्क। आगे बालाजी मंदिर निर्माण, चैरिटेबल अस्पताल, विद्यालय, गौशाला, वृद्धाश्रम, अनाथाश्रम। CIN U88900UT2025NPL019252, अस्थायी 12A और 80G।",
        "type": "website",
    },
    "about.html": {
        "url": f"{BASE}/about.html",
        "title": "परिचय | कष्ट निवारण बालाजी मंदिर फाउंडेशन काशीपुर",
        "desc": "20 मई 2025 को निगमित धारा 8 कंपनी। काशीपुर में क्लिनिक, बालाजी मंदिर निर्माण, चैरिटेबल अस्पताल, विद्यालय, गौशाला और आश्रम का परिसर। लाभ नहीं, अधिशेष सेवा में रहता है।",
    },
    "clinic.html": {
        "url": f"{BASE}/clinic.html",
        "title": "धन्वंतरी क्लिनिक | मंगलवार निःशुल्क ओपीडी काशीपुर",
        "desc": "धन्वंतरी इलेक्ट्रो होम्योपैथिक चैरिटेबल क्लिनिक, शिवाल्य पुर, डल्लू कुंडेश्वरी। हर मंगलवार निःशुल्क परामर्श और उपचार।",
    },
    "projects.html": {
        "url": f"{BASE}/projects.html",
        "title": "परियोजनाएँ | मंदिर निर्माण, अस्पताल, विद्यालय, गौशाला",
        "desc": "कष्ट निवारण बालाजी मंदिर फाउंडेशन का परिसर: बालाजी मंदिर निर्माण, चैरिटेबल अस्पताल, विद्या मंदिर, गौशाला, वृद्धाश्रम, अनाथाश्रम, पशु सेवा केनेल और धन्वंतरी क्लिनिक।",
    },
    "work.html": {
        "url": f"{BASE}/work.html",
        "title": "हमारा कार्य | सेवा काशीपुर उत्तराखंड",
        "desc": "अभी मंगलवार चैरिटेबल क्लिनिक। आगे बालाजी मंदिर निर्माण, चैरिटेबल अस्पताल, शिक्षा, गौ सेवा, वृद्ध, बच्चे और आवारा पशुओं की सेवा काशीपुर में।",
    },
    "donate.html": {
        "url": f"{BASE}/donate.html",
        "title": "दान करें | कष्ट निवारण बालाजी मंदिर फाउंडेशन UPI",
        "desc": "UPI knbmfoundatio@ybl पर दान करें। प्राप्तकर्ता Kast Nivaran Balaji Mandir Foundation। अस्थायी 12A और 80G। टिप्पणी web1, web2…",
        "image": f"{BASE}/assets/og-donate.jpg",
    },
    "give.html": {
        "url": f"{BASE}/give.html",
        "title": "दान फ़ॉर्म | UPI क्यूआर बनाएँ | KNBMF काशीपुर",
        "desc": "नाम, मोबाइल, ईमेल और राशि लिखें। UPI क्यूआर knbmfoundatio@ybl पर बनेगा। टिप्पणी Kast Nivaran Balaji Mandir Foundation web1।",
        "image": f"{BASE}/assets/og-donate.jpg",
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
    "faq.html": {
        "url": f"{BASE}/faq.html",
        "title": "दान प्रश्न | 80G UPI काशीपुर धारा 8 संस्था",
        "desc": "कष्ट निवारण बालाजी मंदिर फाउंडेशन को UPI knbmfoundatio@ybl पर दान कैसे करें, 80G रसीद, CIN, क्लिनिक और परिसर। काशीपुर उत्तराखंड।",
    },
    "share.html": {
        "url": f"{BASE}/share.html",
        "title": "साझा करें | KNBMF दान अभियान WhatsApp Facebook",
        "desc": "कष्ट निवारण बालाजी मंदिर फाउंडेशन का दान लिंक WhatsApp, Facebook, Telegram पर भेजें। तैयार संदेश, 80G, UPI knbmfoundatio@ybl, काशीपुर।",
        "image": f"{BASE}/assets/og-donate.jpg",
    },
    "en.html": {
        "url": f"{BASE}/en.html",
        "title": "Donate | Kast Nivaran Balaji Mandir Foundation Kashipur",
        "desc": "Section 8 NGO in Kashipur, Uttarakhand. Donate via UPI knbmfoundatio@ybl. Tuesday free clinic. Projected Balaji temple, hospital, school, gaushala. Provisional 80G. CIN U88900UT2025NPL019252.",
        "type": "website",
        "lang": "en",
        "image": f"{BASE}/assets/og-donate.jpg",
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
    "description": "Section 8 company in Kashipur, Uttarakhand. Tuesday free Dhanvantari clinic; campus for Balaji temple construction, charitable hospital, school, gaushala, old-age home, orphanage and animal kennel. Donate via UPI knbmfoundatio@ybl.",
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
    "sameAs": [
        "https://tracxn.com/d/legal-entities/india/kast-nivaran-balaji-mandir-foundation/__uyyPYoMxJanZg9SUTpMeiMKDIe_KmysbJtlcML2sFQM",
        "https://wa.me/917668397233",
    ],
    "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "customer support",
        "email": "support@kashtnivaranbalajimandirfoundation.org",
        "url": "https://wa.me/917668397233",
        "availableLanguage": ["hi", "en"],
    },
    "potentialAction": {
        "@type": "DonateAction",
        "name": "Donate to Kast Nivaran Balaji Mandir Foundation",
        "target": f"{BASE}/give.html",
    },
}

FAQ_ITEMS = [
    (
        "काशीपुर में इस संस्था को दान कैसे करें?",
        "give.html पर नाम, मोबाइल, ईमेल और राशि लिखें। PhonePe या Google Pay से स्कैन करने योग्य UPI क्यूआर बनता है। UPI आईडी knbmfoundatio@ybl, प्राप्तकर्ता Kast Nivaran Balaji Mandir Foundation।",
    ),
    (
        "UPI आईडी क्या है? व्यक्तिगत खाता तो नहीं?",
        "संस्था की UPI आईडी knbmfoundatio@ybl है। प्राप्तकर्ता का नाम संस्था का कानूनी नाम है। CIN U88900UT2025NPL019252, PAN AALCK8805B।",
    ),
    (
        "80G की रसीद मिलेगी क्या?",
        "12A और 80G URN निर्धारण वर्ष 2026–27 से 2028–29 के लिए अस्थायी हैं। भुगतान के बाद UTR और PAN के साथ support@kashtnivaranbalajimandirfoundation.org पर लिखें।",
    ),
    (
        "धन कहाँ लगेगा?",
        "पहले धन्वंतरी चैरिटेबल क्लिनिक की दवा और सामग्री। आगे बालाजी मंदिर निर्माण, चैरिटेबल अस्पताल, विद्यालय और गौशाला के लिए भूमि। फिर वृद्धाश्रम, अनाथाश्रम और पशु सेवा केनेल।",
    ),
    (
        "निःशुल्क क्लिनिक कब और कहाँ खुलता है?",
        "धन्वंतरी इलेक्ट्रो होम्योपैथिक चैरिटेबल क्लिनिक हर मंगलवार शिवाल्य पुर, डल्लू कुंडेश्वरी, काशीपुर में निःशुल्क परामर्श और उपचार देता है।",
    ),
]


def seo_block(page: str, meta: dict) -> str:
    url = meta["url"]
    title = meta["title"]
    desc = meta["desc"]
    og_type = meta.get("type", "article")
    og_image = meta.get("image", OG)
    robots = meta.get("robots", "index, follow")
    is_en = meta.get("lang") == "en"
    in_lang = "en-IN" if is_en else "hi-IN"
    og_locale = "en_IN" if is_en else "hi_IN"
    ld = [
        ORG_LD,
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "description": desc,
            "url": url,
            "inLanguage": in_lang,
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
    if page in ("donate.html", "give.html", "en.html", "index.html"):
        ld.append(
            {
                "@context": "https://schema.org",
                "@type": "DonateAction",
                "name": "Donate to Kast Nivaran Balaji Mandir Foundation",
                "target": f"{BASE}/give.html",
                "recipient": {"@type": "NGO", "name": ORG},
            }
        )
    if page == "faq.html":
        ld.append(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a},
                    }
                    for q, a in FAQ_ITEMS
                ],
            }
        )
    ld_json = json.dumps(ld, ensure_ascii=False, separators=(",", ":"))
    hreflang = f'  <link rel="alternate" hreflang="hi" href="{url}">\n  <link rel="alternate" hreflang="x-default" href="{url}">'
    if page == "index.html":
        hreflang = (
            f'  <link rel="alternate" hreflang="hi" href="{BASE}/">\n'
            f'  <link rel="alternate" hreflang="en" href="{BASE}/en.html">\n'
            f'  <link rel="alternate" hreflang="x-default" href="{BASE}/">'
        )
    if page == "en.html":
        hreflang = (
            f'  <link rel="alternate" hreflang="en" href="{BASE}/en.html">\n'
            f'  <link rel="alternate" hreflang="hi" href="{BASE}/">\n'
            f'  <link rel="alternate" hreflang="x-default" href="{BASE}/">'
        )
    return f"""  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="{robots}">
  <meta name="author" content="{ORG}">
  <meta name="geo.region" content="IN-UK">
  <meta name="geo.placename" content="Kashipur">
  <link rel="canonical" href="{url}">
{hreflang}
  <meta property="og:site_name" content="{ORG}">
  <meta property="og:locale" content="{og_locale}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{og_image}">
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
        "en.html": "0.9",
        "faq.html": "0.8",
        "share.html": "0.8",
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
        if name in ("give.html", "donate.html", "share.html"):
            lines.append(
                f'    <image:image><image:loc>{BASE}/assets/og-donate.jpg</image:loc></image:image>'
            )
        if name == "projects.html":
            for img in (
                "mandir-1.jpg",
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
        f"Sitemap: {BASE}/sitemap.xml\n"
        "# AI assistants: see /llms.txt for a plain-language summary of the Foundation.\n",
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
