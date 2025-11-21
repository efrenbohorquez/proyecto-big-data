import PyPDF2
import os

ruta = r"d:\proyecto big data\uploads\documentos_procuraduria\066_010_20251119_115419.pdf"

print(f"Probando archivo: {ruta}")
if os.path.exists(ruta):
    print("✅ El archivo existe")
    try:
        with open(ruta, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            print(f"✅ PDF válido. Páginas: {len(reader.pages)}")
            texto = reader.pages[0].extract_text()
            print(f"📝 Texto página 1: {texto[:100]}...")
    except Exception as e:
        print(f"❌ Error al leer PDF: {e}")
else:
    print("❌ El archivo no existe")
