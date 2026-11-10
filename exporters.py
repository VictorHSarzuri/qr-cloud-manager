import io
import qrcode
import qrcode.image.svg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def generate_qr_svg(data: str) -> bytes:
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(data, image_factory=factory)
    stream = io.BytesIO()
    img.save(stream)
    return stream.getvalue()

def generate_qr_pdf(data: str, title: str) -> bytes:
    qr_img = qrcode.make(data)
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 730, f"Codigo QR: {title}")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 705, f"Contenido / URL: {data}")
    
    reader = ImageReader(img_buffer)
    c.drawImage(reader, 100, 430, width=250, height=250)
    
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 400, "Generado automaticamente por QR Cloud Manager.")
    
    c.showPage()
    c.save()
    
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
