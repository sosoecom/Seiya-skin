from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable
import os

# ─── PALETTE SEIYA SKIN ───────────────────────────────────────────────────────
NOIR        = colors.HexColor("#1A1A1A")
BLANC       = colors.HexColor("#FFFFFF")
CREME       = colors.HexColor("#FAF7F2")
BEIGE       = colors.HexColor("#F0EBE3")
BEIGE_DARK  = colors.HexColor("#D9D0C3")
TAUPE       = colors.HexColor("#B0A090")
GOLD        = colors.HexColor("#C4A882")
GOLD_LIGHT  = colors.HexColor("#E8D5BE")
ACCENT      = colors.HexColor("#8B7355")

W, H = A4  # 210 x 297 mm

# ─── HELPERS ─────────────────────────────────────────────────────────────────

class ColoredRect(Flowable):
    """Full-width colored rectangle used as section dividers / backgrounds."""
    def __init__(self, width, height, fill_color, radius=4):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.fill_color)
        self.canv.roundRect(0, 0, self.width, self.height,
                            self.radius, stroke=0, fill=1)


def make_doc(filename):
    return SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=16*mm,
        bottomMargin=16*mm,
        title="Brief UGC — Seiya Skin",
        author="Seiya Skin",
    )


def styles():
    """Return a dict of paragraph styles."""
    base = getSampleStyleSheet()

    def ps(name, parent="Normal", **kw):
        return ParagraphStyle(name, parent=base[parent], **kw)

    return {
        # ── brand header ──────────────────────────────────────
        "brand": ps("brand",
            fontName="Helvetica",
            fontSize=8,
            textColor=TAUPE,
            letterSpacing=3,
            alignment=TA_CENTER,
            spaceAfter=1*mm,
        ),
        # ── hero title ────────────────────────────────────────
        "hero_title": ps("hero_title",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=NOIR,
            leading=27,
            alignment=TA_CENTER,
            spaceBefore=3*mm,
            spaceAfter=2*mm,
        ),
        "hero_sub": ps("hero_sub",
            fontName="Helvetica-Oblique",
            fontSize=11,
            textColor=ACCENT,
            leading=15,
            alignment=TA_CENTER,
            spaceAfter=1*mm,
        ),
        # ── section label ─────────────────────────────────────
        "section_label": ps("section_label",
            fontName="Helvetica",
            fontSize=7,
            textColor=GOLD,
            letterSpacing=2.5,
            spaceBefore=5*mm,
            spaceAfter=1.5*mm,
        ),
        # ── section title ─────────────────────────────────────
        "section_title": ps("section_title",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=NOIR,
            leading=17,
            spaceAfter=3*mm,
        ),
        # ── body ──────────────────────────────────────────────
        "body": ps("body",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=NOIR,
            leading=15,
            spaceAfter=2*mm,
        ),
        "body_bold": ps("body_bold",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=NOIR,
            leading=15,
            spaceAfter=1.5*mm,
        ),
        # ── quote / intention ─────────────────────────────────
        "quote": ps("quote",
            fontName="Helvetica-Oblique",
            fontSize=10,
            textColor=ACCENT,
            leading=16,
            leftIndent=6*mm,
            spaceAfter=2*mm,
        ),
        # ── dialogue ──────────────────────────────────────────
        "dialogue": ps("dialogue",
            fontName="Helvetica-BoldOblique",
            fontSize=10.5,
            textColor=NOIR,
            leading=16,
            leftIndent=4*mm,
            spaceAfter=2*mm,
        ),
        # ── caption / screen text ─────────────────────────────
        "caption": ps("caption",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=ACCENT,
            leading=13,
            spaceAfter=1.5*mm,
        ),
        # ── tag (pill label) ──────────────────────────────────
        "tag": ps("tag",
            fontName="Helvetica",
            fontSize=8,
            textColor=BLANC,
            alignment=TA_CENTER,
        ),
        # ── hook item ─────────────────────────────────────────
        "hook": ps("hook",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=NOIR,
            leading=14,
            leftIndent=4*mm,
            spaceAfter=2*mm,
        ),
        # ── footer ────────────────────────────────────────────
        "footer": ps("footer",
            fontName="Helvetica",
            fontSize=7.5,
            textColor=TAUPE,
            alignment=TA_CENTER,
        ),
        # ── timecode ──────────────────────────────────────────
        "timecode": ps("timecode",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=GOLD,
            letterSpacing=1,
        ),
        # ── info box ──────────────────────────────────────────
        "info_key": ps("info_key",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            textColor=ACCENT,
            spaceAfter=0.5*mm,
        ),
        "info_val": ps("info_val",
            fontName="Helvetica",
            fontSize=9,
            textColor=NOIR,
            leading=13,
            spaceAfter=2*mm,
        ),
        # ── warning / note ────────────────────────────────────
        "note": ps("note",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=ACCENT,
            leading=13,
            leftIndent=3*mm,
        ),
    }


def sp(n=1):
    return Spacer(1, n * 3*mm)


def hr(color=BEIGE_DARK, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=3*mm, spaceBefore=3*mm)


def section_header(s, label_text, title_text):
    """Gold micro-label + bold title."""
    return [
        Paragraph(label_text.upper(), s["section_label"]),
        Paragraph(title_text, s["section_title"]),
    ]


def pill(s, text, bg=GOLD, fg=BLANC):
    """Small pill-shaped label."""
    data = [[Paragraph(text, s["tag"])]]
    t = Table(data, colWidths=[30*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), bg),
        ("ROUNDEDCORNERS", [4]),
        ("TOPPADDING",  (0,0), (-1,-1), 2),
        ("BOTTOMPADDING",(0,0), (-1,-1), 2),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING",(0,0), (-1,-1), 4),
    ]))
    return t


def info_box(s, items, bg=BEIGE):
    """Key/value info box with light background."""
    rows = []
    for k, v in items:
        rows.append([
            Paragraph(k, s["info_key"]),
            Paragraph(v, s["info_val"]),
        ])
    t = Table(rows, colWidths=[38*mm, 115*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), bg),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING",(0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[bg, BLANC]),
        ("LINEBELOW",   (0,0), (-1,-2), 0.3, BEIGE_DARK),
    ]))
    return t


def scene_block(s, timecode, plan, dialogue, screen_text, intention,
                content_width):
    """One scene card with timecode badge + all info."""
    inner_w = content_width - 10*mm

    # timecode badge
    badge_data = [[Paragraph(timecode, s["timecode"])]]
    badge = Table(badge_data, colWidths=[28*mm])
    badge.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), GOLD_LIGHT),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING",(0,0), (-1,-1), 5),
        ("ROUNDEDCORNERS", [3]),
    ]))

    elems = [badge, Spacer(1, 2*mm)]

    if plan:
        elems.append(Paragraph(
            f'<font color="#B0A090"><b>PLAN ·</b></font>  {plan}',
            s["body"]))

    if dialogue:
        lines = [f"<i>« {l.strip()} »</i>" for l in dialogue]
        elems.append(Paragraph("<br/>".join(lines), s["dialogue"]))

    if screen_text:
        st_rows = [[Paragraph(f'<font color="#C4A882">▸</font>  {t}', s["caption"])]
                   for t in screen_text]
        st = Table(st_rows, colWidths=[inner_w - 6*mm])
        st.setStyle(TableStyle([
            ("BACKGROUND",  (0,0),(-1,-1), BEIGE),
            ("TOPPADDING",  (0,0),(-1,-1), 2),
            ("BOTTOMPADDING",(0,0),(-1,-1), 2),
            ("LEFTPADDING", (0,0),(-1,-1), 5),
            ("RIGHTPADDING",(0,0),(-1,-1), 5),
        ]))
        elems += [st, Spacer(1,1.5*mm)]

    if intention:
        elems.append(Paragraph(
            f'<font color="#C4A882"><b>↳</b></font>  <i>{intention}</i>',
            s["note"]))

    inner = Table([[elems]], colWidths=[inner_w])
    inner.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
    ]))

    outer = Table([[inner]], colWidths=[content_width])
    outer.setStyle(TableStyle([
        ("BOX",         (0,0),(-1,-1), 0.5, BEIGE_DARK),
        ("BACKGROUND",  (0,0),(-1,-1), BLANC),
        ("TOPPADDING",  (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ("LEFTPADDING", (0,0),(-1,-1), 0),
        ("RIGHTPADDING",(0,0),(-1,-1), 0),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return [outer, Spacer(1, 3*mm)]


def shot_table(s, rows, content_width):
    """Shot list table."""
    header = [
        Paragraph("#", s["body_bold"]),
        Paragraph("Plan", s["body_bold"]),
        Paragraph("Action", s["body_bold"]),
        Paragraph("Durée", s["body_bold"]),
        Paragraph("But marketing", s["body_bold"]),
    ]
    data = [header] + [
        [Paragraph(str(r[0]), s["body"]),
         Paragraph(r[1], s["body"]),
         Paragraph(r[2], s["body"]),
         Paragraph(r[3], s["body"]),
         Paragraph(r[4], s["body"])]
        for r in rows
    ]
    col_w = [8*mm, 32*mm, 48*mm, 14*mm, 51*mm]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), NOIR),
        ("TEXTCOLOR",   (0,0), (-1,0), BLANC),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[BLANC, BEIGE]),
        ("LINEBELOW",   (0,0), (-1,-1), 0.3, BEIGE_DARK),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING",(0,0),(-1,-1), 4),
    ]))
    return [t, Spacer(1, 3*mm)]


def timecode_table(s, rows, content_width):
    """Timecode / text overlay table."""
    header = [Paragraph("Timecode", s["body_bold"]),
              Paragraph("Texte à l'écran", s["body_bold"])]
    data = [header] + [
        [Paragraph(r[0], s["body"]), Paragraph(f'`{r[1]}`', s["body"])]
        for r in rows
    ]
    t = Table(data, colWidths=[22*mm, 150*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), NOIR),
        ("TEXTCOLOR",   (0,0), (-1,0), BLANC),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[BLANC, BEIGE]),
        ("LINEBELOW",   (0,0), (-1,-1), 0.3, BEIGE_DARK),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING",(0,0),(-1,-1), 4),
    ]))
    return [t, Spacer(1, 3*mm)]


def script_text_box(s, text, content_width):
    """Full script in a beige box."""
    lines = [Paragraph(l if l.strip() else "&nbsp;", s["body"])
             for l in text.strip().split("\n")]
    inner = Table([[lines]], colWidths=[content_width - 10*mm])
    inner.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
    ]))
    outer = Table([[inner]], colWidths=[content_width])
    outer.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,-1), BEIGE),
        ("BOX",         (0,0),(-1,-1), 0.5, BEIGE_DARK),
        ("TOPPADDING",  (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ("LEFTPADDING", (0,0),(-1,-1), 0),
        ("RIGHTPADDING",(0,0),(-1,-1), 0),
        ("ROUNDEDCORNERS",[4]),
    ]))
    return [outer, Spacer(1, 3*mm)]


def page_bg(canvas, doc):
    """White background + thin gold top bar."""
    canvas.saveState()
    canvas.setFillColor(BLANC)
    canvas.rect(0, 0, W, H, stroke=0, fill=1)
    # top gold line
    canvas.setFillColor(GOLD)
    canvas.rect(0, H - 4, W, 4, stroke=0, fill=1)
    # bottom footer
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(TAUPE)
    canvas.drawCentredString(W/2, 8*mm,
        "Seiya Skin — Document confidentiel — Usage UGC exclusif")
    canvas.restoreState()


# ═══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT 1 — YUKI CREAM
# ═══════════════════════════════════════════════════════════════════════════════

def build_yuki(filename):
    doc = make_doc(filename)
    s = styles()
    cw = W - 36*mm  # content width
    story = []

    # ── HERO ──────────────────────────────────────────────────────────────────
    story += [
        sp(1),
        Paragraph("SEIYA SKIN · BRIEF UGC", s["brand"]),
        Paragraph("Vidéo 1 · Yuki Cream", s["hero_title"]),
        Paragraph(
            "« Ma peau réagissait à tout. J'avais arrêté d'espérer. »",
            s["hero_sub"]),
        hr(GOLD, 1),
        sp(1),
    ]

    # ── CONTEXTE MARQUE ───────────────────────────────────────────────────────
    story += section_header(s, "01 · Contexte", "La marque & l'avatar")
    story.append(info_box(s, [
        ("Marque",       "Seiya Skin — skincare premium, inspiration japonaise"),
        ("Univers",      "Minimaliste · épuré · sensoriel · doux · moderne"),
        ("Positionnement","Soins pour peaux sensibles, réactives, fragilisées"),
        ("Promesse",     "Efficacité visible sans agresser la peau"),
        ("Avatar",       "Femme 22–40 ans · peau sensible · tiraillements · rougeurs · a tout essayé · veut se sentir enfin comprise"),
        ("Ton de marque","Doux · expert · rassurant · premium · jamais agressif"),
    ]))
    story.append(sp())

    # ── PRODUIT ───────────────────────────────────────────────────────────────
    story += section_header(s, "02 · Produit", "Yuki Cream — Crème barrière réparatrice")
    story.append(info_box(s, [
        ("Ce qu'il fait",  "Reconstruit la barrière cutanée · apaise · nourrit · protège"),
        ("Bénéfices",      "Réduit tiraillements, rougeurs et intolérance aux produits"),
        ("Formule",        "Testé dermatologiquement · vegan · cruelty-free"),
        ("Angle central",  "Elle ne se contente pas d'hydrater. Elle reconstruit."),
        ("Conversion",     "Le concept barrière cutanée explique pourquoi les autres produits ont échoué — sans accuser, en éduquant."),
    ]))
    story.append(sp())

    # ── CONCEPT ───────────────────────────────────────────────────────────────
    story += section_header(s, "03 · Concept", "Ton rôle & mécanique de persuasion")
    story.append(Paragraph(
        "Tu es la femme qui a tout essayé et qui avait arrêté d'y croire. "
        "Tu n'es pas une experte. Tu n'es pas une vendeuse. Tu es quelqu'un "
        "qui a enfin compris pourquoi sa peau réagissait à tout — et qui veut "
        "partager cette découverte avec une amie qui vit la même chose.",
        s["body"]))
    story.append(info_box(s, [
        ("Émotion à incarner",   "Soulagement sincère + espoir retrouvé"),
        ("Ce qu'elle doit ressentir", "« C'est exactement moi. Elle a trouvé quelque chose que je n'ai pas encore essayé. »"),
        ("Mécanique",            "Identification douleur → Éducation barrière → Solution crédible → Timeline → Garantie"),
        ("Durée cible",          "30–32 secondes"),
        ("Funnel",               "Top of funnel — cold traffic exclusivement"),
    ]))
    story.append(sp())

    # ── HOOKS ─────────────────────────────────────────────────────────────────
    story += section_header(s, "04 · Hooks", "5 options — 1 recommandé")
    hooks = [
        ("★  RECOMMANDÉ",
         "« Si ta peau réagit à tout — je t'explique exactement ce qui se passe. »",
         True),
        ("Option 2",
         "« J'ai la peau la plus chiante du monde — et j'ai enfin compris pourquoi. »",
         False),
        ("Option 3",
         "« Le problème c'est pas que t'as la peau sensible. C'est que ta barrière cutanée est cassée. »",
         False),
        ("Option 4",
         "« J'ai essayé 14 crèmes différentes. Pas une seule n'a réglé le vrai problème. »",
         False),
        ("Option 5",
         "« Dis-moi si ça te parle : tu mets une nouvelle crème, ta peau réagit, tu la jettes, tu recommences. »",
         False),
    ]
    for label, text, featured in hooks:
        bg = GOLD_LIGHT if featured else BEIGE
        row = [[
            Paragraph(label, s["info_key"]),
            Paragraph(text, s["dialogue"]),
        ]]
        t = Table(row, colWidths=[25*mm, cw - 25*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",  (0,0),(-1,-1), bg),
            ("TOPPADDING",  (0,0),(-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING", (0,0),(-1,-1), 5),
            ("RIGHTPADDING",(0,0),(-1,-1), 5),
            ("LINEBELOW",   (0,0),(-1,-1), 0.3, BEIGE_DARK),
        ]))
        story += [t, Spacer(1, 1*mm)]
    story.append(sp())

    # ── SCRIPT ────────────────────────────────────────────────────────────────
    story += section_header(s, "05 · Script", "Séquence par séquence")
    story.append(Paragraph(
        "Apprends ce texte. Adapte les formulations si quelque chose "
        "ne te ressemble pas — mais respecte la structure, l'ordre des idées, "
        "et la durée de chaque séquence.",
        s["note"]))
    story.append(sp())

    scenes = [
        {
            "timecode": "00:00 → 00:02  ·  HOOK",
            "plan": "Face cam · cadrage poitrine–tête · lumière naturelle · regard direct · pas de sourire",
            "dialogue": [
                "Si ta peau réagit à tout —",
                "je t'explique exactement ce qui se passe.",
            ],
            "screen": ["Peau sensible → regarde ça"],
            "intention": "Fais une légère pause après « à tout ». Comme si tu attendais qu'elle se reconnaisse. Arrêt scroll en moins de 2 secondes.",
        },
        {
            "timecode": "00:02 → 00:09  ·  IDENTIFICATION",
            "plan": "Face cam + intercut gros plan avant-bras / joue · tu passes doucement ta main dessus",
            "dialogue": [
                "Moi, ma peau tirait le matin.",
                "Elle rougissait pour rien.",
                "Je testais un nouveau produit — elle réagissait.",
                "J'avais fini par juste... arrêter d'essayer.",
            ],
            "screen": ["tiraillements · rougeurs · intolérance"],
            "intention": "Légèrement vulnérable. Pas de drama. Juste la fatigue vraie. Rythme lent, laisse les phrases respirer.",
        },
        {
            "timecode": "00:09 → 00:16  ·  RUPTURE / ÉDUCATION",
            "plan": "Face cam · légèrement plus proche · ton plus ancré · comme si tu allais révéler quelque chose",
            "dialogue": [
                "Ce que j'ai compris c'est que c'est pas 'juste ma peau'.",
                "C'est ma barrière cutanée qui était fragilisée.",
                "Et tous les produits que j'essayais —",
                "ils ne la réparaient pas.",
                "Ils l'irritaient encore plus.",
            ],
            "screen": ["Le vrai problème : barrière cutanée fragilisée"],
            "intention": "C'est LE moment de la vidéo. « Ils l'irritaient encore plus » = révélation, pas accusation. Légère émotion. Juste la vérité qui sort.",
        },
        {
            "timecode": "00:16 → 00:23  ·  SOLUTION",
            "plan": "Gros plan pot Yuki Cream · puis application texture sur joue / poignet · absorption visible (ralenti possible)",
            "dialogue": [
                "Yuki Cream, c'est une crème barrière.",
                "Elle ne se contente pas d'hydrater.",
                "Elle reconstruit.",
                "Et c'est exactement ça dont ma peau avait besoin depuis le début.",
            ],
            "screen": ["Yuki Cream · crème barrière réparatrice"],
            "intention": "« Reconstruit » = dit plus lentement. C'est l'ancrage central. Geste d'application : lent, sensoriel. La femme doit avoir envie de faire ce geste.",
        },
        {
            "timecode": "00:23 → 00:28  ·  PREUVE",
            "plan": "Face cam · peau lumineuse · sourire naturel · ton confiant et détendu",
            "dialogue": [
                "Semaine un — je tiraillais moins.",
                "Semaine deux — plus de rougeurs le matin.",
                "Maintenant j'applique. Et j'oublie.",
                "C'est tout ce que je voulais.",
            ],
            "screen": ["S1 : moins de tiraillements", "S2 : peau plus calme"],
            "intention": "« J'applique. Et j'oublie. » — pause entre les deux. Court silence. « C'est tout ce que je voulais » = sincère, pas triomphal.",
        },
        {
            "timecode": "00:28 → 00:32  ·  CTA",
            "plan": "Face cam · pot Yuki Cream dans la main · tenu naturellement",
            "dialogue": [
                "Le lien est en bio.",
                "Et ils ont une garantie 30 jours —",
                "donc tu risques vraiment rien.",
            ],
            "screen": ["Essai 30 jours · Remboursée si pas convaincue", "Lien en bio ↓"],
            "intention": "Ton factuel. Pas vendeur. Presque détaché. « tu risques vraiment rien » = évidence, pas argument de vente.",
        },
    ]

    for sc in scenes:
        story += scene_block(
            s, sc["timecode"], sc["plan"], sc["dialogue"],
            sc["screen"], sc["intention"], cw)

    story.append(PageBreak())

    # ── TEXTE COMPLET ─────────────────────────────────────────────────────────
    story += section_header(s, "06 · Mémo", "Texte complet à apprendre")
    script_full = """Si ta peau réagit à tout —
je t'explique exactement ce qui se passe.

Moi, ma peau tirait le matin.
Elle rougissait pour rien.
Je testais un nouveau produit — elle réagissait.
J'avais fini par juste... arrêter d'essayer.

Ce que j'ai compris c'est que c'est pas 'juste ma peau'.
C'est ma barrière cutanée qui était fragilisée.
Et tous les produits que j'essayais —
ils ne la réparaient pas. Ils l'irritaient encore plus.

[voix off sur les plans gros plan]
Yuki Cream, c'est une crème barrière.
Elle ne se contente pas d'hydrater. Elle reconstruit.
Et c'est exactement ça dont ma peau avait besoin depuis le début.

Semaine un — je tiraillais moins.
Semaine deux — plus de rougeurs le matin.
Maintenant j'applique. Et j'oublie. C'est tout ce que je voulais.

Le lien est en bio.
Et ils ont une garantie 30 jours —
donc tu risques vraiment rien."""
    story += script_text_box(s, script_full, cw)

    # ── DIRECTION TOURNAGE ────────────────────────────────────────────────────
    story += section_header(s, "07 · Tournage", "Direction créative")
    story.append(info_box(s, [
        ("Vibe",         "Tu parles à une amie — pas à une caméra. Sincérité avant tout."),
        ("Ton de voix",  "Calme · posé · légèrement confidentiel · aucune excitation"),
        ("Maquillage",   "Rien ou presque. Peau naturelle. Une imperfection est parfaite."),
        ("Tenue",        "Haut uni, couleur douce — blanc, crème, beige. Rien de voyant."),
        ("Décor",        "Salle de bain épurée ou coin chambre blanc. Lumière de fenêtre. Pas de désordre."),
        ("Lumière",      "Lumière naturelle douce ou ring light diffusé. Peau lisible, pas parfaite."),
        ("Rythme montage","Lent et posé. Jump cuts légers sur voix off. Pas de transitions flashy."),
        ("Émotion",      "70% calme et sincère · 30% légèrement émue sur « j'avais arrêté d'essayer »"),
        ("À éviter",     "Sourire forcé au début · ton exalté · surjeu · phrases récitées · ambiance pub TV"),
    ]))
    story.append(sp())

    # ── SHOT LIST ─────────────────────────────────────────────────────────────
    story += section_header(s, "08 · Shot list", "Plans à filmer")
    story += shot_table(s, [
        (1, "Face cam — buste",          "Accroche directe caméra",                          "2s", "Hook — arrêt scroll"),
        (2, "Gros plan avant-bras/joue", "Caresse douce de la peau",                         "3s", "Identification visuelle du problème"),
        (3, "Face cam — buste",          "« j'avais arrêté d'essayer »",                     "5s", "Empathie & mirroring"),
        (4, "Face cam — rapproché",      "Révélation barrière cutanée",                      "5s", "Éducation & curiosité"),
        (5, "Gros plan Yuki Cream",      "Ouverture, texture visible",                       "2s", "Présentation produit premium"),
        (6, "Gros plan application",     "Texture appliquée, absorption",                    "3s", "Désir sensoriel"),
        (7, "Face cam — peau lumineuse", "Résultat, sourire naturel",                        "4s", "Aspiration"),
        (8, "Face cam + produit",        "CTA + garantie",                                   "4s", "Conversion finale"),
    ], cw)

    # ── TEXTES ÉCRAN ──────────────────────────────────────────────────────────
    story += section_header(s, "09 · Textes écran", "Récapitulatif montage")
    story += timecode_table(s, [
        ("00:01", "Peau sensible → regarde ça"),
        ("00:04", "tiraillements · rougeurs · intolérance"),
        ("00:11", "Le vrai problème : barrière cutanée fragilisée"),
        ("00:17", "Yuki Cream · crème barrière réparatrice"),
        ("00:24", "S1 : moins de tiraillements"),
        ("00:25", "S2 : peau plus calme"),
        ("00:29", "Essai 30 jours · Remboursée si pas convaincue"),
        ("00:30", "Lien en bio ↓"),
    ], cw)

    # ── LIVRAISON ─────────────────────────────────────────────────────────────
    story += section_header(s, "10 · Livraison", "Consignes de rendu")
    story.append(info_box(s, [
        ("Format",       "MP4 · H.264 · 1080×1920 minimum (9:16 vertical)"),
        ("Fichiers",     "① Version complète avec textes  ② Sans textes  ③ Hook seul (00:00→00:03)"),
        ("Prises mini",  "3× hook · 2× séquence complète · 2× gros plan application (dont 1 ralenti)"),
        ("Questions",    "Écris-nous avant de tourner. On préfère clarifier maintenant."),
    ]))

    doc.build(story, onFirstPage=page_bg, onLaterPages=page_bg)
    print(f"✓ {filename}")


# ═══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT 2 — SHIZUKU SERUM
# ═══════════════════════════════════════════════════════════════════════════════

def build_shizuku(filename):
    doc = make_doc(filename)
    s = styles()
    cw = W - 36*mm
    story = []

    story += [
        sp(1),
        Paragraph("SEIYA SKIN · BRIEF UGC", s["brand"]),
        Paragraph("Vidéo 2 · Shizuku Serum", s["hero_title"]),
        Paragraph(
            "« La peau que j'avais avant — je l'ai retrouvée. »",
            s["hero_sub"]),
        hr(GOLD, 1),
        sp(1),
    ]

    story += section_header(s, "01 · Contexte", "La marque & l'avatar")
    story.append(info_box(s, [
        ("Marque",       "Seiya Skin — skincare premium, inspiration japonaise"),
        ("Univers",      "Minimaliste · épuré · sensoriel · doux · moderne"),
        ("Positionnement","Soins pour peaux sensibles, réactives, fragilisées"),
        ("Promesse",     "Efficacité visible sans agresser la peau"),
        ("Avatar",       "Femme 22–40 ans · veut un éclat naturel · a essayé des sérums sans résultat durable · veut simple et efficace"),
        ("Ton de marque","Doux · expert · rassurant · premium · jamais agressif"),
    ]))
    story.append(sp())

    story += section_header(s, "02 · Produit", "Shizuku Serum — Sérum hydratation, apaisement, éclat")
    story.append(info_box(s, [
        ("Ce qu'il fait",  "Hydrate en profondeur · peau + souple + rebondie + lumineuse · apaise les peaux sensibles"),
        ("Texture",        "Légère · absorption immédiate · non grasse"),
        ("Formule",        "Testé dermatologiquement · vegan · cruelty-free"),
        ("Angle central",  "Une vraie hydratation change tout. Et ça se voit."),
        ("Conversion",     "Le sérum vend du désir visuel. Texture filmable, résultat enviable. « Une goutte, un résultat en 2 semaines » = simple et crédible."),
    ]))
    story.append(sp())

    story += section_header(s, "03 · Concept", "Ton rôle & mécanique")
    story.append(Paragraph(
        "Tu es la femme qui a retrouvé l'éclat de sa peau — pas grâce à plus de maquillage, "
        "mais grâce à un seul geste quotidien. Tu partages quelque chose qui te rend fière sans "
        "avoir besoin de le crier. Comme quand ta peau est belle le matin et que tu le remarques "
        "dans le miroir avant même de penser à te maquiller.", s["body"]))
    story.append(info_box(s, [
        ("Émotion à incarner",   "Désir doux + fierté calme + satisfaction naturelle"),
        ("Ce qu'elle doit ressentir", "« Je veux cette peau. Je veux ce qu'elle ressent. »"),
        ("Mécanique",            "Aspiration incarnée → Tension passée → Démonstration sensorielle → Timeline → Désir d'achat"),
        ("Durée cible",          "26–28 secondes"),
        ("Funnel",               "Top / Mid funnel — cold traffic et retargeting léger"),
    ]))
    story.append(sp())

    story += section_header(s, "04 · Hooks", "5 options — 1 recommandé")
    hooks = [
        ("★  RECOMMANDÉ",
         "« T'as déjà eu cette peau — souple, fraîche, lumineuse, sans avoir rien fait de spécial ? Ce sérum me l'a rendue. »",
         True),
        ("Option 2",
         "« Il m'a fallu 6 sérums pour trouver celui qui fait enfin quelque chose. »",
         False),
        ("Option 3",
         "« Ma peau avait l'air fatigué peu importe ce que je faisais — jusqu'à il y a 3 semaines. »",
         False),
        ("Option 4",
         "« Le glow que t'as quand tu t'hydrates vraiment bien — ce sérum fait ça en 60 secondes. »",
         False),
        ("Option 5",
         "« Je voulais cette peau 'elle a bonne mine' sans fond de teint. J'ai trouvé comment. »",
         False),
    ]
    for label, text, featured in hooks:
        bg = GOLD_LIGHT if featured else BEIGE
        row = [[Paragraph(label, s["info_key"]), Paragraph(text, s["dialogue"])]]
        t = Table(row, colWidths=[25*mm, cw - 25*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",  (0,0),(-1,-1), bg),
            ("TOPPADDING",  (0,0),(-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING", (0,0),(-1,-1), 5),
            ("RIGHTPADDING",(0,0),(-1,-1), 5),
            ("LINEBELOW",   (0,0),(-1,-1), 0.3, BEIGE_DARK),
        ]))
        story += [t, Spacer(1, 1*mm)]
    story.append(sp())

    story += section_header(s, "05 · Script", "Séquence par séquence")
    story.append(Paragraph(
        "Adapte les formulations si quelque chose ne te ressemble pas — "
        "mais respecte la structure, l'ordre des idées, et la durée.",
        s["note"]))
    story.append(sp())

    scenes = [
        {
            "timecode": "00:00 → 00:03  ·  HOOK",
            "plan": "Face cam · cadrage serré · peau lumineuse visible · lumière naturelle · regard calme · léger sourire de satisfaction",
            "dialogue": [
                "T'as déjà eu cette peau —",
                "souple, fraîche, lumineuse,",
                "sans avoir rien fait de spécial ?",
                "Ce sérum me l'a rendue.",
            ],
            "screen": ["Le sérum qui a tout changé →"],
            "intention": "Les mots « souple, fraîche, lumineuse » doivent être dits lentement, presque avec plaisir. La femme qui regarde doit VOULOIR ce que tu ressens. En 3 secondes.",
        },
        {
            "timecode": "00:03 → 00:08  ·  TENSION",
            "plan": "Face cam · ton plus neutre · comme si tu racontais ce qui existait avant",
            "dialogue": [
                "Avant, ma peau avait toujours l'air un peu terne.",
                "Un peu fatiguée. Pourtant je la soignais.",
                "Le problème —",
                "c'est que je l'hydratais en surface.",
                "Pas vraiment en profondeur.",
            ],
            "screen": ["hydrater en surface ≠ hydrater vraiment"],
            "intention": "« Pourtant je la soignais » = la phrase la plus importante. Elle valide l'effort passé de la cliente. Ton factuel, pas résigné.",
        },
        {
            "timecode": "00:08 → 00:18  ·  DÉMONSTRATION",
            "plan": "Gros plan flacon → une goutte prélevée → application joue / poignet · geste lent, sensoriel · absorption visible · ralenti possible",
            "dialogue": [
                "Shizuku Serum.",
                "Une goutte le matin, avant la crème.",
                "Tu le masses — il pénètre en quelques secondes.",
                "Et ta peau retient l'humidité toute la journée.",
                "Pas juste les vingt premières minutes.",
            ],
            "screen": ["1 goutte · absorption immédiate", "hydratation qui dure"],
            "intention": "Le geste d'application est le cœur de cette vidéo. Lent. Précis. Presque rituel. « Pas juste les vingt premières minutes » = dis-le avec un léger sourire.",
        },
        {
            "timecode": "00:18 → 00:24  ·  RÉSULTAT",
            "plan": "Face cam · peau lumineuse · lumière naturelle pleine face · pas de maquillage · regard caméra",
            "dialogue": [
                "En deux semaines — ma peau était plus souple.",
                "Mon teint était plus uni.",
                "J'avais cet éclat que j'essayais d'avoir avec du fond de teint.",
                "Là — c'est juste ma peau.",
            ],
            "screen": ["2 semaines · peau + souple · teint + uni", "c'est juste ma peau."],
            "intention": "« Là — c'est juste ma peau. » Pause avant. Pause après. Fierté calme. Pas d'exclamation. Juste la certitude.",
        },
        {
            "timecode": "00:24 → 00:28  ·  CTA",
            "plan": "Face cam · flacon Shizuku dans la main · en disant « ta peau ressemble pas à ça », geste discret vers ton visage",
            "dialogue": [
                "Le lien est en bio.",
                "Et si dans 30 jours ta peau ressemble pas à ça —",
                "ils remboursent.",
            ],
            "screen": ["Essai 30 jours · Remboursée sinon", "Lien en bio ↓"],
            "intention": "Le geste vers le visage rappelle l'aspiration une dernière fois. Ton : factuel, serein, pas vendeur.",
        },
    ]
    for sc in scenes:
        story += scene_block(
            s, sc["timecode"], sc["plan"], sc["dialogue"],
            sc["screen"], sc["intention"], cw)

    story.append(PageBreak())

    story += section_header(s, "06 · Mémo", "Texte complet à apprendre")
    script_full = """T'as déjà eu cette peau —
souple, fraîche, lumineuse, sans avoir rien fait de spécial ?
Ce sérum me l'a rendue.

Avant, ma peau avait toujours l'air un peu terne.
Un peu fatiguée. Pourtant je la soignais.
Le problème — c'est que je l'hydratais en surface.
Pas vraiment en profondeur.

[voix off sur les plans gros plan]
Shizuku Serum. Une goutte le matin, avant la crème.
Tu le masses — il pénètre en quelques secondes.
Et ta peau retient l'humidité toute la journée.
Pas juste les vingt premières minutes.

En deux semaines — ma peau était plus souple.
Mon teint était plus uni.
J'avais cet éclat que j'essayais d'avoir avec du fond de teint.
Là — c'est juste ma peau.

Le lien est en bio.
Et si dans 30 jours ta peau ressemble pas à ça — ils remboursent."""
    story += script_text_box(s, script_full, cw)

    story += section_header(s, "07 · Tournage", "Direction créative")
    story.append(info_box(s, [
        ("Vibe",         "Quelqu'un qui a trouvé quelque chose et veut le partager — pas le vendre. La vidéo doit sentir le matin."),
        ("Ton de voix",  "Chaleureux · légèrement enthousiaste · jamais excessif"),
        ("Maquillage",   "AUCUN ou base ultra légère. L'éclat doit venir de ta peau — pas d'un fond de teint. Règle absolue."),
        ("Tenue",        "Peignoir léger ou haut simple avec épaule visible. Atmosphère matinale intime."),
        ("Décor",        "Salle de bain épurée ou coiffeuse. Carrelage blanc. Serviette blanche, verre d'eau."),
        ("Lumière",      "Lumière naturelle en priorité absolue. Peau lumineuse naturellement, sans filtre."),
        ("Rythme montage","Légèrement plus rythmé sur le gros plan sérum. Ralenti possible sur l'absorption."),
        ("Émotion",      "Satisfaction douce + légère fierté. Pas d'euphorie. Tu as trouvé ce que tu cherchais."),
        ("À éviter",     "Filtre beauté · peau trop parfaite · enthousiasme forcé · plans trop longs sans voix"),
    ]))
    story.append(sp())

    story += section_header(s, "08 · Shot list", "Plans à filmer")
    story += shot_table(s, [
        (1, "Face cam — buste",         "Peau lumineuse visible, hook aspiration",           "3s", "Aspiration immédiate"),
        (2, "Face cam",                 "« pourtant je la soignais »",                       "4s", "Identification"),
        (3, "Gros plan flacon sérum",   "Flacon posé, lumière dessus",                       "1,5s","Désir visuel produit"),
        (4, "Gros plan main",           "Une goutte de sérum prélevée",                      "1,5s","Rituel, sensorialité"),
        (5, "Gros plan joue/poignet",   "Application et absorption visible",                 "4s", "Désir tactile"),
        (6, "Face cam",                 "Résultat semaine 2, ton plus vivant",               "4s", "Preuve progressive"),
        (7, "Gros plan peau",           "Peau lumineuse rebondie en close-up",               "2s", "Aspiration maximale"),
        (8, "Face cam + produit",       "CTA + garantie, geste vers le visage",              "4s", "Conversion"),
    ], cw)

    story += section_header(s, "09 · Textes écran", "Récapitulatif montage")
    story += timecode_table(s, [
        ("00:01", "Le sérum qui a tout changé →"),
        ("00:06", "hydrater en surface ≠ hydrater vraiment"),
        ("00:11", "1 goutte · absorption immédiate"),
        ("00:14", "hydratation qui dure"),
        ("00:20", "2 semaines · peau + souple · teint + uni"),
        ("00:22", "c'est juste ma peau."),
        ("00:25", "Essai 30 jours · Remboursée sinon"),
        ("00:26", "Lien en bio ↓"),
    ], cw)

    story += section_header(s, "10 · Livraison", "Consignes de rendu")
    story.append(info_box(s, [
        ("Format",       "MP4 · H.264 · 1080×1920 minimum (9:16 vertical)"),
        ("Fichiers",     "① Version complète avec textes  ② Sans textes  ③ Hook seul (00:00→00:03)"),
        ("Prises mini",  "3× hook · 2× séquence complète · 2× gros plan application (dont 1 ralenti)"),
        ("Questions",    "Écris-nous avant de tourner. On préfère clarifier maintenant."),
    ]))

    doc.build(story, onFirstPage=page_bg, onLaterPages=page_bg)
    print(f"✓ {filename}")


# ═══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT 3 — ASAHI CREAM
# ═══════════════════════════════════════════════════════════════════════════════

def build_asahi(filename):
    doc = make_doc(filename)
    s = styles()
    cw = W - 36*mm
    story = []

    story += [
        sp(1),
        Paragraph("SEIYA SKIN · BRIEF UGC", s["brand"]),
        Paragraph("Vidéo 3 · Asahi Cream", s["hero_title"]),
        Paragraph(
            "« J'ai arrêté de me battre contre ma peau. J'ai commencé à l'écouter. »",
            s["hero_sub"]),
        hr(GOLD, 1),
        sp(1),
    ]

    story += section_header(s, "01 · Contexte", "La marque & l'avatar")
    story.append(info_box(s, [
        ("Marque",       "Seiya Skin — skincare premium, inspiration japonaise"),
        ("Univers",      "Minimaliste · épuré · sensoriel · doux · moderne"),
        ("Positionnement","Soins pour peaux sensibles, réactives, fragilisées"),
        ("Promesse",     "Efficacité visible sans agresser la peau"),
        ("Avatar",       "Femme 22–40 ans · a tout essayé · est sceptique · veut des preuves pas des slogans · veut arrêter de chercher"),
        ("Ton de marque","Doux · expert · rassurant · premium · jamais agressif"),
    ]))
    story.append(sp())

    story += section_header(s, "02 · Produit", "Asahi Cream — Crème de jour éclat et confort")
    story.append(info_box(s, [
        ("Ce qu'il fait",  "Confort et éclat dès le matin · peau + souple + unifiée + lumineuse"),
        ("Format",         "Grand format 50ml — plus de produit, plus longtemps"),
        ("Formule",        "Testé dermatologiquement · vegan · cruelty-free"),
        ("Angle central",  "Les autres crèmes couvraient. Asahi Cream, elle construit."),
        ("Conversion",     "Before/after matin très filmable et crédible. La différenciation « construire vs couvrir » est puissante et mémorable."),
    ]))
    story.append(sp())

    story += section_header(s, "03 · Concept", "Ton rôle & mécanique")
    story.append(Paragraph(
        "Tu es la femme revenue de tout. Pas cynique. Pas amère. Juste quelqu'un qui a essayé "
        "beaucoup de choses, qui a été déçue plusieurs fois, qui avait baissé les attentes — "
        "et qui a quand même essayé une dernière fois. Et cette fois, c'était différent. "
        "C'est cet arc narratif que tu incarnes du début à la fin.", s["body"]))
    story.append(info_box(s, [
        ("Émotion à incarner",   "Confiance calme + réconciliation avec son miroir du matin"),
        ("Ce qu'elle doit ressentir", "« Elle était comme moi. Ça a marché pour elle. Peut-être pour moi aussi. »"),
        ("Mécanique",            "Identification totale → Preuve d'usage progressive → Différenciation → Pic émotionnel → Garantie"),
        ("Durée cible",          "35–38 secondes"),
        ("Funnel",               "Mid / Bottom funnel — retargeting principal + cold sceptique"),
    ]))
    story.append(sp())

    story += section_header(s, "04 · Hooks", "5 options — 1 recommandé")
    hooks = [
        ("★  RECOMMANDÉ",
         "« J'avais essayé tellement de crèmes que j'avais arrêté d'y croire. Et puis j'ai essayé Asahi Cream. »",
         True),
        ("Option 2",
         "« Je croyais sincèrement que j'avais juste la peau impossible. J'avais tort. »",
         False),
        ("Option 3",
         "« Voilà ma routine du matin en 4 minutes — et pourquoi j'ai arrêté de tester des nouveaux produits. »",
         False),
        ("Option 4",
         "« J'ai commandé Asahi Cream en me disant 'encore un essai'. C'est le seul que j'ai gardé. »",
         False),
        ("Option 5",
         "« Si t'as la peau sensible et que t'en as marre de faire des tests — regarde ça. »",
         False),
    ]
    for label, text, featured in hooks:
        bg = GOLD_LIGHT if featured else BEIGE
        row = [[Paragraph(label, s["info_key"]), Paragraph(text, s["dialogue"])]]
        t = Table(row, colWidths=[25*mm, cw - 25*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",  (0,0),(-1,-1), bg),
            ("TOPPADDING",  (0,0),(-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING", (0,0),(-1,-1), 5),
            ("RIGHTPADDING",(0,0),(-1,-1), 5),
            ("LINEBELOW",   (0,0),(-1,-1), 0.3, BEIGE_DARK),
        ]))
        story += [t, Spacer(1, 1*mm)]
    story.append(sp())

    story += section_header(s, "05 · Script", "Séquence par séquence")
    story.append(Paragraph(
        "Adapte les formulations si quelque chose ne te ressemble pas — "
        "mais respecte la structure, l'ordre des idées, et la durée.",
        s["note"]))
    story.append(sp())

    scenes = [
        {
            "timecode": "00:00 → 00:03  ·  HOOK",
            "plan": "Face cam · peau naturelle sans maquillage · lumière matin · regard direct · légèrement fatigué · pas de sourire",
            "dialogue": [
                "J'avais essayé tellement de crèmes",
                "que j'avais arrêté d'y croire.",
                "Et puis j'ai essayé Asahi Cream.",
            ],
            "screen": ["J'avais tout essayé.", "Jusqu'à ça."],
            "intention": "Deux phrases. La première crée l'identification totale. La deuxième ouvre la boucle narrative. Dis « j'avais arrêté d'y croire » avec la fatigue vraie de quelqu'un qui l'a vraiment vécu.",
        },
        {
            "timecode": "00:03 → 00:10  ·  IDENTIFICATION PROFONDE",
            "plan": "Face cam · même atmosphère · regard qui descend légèrement comme un souvenir",
            "dialogue": [
                "Ma peau était sensible.",
                "Elle réagissait à tout.",
                "Elle tirait le matin.",
                "Elle rougissait au moindre changement.",
                "Et à force —",
                "j'avais juste appris à vivre avec l'inconfort.",
                "Comme si c'était normal.",
            ],
            "screen": ["sensible · réactive · inconfortable", "« j'avais appris à vivre avec. »"],
            "intention": "Empathie maximum. Chaque phrase respire. « Comme si c'était normal » = légère ironie douce sur soi-même. L'avatar pense : « c'est exactement ce que je fais. »",
        },
        {
            "timecode": "00:10 → 00:20  ·  APPLICATION",
            "plan": "Face cam before → gros plan pot Asahi Cream → texture prélevée → application joue (geste vers le haut) · ralenti possible",
            "dialogue": [
                "Le premier matin —",
                "texture légère. Absorption immédiate.",
                "Aucune réaction.",
                "Pour ma peau — c'était déjà inattendu.",
            ],
            "screen": ["Jour 1 : aucune réaction.", "Pour moi — c'était déjà énorme."],
            "intention": "« Pour ma peau — c'était déjà inattendu » = phrase la plus anti-marketing du script. Elle dit : je ne m'emballe pas. C'est ce qui rend la suite crédible.",
        },
        {
            "timecode": "00:20 → 00:28  ·  PROGRESSION",
            "plan": "Face cam · ton légèrement plus animé · la transformation commence à se sentir dans la voix",
            "dialogue": [
                "Semaine une — ma peau était plus souple le soir que le matin.",
                "Pour moi ça n'arrivait jamais.",
                "Semaine deux — mon teint était plus uni. Plus lumineux.",
                "Et j'ai compris pourquoi les autres crèmes ne marchaient pas —",
                "elles couvraient.",
                "Asahi Cream, elle construit.",
            ],
            "screen": ["S1 : peau plus souple le soir", "S2 : teint + uni · + lumineux", "COUVRIR  ≠  CONSTRUIRE"],
            "intention": "« Pour moi ça n'arrivait jamais. » = dit simplement, en aparté. Crédibilise tout. « Elles couvraient. Asahi Cream, elle construit. » = pause entre les deux. Les deux mots les plus importants de la vidéo.",
        },
        {
            "timecode": "00:28 → 00:33  ·  PIC ÉMOTIONNEL",
            "plan": "Face cam · peau lumineuse · regard vers caméra puis légèrement de côté comme vers le miroir imaginaire",
            "dialogue": [
                "Maintenant je mets moins de maquillage le matin.",
                "Pas parce que j'ai renoncé à prendre soin de moi.",
                "Parce que j'ai moins besoin de cacher.",
            ],
            "screen": ["moins de maquillage.", "parce que moins besoin de cacher."],
            "intention": "Moment émotionnel le plus fort de la vidéo. Dit doucement. Avec une vraie douceur. Pas d'exclamation. Juste la paix de quelqu'un qui a arrêté de se battre.",
        },
        {
            "timecode": "00:33 → 00:38  ·  CTA",
            "plan": "Face cam · pot Asahi Cream dans la main · regard direct caméra · tenu naturellement",
            "dialogue": [
                "Ils ont mis une garantie 30 jours.",
                "Ce qui veut dire que même si t'es sceptique",
                "— comme je l'étais —",
                "t'as rien à perdre à essayer.",
                "Le lien est en bio.",
            ],
            "screen": ["Garantie 30 jours · Pour les sceptiques aussi.", "Lien en bio ↓"],
            "intention": "« comme je l'étais » = inclusion parfaite. Tu te places dans le camp de celle qui regardait avec méfiance. Tu n'es pas la vendeuse. Tu es la cliente convertie.",
        },
    ]
    for sc in scenes:
        story += scene_block(
            s, sc["timecode"], sc["plan"], sc["dialogue"],
            sc["screen"], sc["intention"], cw)

    story.append(PageBreak())

    story += section_header(s, "06 · Mémo", "Texte complet à apprendre")
    script_full = """J'avais essayé tellement de crèmes
que j'avais arrêté d'y croire.
Et puis j'ai essayé Asahi Cream.

Ma peau était sensible. Elle réagissait à tout.
Elle tirait le matin. Elle rougissait au moindre changement.
Et à force — j'avais juste appris à vivre avec l'inconfort.
Comme si c'était normal.

[voix off sur les plans gros plan]
Le premier matin — texture légère. Absorption immédiate.
Aucune réaction. Pour ma peau — c'était déjà inattendu.

Semaine une — ma peau était plus souple le soir que le matin.
Pour moi ça n'arrivait jamais.
Semaine deux — mon teint était plus uni. Plus lumineux.
Et j'ai compris pourquoi les autres crèmes ne marchaient pas —
elles couvraient. Asahi Cream, elle construit.

Maintenant je mets moins de maquillage le matin.
Pas parce que j'ai renoncé à prendre soin de moi.
Parce que j'ai moins besoin de cacher.

Ils ont mis une garantie 30 jours.
Ce qui veut dire que même si t'es sceptique — comme je l'étais —
t'as rien à perdre à essayer. Le lien est en bio."""
    story += script_text_box(s, script_full, cw)

    story += section_header(s, "07 · Tournage", "Direction créative")
    story.append(info_box(s, [
        ("Vibe",         "Femme revenue de tout. Pas cynique. L'arc : résignation → espoir prudent → paix. Du début à la fin."),
        ("Ton de voix",  "Légèrement las au début · progressivement plus ancré · sobre dans l'enthousiasme"),
        ("Maquillage",   "Séq. 1–3 : aucun. Séq. 4–6 : léger glow naturel. Différence visible mais non artificielle."),
        ("Tenue",        "Pyjama ou haut très simple. Cheveux naturels. Atmosphère lève-tôt authentique."),
        ("Décor",        "Salle de bain ou table de nuit. Très épuré. Serviette blanche, verre d'eau. Asahi Cream seul visible."),
        ("Lumière",      "Lumière chaude de matin. Fenêtre de côté. Le before honnête. Le after lumineux sans filtre."),
        ("Rythme montage","Lent jusqu'au milieu · légèrement + rythmé sur la progression S1/S2 · ralenti sur l'application"),
        ("Émotion",      "Las au début → ancré → paix douce à la fin. Le voyage émotionnel doit s'entendre dans la voix."),
        ("À éviter",     "Enthousiasme excessif · peau trop parfaite au départ · ton vendeur à n'importe quel moment"),
    ]))
    story.append(sp())

    story += section_header(s, "08 · Shot list", "Plans à filmer")
    story += shot_table(s, [
        (1,  "Face cam — peau naturelle",   "Hook, regard direct, légèrement fatigué",         "3s",  "Identification totale"),
        (2,  "Face cam",                    "« j'avais appris à vivre avec l'inconfort »",      "6s",  "Empathie profonde"),
        (3,  "Face cam — before matin",     "Point de départ du rituel, peau honnête",          "1,5s","Before crédible"),
        (4,  "Gros plan pot Asahi",         "Produit ouvert, texture visible",                  "1s",  "Présentation premium"),
        (5,  "Gros plan main",              "Texture Asahi prélevée",                           "1s",  "Sensorialité"),
        (6,  "Gros plan joue",              "Application, massage doux vers le haut",           "3s",  "Rituel, absorption"),
        (7,  "Face cam",                    "« Pour ma peau c'était déjà inattendu »",          "4s",  "Anti-hype, crédibilité"),
        (8,  "Face cam",                    "Progression semaine 1 / semaine 2",                "5s",  "Timeline concrète"),
        (9,  "Face cam",                    "« j'ai moins besoin de cacher »",                  "4s",  "Pic émotionnel"),
        (10, "Face cam + produit",          "CTA + garantie + sceptiques",                      "5s",  "Conversion finale"),
    ], cw)

    story += section_header(s, "09 · Textes écran", "Récapitulatif montage")
    story += timecode_table(s, [
        ("00:00", "J'avais tout essayé."),
        ("00:01", "Jusqu'à ça."),
        ("00:05", "sensible · réactive · inconfortable"),
        ("00:08", "« j'avais appris à vivre avec. »"),
        ("00:13", "Jour 1 : aucune réaction."),
        ("00:14", "Pour moi — c'était déjà énorme."),
        ("00:22", "S1 : peau plus souple le soir"),
        ("00:24", "S2 : teint + uni · + lumineux"),
        ("00:26", "COUVRIR  ≠  CONSTRUIRE"),
        ("00:29", "moins de maquillage."),
        ("00:31", "parce que moins besoin de cacher."),
        ("00:34", "Garantie 30 jours · Pour les sceptiques aussi."),
        ("00:36", "Lien en bio ↓"),
    ], cw)

    story += section_header(s, "10 · Livraison", "Consignes de rendu")
    story.append(info_box(s, [
        ("Format",       "MP4 · H.264 · 1080×1920 minimum (9:16 vertical)"),
        ("Fichiers",     "① Version complète avec textes  ② Sans textes  ③ Hook seul (00:00→00:03)  ④ Plan application seul"),
        ("Prises mini",  "3× hook · 2× séquence complète · 2× application (dont 1 ralenti) · 2× « j'ai moins besoin de cacher »"),
        ("Questions",    "Écris-nous avant de tourner. On préfère clarifier maintenant."),
    ]))

    doc.build(story, onFirstPage=page_bg, onLaterPages=page_bg)
    print(f"✓ {filename}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.chdir("/home/user/Seiya-skin")
    build_yuki("brief-ugc-yuki-cream.pdf")
    build_shizuku("brief-ugc-shizuku-serum.pdf")
    build_asahi("brief-ugc-asahi-cream.pdf")
    print("\nDone — 3 PDFs generated.")
