from rest_framework import serializers
from datetime import date, datetime
from PyPDF2 import PdfReader
import re
from .models import DocumentoVehicular
import requests
impo

# =======================================================
# REGEX
# =======================================================
PATENTE_RE = re.compile(r"\b([A-Z]{2,4}\d{2,4}(?:-?[A-Z0-9])?)\b")
FECHA_RE = re.compile(r"\b(\d{2}[-/]\d{2}[-/]\d{4})\b")


def _norm_patente(p):
    return re.sub(r"[^A-Z0-9]", "", p.upper())


# OCR EXTERNO (OCR.SPACE)
def ocr_externo(file):
    url = "https://api.ocr.space/parse/image"

    api_key = os.environ.get("OCR_API_KEY", "helloworld")

    result = requests.post(
        url,
        files={"file": file},
        data={
            "apikey": api_key,
            "language": "spa",      # Mejor detección español
            "isTable": True,        # Para SOAP/PC/RT con cuadros
            "scale": True,          # Aumenta calidad
            "OCREngine": 2          # Motor OCR avanzado
        },
    )

    try:
        return result.json()["ParsedResults"][0]["ParsedText"]
    except:
        return ""



# =======================================================
# SERIALIZER PRINCIPAL
# =======================================================
class DocumentoVehicularSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoVehicular
        fields = "__all__"
        read_only_fields = [
            "user", "fecha_subida", "activo",
            "puntaje_validacion", "detalles_validacion"
        ]

    # =======================================================
    # VALIDACIÓN PRINCIPAL
    # =======================================================
    def validate(self, attrs):

        tipo = attrs.get("tipo")
        vehiculo = attrs.get("vehiculo")
        archivo = attrs.get("archivo")

        patente_veh = _norm_patente(vehiculo.patente)

        # 1) Extraer texto normalmente
        texto = self._leer_texto_pdf(archivo)

        # 2) Si no hay, ejecutar OCR externo
        if not texto.strip():
            archivo.seek(0)
            texto = ocr_externo(archivo)

        texto_upper = texto.upper()

        patentes_pdf, fecha_pdf, _, anios_pdf = self._procesar_pdf(texto)

        # SELECTOR DEL TIPO
        if tipo == "pc":
            return self._validar_pc(attrs, vehiculo, texto_upper, patentes_pdf, fecha_pdf, anios_pdf)

        if tipo == "so":
            return self._validar_soap(attrs, vehiculo, texto_upper, patentes_pdf, anios_pdf)

        if tipo == "rt":
            return self._validar_rt(attrs, vehiculo, texto_upper, patentes_pdf)

        return attrs

    # =======================================================
    # LECTURA PDF (PyPDF2 + fallback al OCR externo)
    # =======================================================
    def _leer_texto_pdf(self, archivo):
        texto = ""

        try:
            reader = PdfReader(archivo)
            for page in reader.pages:
                c = page.extract_text()
                if c:
                    texto += c + "\n"
        except:
            pass

        archivo.seek(0)
        return texto

    # =======================================================
    # PROCESAR PDF (igual como lo tenías)
    # =======================================================
    def _procesar_pdf(self, texto):
        patentes = [m.group(1).upper() for m in PATENTE_RE.finditer(texto)]

        fechas = [m.group(1) for m in FECHA_RE.finditer(texto)]
        fecha_pdf = None
        for fs in fechas:
            try:
                f = datetime.strptime(fs.replace("/", "-"), "%d-%m-%Y").date()
                if fecha_pdf is None or f > fecha_pdf:
                    fecha_pdf = f
            except:
                pass

        anios_pdf = re.findall(r"\b(20[2-4][0-9])\b", texto)

        return patentes, fecha_pdf, texto.upper(), anios_pdf

    # =======================================================
    # VALIDACIÓN PC
    # (SE MANTIENE IGUAL QUE TU VERSIÓN)
    # =======================================================
    def _validar_pc(self, attrs, vehiculo, texto, patentes_pdf, fecha_pdf, anios_pdf):

        score = 0
        detalles = {}
        minimo = 85

        # patente
        score += 20
        detalles["patente"] = True

        # marca
        marca_ok = vehiculo.marca.upper() in texto
        detalles["marca"] = marca_ok
        score += 10 if marca_ok else 0

        # modelo
        modelo_ok = vehiculo.modelo.upper() in texto
        detalles["modelo"] = modelo_ok
        score += 10 if modelo_ok else 0

        # palabra clave
        clave_ok = "PERMISO" in texto or "CIRCUL" in texto
        detalles["palabra_clave"] = clave_ok
        score += 15 if clave_ok else 0

        # firma o timbre
        firma_ok = (
            "FIRMA ELECTR" in texto or
            "TIMBRE" in texto or
            "CAJERO" in texto
        )
        detalles["firma"] = firma_ok
        score += 15 if firma_ok else 0

        # año
        anio_ok = bool(anios_pdf)
        detalles["anio"] = anio_ok
        score += 15 if anio_ok else 0

        # vencimiento auto
        if not attrs.get("fecha_vencimiento") and fecha_pdf:
            attrs["fecha_vencimiento"] = fecha_pdf

        venc_ok = (
            attrs.get("fecha_vencimiento")
            and attrs["fecha_vencimiento"] >= date.today()
        )
        detalles["vencimiento"] = venc_ok
        score += 15 if venc_ok else 0

        attrs["puntaje_validacion"] = score
        attrs["detalles_validacion"] = detalles

        if score < minimo:
            raise serializers.ValidationError({
                "archivo": f"PC insuficiente ({score}/100)",
                "detalles": detalles
            })

        return attrs

    # =======================================================
    # VALIDACIÓN SOAP
    # =======================================================
    def _validar_soap(self, attrs, vehiculo, texto, patentes_pdf, anios_pdf):

        score = 0
        detalles = {}
        minimo = 85

        # patente
        score += 20
        detalles["patente"] = True

        # marca
        marca_ok = vehiculo.marca.upper() in texto
        detalles["marca"] = marca_ok
        score += 10 if marca_ok else 0

        # modelo
        modelo_ok = vehiculo.modelo.upper() in texto
        detalles["modelo"] = modelo_ok
        score += 10 if modelo_ok else 0

        # año
        anio_ok = bool(anios_pdf)
        detalles["anio"] = anio_ok
        score += 10 if anio_ok else 0

        # palabras clave
        claves = ["SEGURO", "OBLIGATORIO", "18490", "CERTIFICADO"]
        claves_ok = any(c in texto for c in claves)
        detalles["palabras_clave"] = claves_ok
        score += 20 if claves_ok else 0

        # nombre y rut
        user = self.context["request"].user
        nombre_full = f"{user.nombre} {user.apellidos}".strip().upper()
        texto_norm = texto.replace(" ", "")
        nombre_norm = nombre_full.replace(" ", "")

        nombre_ok = nombre_norm in texto_norm
        detalles["nombre_apellido"] = nombre_ok
        score += 5 if nombre_ok else 0

        rut_user = re.sub(r"[^0-9K]", "", user.rut.upper())
        rut_pdf = re.sub(r"[^0-9K]", "", texto)
        rut_ok = rut_user in rut_pdf
        detalles["rut"] = rut_ok
        score += 20 if rut_ok else 0

        attrs["puntaje_validacion"] = score
        attrs["detalles_validacion"] = detalles

        if score < minimo:
            raise serializers.ValidationError({
                "archivo": f"SOAP insuficiente ({score}/100)",
                "detalles": detalles
            })

        return attrs

    # =======================================================
    # VALIDACIÓN RT
    # =======================================================
    def _validar_rt(self, attrs, vehiculo, texto, patentes_pdf):

        nombre = attrs["archivo"].name.lower()

        if not (nombre.endswith(".pdf") or nombre.endswith(".jpg") or nombre.endswith(".jpeg") or nombre.endswith(".png")):
            raise serializers.ValidationError({"archivo": "Formato no permitido para RT."})

        if not attrs.get("fecha_vencimiento"):
            raise serializers.ValidationError({"fecha_vencimiento": "Debe ingresar fecha."})

        if attrs["fecha_vencimiento"] < date.today():
            raise serializers.ValidationError({"fecha_vencimiento": "RT vencida."})

        score = 0
        detalles = {}
        minimo = 75

        patente_bd = _norm_patente(vehiculo.patente)[:6]
        patentes_pdf_norm = [_norm_patente(p) for p in patentes_pdf]
        pat_pdf_join = "".join(patentes_pdf_norm)

        patente_ok = patente_bd in pat_pdf_join
        detalles["patente"] = patente_ok
        score += 40 if patente_ok else 0

        claves_rt = ["CERTIFICADO", "REVISION", "APROBADO", "PLANTA"]
        claves_ok = sum(1 for c in claves_rt if c in texto) >= 2
        detalles["palabras_clave"] = claves_ok
        score += 20 if claves_ok else 0

        marca_ok = vehiculo.marca.upper() in texto
        modelo_ok = vehiculo.modelo.upper() in texto
        anio_ok = str(vehiculo.año) in texto

        detalles["marca"] = marca_ok
        detalles["modelo"] = modelo_ok
        detalles["anio"] = anio_ok

        score += 10 if marca_ok else 0
        score += 10 if modelo_ok else 0
        score += 10 if anio_ok else 0

        rut_user = re.sub(r"[^0-9K]", "", vehiculo.user.rut.upper())
        rut_pdf = re.sub(r"[^0-9K]", "", texto)
        rut_ok = rut_user in rut_pdf
        detalles["rut"] = rut_ok
        score += 10 if rut_ok else 0

        attrs["puntaje_validacion"] = score
        attrs["detalles_validacion"] = detalles

        if score < minimo:
            raise serializers.ValidationError({
                "archivo": f"RT insuficiente ({score}/100)",
                "detalles": detalles
            })

        return attrs

    # =======================================================
    # CREATE (DESACTIVAR ANTERIORES)
    # =======================================================
    def create(self, validated_data):
        user = self.context["request"].user
        vehiculo = validated_data["vehiculo"]
        tipo = validated_data["tipo"]

        DocumentoVehicular.objects.filter(
            user=user,
            vehiculo=vehiculo,
            tipo=tipo,
            activo=True
        ).update(activo=False)

        validated_data["user"] = user
        return super().create(validated_data)
