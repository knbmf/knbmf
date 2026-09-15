#!/usr/bin/env python3
"""Paint Hindi donate share cards with local Devanagari fonts."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
LOGO = ROOT / "assets" / "logo-mark.png"
FONT = "/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc"
SERIF = "/System/Library/Fonts/Supplemental/ITFDevanagari.ttc"

MAROON = (110, 46, 38)
MAROON_DEEP = (90, 36, 30)
GOLD = (196, 160, 74)
CREAM = (244, 238, 228)
PAPER = (251, 247, 240)
INK = (28, 23, 18)
MUTED = (93, 85, 75)
WHITE = (255, 252, 247)


def font(size, serif=False):
    path = SERIF if serif else FONT
    try:
        return ImageFont.truetype(path, size, index=0)
    except OSError:
        return ImageFont.truetype(FONT, size, index=0)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def paste_logo(im, xy, size):
    if not LOGO.exists():
        return
    mark = Image.open(LOGO).convert("RGBA")
    mark.thumbnail((size, size))
    im.alpha_composite(mark, xy)


def card_square():
    w = h = 1080
    im = Image.new("RGBA", (w, h), CREAM + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((48, 48, w - 48, h - 48), outline=GOLD, width=4)
    d.rectangle((72, 72, w - 72, h - 72), fill=PAPER + (255,))
    paste_logo(im, (90, 110), 120)
    y = 130
    d.text((230, y), "कष्ट निवारण बालाजी मंदिर", font=font(42, True), fill=MAROON)
    d.text((230, y + 58), "फाउंडेशन  |  काशीपुर", font=font(32), fill=MUTED)
    d.line((90, 280, w - 90, 280), fill=GOLD, width=2)
    title = font(64, True)
    for i, line in enumerate(["आज दान करें।", "कल परिसर बने।"]):
        d.text((90, 330 + i * 84), line, font=title, fill=MAROON_DEEP)
    body = font(34)
    lines = wrap(
        d,
        "धारा 8 संस्था। मंगलवार निःशुल्क धन्वंतरी क्लिनिक चल रहा है। आगे बालाजी मंदिर, चैरिटेबल अस्पताल, विद्यालय, गौशाला, वृद्धाश्रम, अनाथाश्रम।",
        body,
        w - 180,
    )
    y = 530
    for line in lines:
        d.text((90, y), line, font=body, fill=INK)
        y += 48
    d.rounded_rectangle((90, 760, w - 90, 860), 18, fill=MAROON)
    d.text((120, 782), "Donate now   |   give.html", font=font(40), fill=WHITE)
    d.text((90, 890), "UPI  knbmfoundatio@ybl", font=font(32), fill=MAROON)
    d.text(
        (90, 940),
        "kashtnivaranbalajimandirfoundation.org/give.html",
        font=font(26),
        fill=MUTED,
    )
    d.text((90, 980), "CIN U88900UT2025NPL019252   |  अस्थायी 80G", font=font(24), fill=MUTED)
    rgb = Image.new("RGB", im.size, CREAM)
    rgb.paste(im, mask=im.split()[-1])
    rgb.save(OUT / "share-wa.jpg", "JPEG", quality=90, optimize=True)


def card_story():
    w, h = 1080, 1920
    im = Image.new("RGBA", (w, h), CREAM + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 16), fill=GOLD)
    d.rectangle((0, h - 16, w, h), fill=MAROON)
    paste_logo(im, (90, 80), 140)
    d.text((250, 110), "कष्ट निवारण बालाजी मंदिर", font=font(38, True), fill=MAROON)
    d.text((250, 168), "फाउंडेशन", font=font(38, True), fill=MAROON)
    d.text((90, 280), "काशीपुर  |  उत्तराखंड", font=font(32), fill=MUTED)
    d.text((90, 380), "सेवा का", font=font(86, True), fill=MAROON_DEEP)
    d.text((90, 490), "परिसर", font=font(86, True), fill=MAROON_DEEP)
    d.text((90, 600), "उठ रहा है।", font=font(86, True), fill=GOLD)
    body = font(36)
    copy = [
        "अभी: मंगलवार निःशुल्क क्लिनिक",
        "आगे: मंदिर, अस्पताल, विद्यालय",
        "गौशाला, वृद्धाश्रम, अनाथाश्रम",
        "",
        "दान संस्था के UPI पर जाता है।",
        "व्यक्तिगत खाते में नहीं।",
    ]
    y = 760
    for line in copy:
        d.text((90, y), line, font=body, fill=INK)
        y += 58
    d.rounded_rectangle((90, 1220, w - 90, 1380), 24, fill=MAROON)
    d.text((130, 1255), "अभी दान करें", font=font(52, True), fill=WHITE)
    d.text((130, 1320), "give.html  |  knbmfoundatio@ybl", font=font(30), fill=GOLD)
    d.text((90, 1460), "kashtnivaranbalajimandirfoundation.org", font=font(28), fill=MUTED)
    d.text((90, 1520), "CIN U88900UT2025NPL019252", font=font(26), fill=MUTED)
    d.text((90, 1570), "अस्थायी 12A और 80G", font=font(26), fill=MUTED)
    rgb = Image.new("RGB", im.size, CREAM)
    rgb.paste(im, mask=im.split()[-1])
    rgb.save(OUT / "share-story.jpg", "JPEG", quality=90, optimize=True)


def card_og():
    w, h = 1200, 630
    im = Image.new("RGBA", (w, h), PAPER + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 18, h), fill=GOLD)
    d.rectangle((0, h - 18, w, h), fill=MAROON)
    paste_logo(im, (56, 48), 96)
    d.text((170, 58), "Kast Nivaran Balaji Mandir Foundation", font=font(28), fill=MUTED)
    d.text((170, 98), "काशीपुर  |  धारा 8 संस्था", font=font(26), fill=MAROON)
    d.text((56, 190), "आज दान करें।", font=font(64, True), fill=MAROON_DEEP)
    d.text((56, 270), "कल परिसर बने।", font=font(64, True), fill=MAROON_DEEP)
    d.text(
        (56, 370),
        "UPI knbmfoundatio@ybl  |  मंगलवार निःशुल्क क्लिनिक  |  अस्थायी 80G",
        font=font(26),
        fill=INK,
    )
    d.rounded_rectangle((56, 440, 620, 530), 16, fill=MAROON)
    d.text((80, 462), "kashtnivaranbalajimandirfoundation.org/give.html", font=font(24), fill=WHITE)
    d.text((56, 555), "CIN U88900UT2025NPL019252", font=font(22), fill=MUTED)
    rgb = Image.new("RGB", im.size, PAPER)
    rgb.paste(im, mask=im.split()[-1])
    rgb.save(OUT / "og-donate.jpg", "JPEG", quality=90, optimize=True)


def main():
    OUT.mkdir(exist_ok=True)
    card_square()
    card_story()
    card_og()
    print("wrote share-wa.jpg share-story.jpg og-donate.jpg")


if __name__ == "__main__":
    main()
