import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import difflib


def extract_paragraphs(pdf_path):
    paragraphs = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text(x_tolerance=1, y_tolerance=1)
            if texto:
                linhas = texto.split("\n")
                for linha in linhas:
                    if linha.strip():
                        paragraphs.append(linha.strip())  # cada linha vira 1 parágrafo
    return paragraphs


def compare_paragraphs(p1, p2):
    diff = difflib.ndiff(p1.split(), p2.split())
    result = []
    for token in diff:
        if token.startswith("  "):
            result.append(token[2:])  # igual
        elif token.startswith("- "):
            result.append(f"[REMOVIDO: {token[2:]}]")
        elif token.startswith("+ "):
            result.append(f"[ADICIONADO: {token[2:]}]")
    return " ".join(result)


def generate_report(pdf1_path, pdf2_path, output_path):
    pdf1_paragraphs = extract_paragraphs(pdf1_path)
    pdf2_paragraphs = extract_paragraphs(pdf2_path)

    max_len = max(len(pdf1_paragraphs), len(pdf2_paragraphs))

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_normal.wordWrap = "CJK"
    style_bold = ParagraphStyle("Bold", parent=style_normal, fontName="Helvetica-Bold", spaceAfter=6)

    story = []

    for i in range(max_len):
        p1 = pdf1_paragraphs[i] if i < len(pdf1_paragraphs) else ""
        p2 = pdf2_paragraphs[i] if i < len(pdf2_paragraphs) else ""
        result = compare_paragraphs(p1, p2)

        story.append(Paragraph("PARÁGRAFO INICIAL:", style_bold))
        story.append(Paragraph(p1 or "[VAZIO]", style_normal))
        story.append(Spacer(1, 12))

        story.append(Paragraph("PARÁGRAFO DE COMPARAÇÃO:", style_bold))
        story.append(Paragraph(p2 or "[VAZIO]", style_normal))
        story.append(Spacer(1, 12))

        story.append(Paragraph("RESULTADO DAS DIFERENÇAS:", style_bold))
        story.append(Paragraph(result or "Sem diferenças.", style_normal))
        story.append(Spacer(1, 24))

    doc.build(story)
    print(f"Relatório gerado em: {output_path}")


if __name__ == "__main__":
    pdf1 = "arquivo1.pdf"
    pdf2 = "arquivo2.pdf"
    output = "resultado.pdf"
    generate_report(pdf1, pdf2, output)
