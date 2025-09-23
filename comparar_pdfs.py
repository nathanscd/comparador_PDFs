import pdfplumber
import difflib
import hashlib
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def extract_paragraphs(pdf_path):
    paragraphs = []
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        # separa em parágrafos: quebra dupla de linha
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs


def paragraph_hash(paragraph):
    """Retorna um hash MD5 para um parágrafo normalizado."""
    normalized = " ".join(paragraph.lower().split())  # remove espaços extras
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def compare_pdfs(pdf1, pdf2, similarity_threshold=0.8):
    p1 = extract_paragraphs(pdf1)
    p2 = extract_paragraphs(pdf2)

    # cria índices de hash
    hash_map1 = {paragraph_hash(p): p for p in p1}
    hash_map2 = {paragraph_hash(p): p for p in p2}

    iguais = []
    diferentes = []

    # primeiro passo: detectar iguais via hash
    for h, para1 in hash_map1.items():
        if h in hash_map2:
            iguais.append((para1, hash_map2[h]))

    # remove os já processados
    usados1 = set([p for p, _ in iguais])
    usados2 = set([p for _, p in iguais])

    restantes1 = [p for p in p1 if p not in usados1]
    restantes2 = [p for p in p2 if p not in usados2]

    # segundo passo: verificar similaridade com difflib
    for para1 in restantes1:
        match_found = False
        for para2 in restantes2:
            ratio = difflib.SequenceMatcher(None, para1, para2).ratio()
            if ratio >= similarity_threshold:
                iguais.append((para1, para2))
                match_found = True
                break
        if not match_found:
            diferentes.append((para1, None))

    # verificar os que sobraram no PDF2
    for para2 in restantes2:
        match_found = False
        for para1 in restantes1:
            ratio = difflib.SequenceMatcher(None, para1, para2).ratio()
            if ratio >= similarity_threshold:
                match_found = True
                break
        if not match_found:
            diferentes.append((None, para2))

    return iguais, diferentes


def gerar_relatorio_pdf(iguais, diferentes, output_pdf="comparacao.pdf"):
    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    styles = getSampleStyleSheet()

    # estilo para preservar formatação original
    mono_style = ParagraphStyle(
        "Mono",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=9,
        leading=12,
        textColor=colors.black,
    )

    story = []
    story.append(Paragraph("Relatório de Comparação de PDFs", styles["Title"]))
    story.append(Spacer(1, 20))

    # Iguais
    story.append(Paragraph("Parágrafos Iguais ou Muito Parecidos:", styles["Heading2"]))
    for p1, p2 in iguais:
        story.append(Preformatted(f"{p1}", mono_style))
        story.append(Preformatted(f"{p2}", mono_style))
        story.append(Paragraph("Resultado: IGUAL", styles["Normal"]))
        story.append(Spacer(1, 15))

    # Diferentes
    story.append(Spacer(1, 20))
    story.append(Paragraph("Parágrafos Diferentes:", styles["Heading2"]))
    for p1, p2 in diferentes:
        if p1:
            story.append(Preformatted(f"{p1}", mono_style))
        if p2:
            story.append(Preformatted(f"{p2}", mono_style))
        story.append(Paragraph("Resultado: DIFERENTE", styles["Normal"]))
        story.append(Spacer(1, 15))

    doc.build(story)
    print(f"Relatório gerado: {output_pdf}")

if __name__ == "__main__":
    # >>>>>>>> TROQUE AQUI OS NOMES DOS PDFs <<<<<<<<
    pdf1 = "GED-150179_Ago_25.pdf"
    pdf2 = "GED 150179 - Especificação Técnica de Medidor Eletrônico Direto e Indireto-rev.pdf"
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    iguais, diferentes = compare_pdfs(pdf1, pdf2)
    gerar_relatorio_pdf(iguais, diferentes, "resultado_comparacao.pdf")