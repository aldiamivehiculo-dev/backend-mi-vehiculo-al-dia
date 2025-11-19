from rest_framework import serializers
from datetime import date, datetime
from PyPDF2 import PdfReader
import re
from .models import DocumentoVehicular
from pdf2image import convert_from_bytes  
import pytesseract     


PATENTE_RE = re.compile(r"\b([A-Z]{2,4}\d{2,4}(?:-?[A-Z0-9])?)\b")
FECHA_RE = re.compile(r"\b(\d{2}[-/]\d{2}[-/]\d{4})\b")


def _norm_patente(p):
    return re.sub(r'[^A-Z0-9]', '', p.upper())


def extract_ocr_text(file_obj):
    try:
        pages = convert_from_bytes(file_obj.read(), dpi=300)
    except:
        file_obj.seek(0)
        return ""

    texto = ""
    for img in pages:
        img = img.convert('L')
        img = img.point(lambda x: 0 if x < 150 else 255, '1')

        t = pytesseract.image_to_string(img, lang="spa+eng")
        if t:
            texto += t + "\n"

    file_obj.seek(0)
    return texto


class DocumentoVehicularSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoVehicular
        fields = '__all__'
        read_only_fields = ['user', 'fecha_subida', 'activo', 'puntaje_validacion', 'detalles_validacion']


    # Validación general
    def validate(self, attrs):
        tipo = attrs.get("tipo")
        vehiculo = attrs.get("vehiculo")
        archivo = attrs.get("archivo")

        patente_veh = _norm_patente(getattr(vehiculo, "patente", ""))

        # Datos evaluación
        detalles = {}
        score = 0
        minimo = 85

        # --- PROCESAMOS EL PDF ---
        try:
            texto_full = self._leer_texto_pdf(archivo).upper()
        except:
            raise serializers.ValidationError({"archivo": "No se pudo leer el documento."})

        patentes_pdf, fecha_pdf, texto_upper, anios_pdf = self._procesar_pdf(archivo)


        #patente debe estar
        if not patentes_pdf:
            raise serializers.ValidationError({"archivo": "No se encontró patente en el documento."})

        if not self._coincide_patente(patente_veh, patentes_pdf):
            raise serializers.ValidationError({
                "archivo": f"Patente del PDF ({','.join(patentes_pdf)}) no coincide con {patente_veh}"
            })
        

        # Validaciones Permiso de Circulación
        if tipo == "pc":
            # Reglas de puntaje
            # patente = 25
            # marca   = 10
            # modelo  = 10
            # tipo    = 10
            # palabra pc = 10
            # firma   = 15
            # año     = 15
            # venc    = 10

            #patente
            score += 25
            detalles["patente"] = True

            #marca
            if vehiculo.marca.upper() in texto_upper:
                score += 10
                detalles["marca"] = True
            else:
                detalles["marca"] = False

            #modelo
            if vehiculo.modelo.upper() in texto_upper:
                score += 10
                detalles["modelo"] = True
            else:
                detalles["modelo"] = False

            # palabra clave permiso/circul
            if "PERMISO" in texto_upper or "CIRCUL" in texto_upper:
                score += 10
                detalles["palabra_clave"] = True
            else:
                detalles["palabra_clave"] = False

            # firma electrónica
            if "FIRMA ELECTR" in texto_upper:
                score += 15
                detalles["firma_electronica"] = True
            else:
                detalles["firma_electronica"] = False

            # año
            if anios_pdf:
                score += 15
                detalles["anio_permiso"] = True
            else:
                detalles["anio_permiso"] = False

            # fecha vencimiento
            if not attrs.get("fecha_vencimiento") and fecha_pdf:
                attrs["fecha_vencimiento"] = fecha_pdf

            if attrs.get("fecha_vencimiento") and attrs["fecha_vencimiento"] >= date.today():
                score += 10
                detalles["vencimiento"] = True
            else:
                detalles["vencimiento"] = False


            # decisión final
            if score < minimo:
                raise serializers.ValidationError({
                    "archivo": f"Documento insuficiente. Puntaje obtenido: {score} / 100",
                    "detalles": detalles
                })  
        #soap
        if tipo =='so':
            nombre = archivo.name.lower()
            if not (nombre.endswith('.pdf') or nombre.endswith('.jpg') or nombre.endswith('.jpeg') or nombre.endswith('.png')):
                raise serializers.ValidationError({
                    "archivo": "Solo se permiten archivos PDF o imágenes (JPG, JPEG, PNG) para SOAP."
                })
            user = self.context["request"].user

            #patente obligatoria
            score +=20
            detalles["patente"] = True

            #marca
            marca_ok = vehiculo.marca.upper() in texto_upper
            detalles["marca"] = marca_ok
            score += 10 if marca_ok else 0

            #modelo
            modelo_ok = vehiculo.modelo.upper() in texto_upper
            detalles["modelo"] = modelo_ok
            score += 10 if modelo_ok else 0

            #tipo
            TIPO_MAP ={
                "auto": ["AUTOMOVIL", "VEHICULO LIVIANO"],
                "camioneta":["CAMIONETA" ],
                "moto": ["MOTOCICLETA", "MOTO"],
                "camion": ["CAMION"],
                "bus": ["BUS"],
            }
            t_match = False
            for palabra in TIPO_MAP.get(vehiculo.tipo, []):
                if palabra in texto_upper:
                    t_match = True
                    break
            detalles["tipo"] = t_match
            score += 10 if t_match else 0
           
            #nombre + apellido
            usuario_fullname = f"{user, 'nombre'}{getattr(user, 'apelidos', '')}".strip().upper()
            nombre_ok =usuario_fullname in texto_upper
            detalles["nombre_apellido"] = nombre_ok
            score +=10 if nombre_ok else 0

            #rut
            rut_user = re.sub(r"[^0-9K]", "", getattr(user, "rut", "").upper())
            rut_ok = rut_user in re.sub(r"[^0-9K]", "", texto_upper)
            detalles["rut"] = rut_ok
            score +=10 if rut_ok else 0

            #palabras claves 

            #18.490
            ley_ok = ("18.490" in texto_upper) or ("LEY" in texto_upper)
            detalles["ley_18490"] = ley_ok
            score += 10 if ley_ok else 0

            #R.V.M
            rvm_ok = ("R.V" in texto_upper) or ("RVM" in texto_upper)
            detalles["rvm"] = rvm_ok
            score += 10 if rvm_ok else 0

            #certificado seguro obligatorio
            cso_ok=("SEGURO OBLIGATORIO" in texto_upper) or("CERTIFICADO" in texto_upper)
            detalles["cso"] = cso_ok
            score += 10 if cso_ok else 0

            # año
            anio_ok = len(anios_pdf) > 0
            detalles["anios"] = anio_ok
            score += 10 if anio_ok else 0

            #aprobacion
            if score < minimo:
                raise serializers.ValidationError({
                    "archivo":f"Documento SOAP insuficiente. Puntaje {score}%",
                    "detalles": detalles,
                })
            
        if tipo =="rt":
            nombre = archivo.name.lower()

            if not (nombre.endswith('.pdf') or nombre.endswith('.jpg') or nombre.endswith('.jpeg') or nombre.endswith('.png')):
                raise serializers.ValidationError({
                    "archivo": "Solo se permiten archivos PDF o imágenes (JPG, JPEG, PNG) para SOAP."
                })
            
            if not attrs.get("fecha_vencimiento"):
                raise serializers.ValidationError({
                    "fecha_vencimiento": "Debe ingresar la fecha de vencimiento."
                })
            
            if attrs ["fecha_vencimiento"] < date.today():
                raise serializers.ValidationError({
                    "fecha_vencimiento": "La Revisión Técnica ya está vencida."
                })
            
            score = 0
            detalles ={
                "validacion_basica": True,
                "ocr_validaciones": "no aplicadas todavias"
            }
            
        # Guardamos datos
        attrs["puntaje_validacion"] = score
        attrs["detalles_validacion"] = detalles

        return attrs

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

        if not texto.strip():
            archivo.seek(0)
            texto = extract_ocr_text(archivo)

        archivo.seek(0)
        return texto


    def _procesar_pdf(self, archivo):
        texto = self._leer_texto_pdf(archivo)
        print(("\n=========== TEXTO OCR (RAW) ==========="))
        print((texto[:3000]) )
        print(("====================================\n"))

        patentes = [m.group(1).upper() for m in PATENTE_RE.finditer(texto)]

        fechas_str = [m.group(1) for m in FECHA_RE.finditer(texto)]
        fecha_pdf = None
        for fs in fechas_str:
            try:
                fmt = "%d-%m-%Y" if "-" in fs else "%d/%m/%Y"
                f = datetime.strptime(fs, fmt).date()
                if fecha_pdf is None or f > fecha_pdf:
                    fecha_pdf = f
            except:
                pass

        anios_pdf = re.findall(r"\b(20[2-4][0-9])\b", texto)

        return patentes, fecha_pdf, texto.upper(), anios_pdf


    def _coincide_patente(self, patente_veh, pat_pdf_list):
        pv = _norm_patente(patente_veh)
        cuerpo = pv[:6]

        for p in pat_pdf_list:
            pp = _norm_patente(p)
            if pp == pv or pp.startswith(cuerpo):
                return True
        return False


    #CREATE
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

    