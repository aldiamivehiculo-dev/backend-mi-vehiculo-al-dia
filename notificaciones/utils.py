from django.core.mail import send_mail
from django.conf import settings
from .models import Notificacion


#Crea una notificación en base de datos y, opcionalmente, envía un correo electrónico
def crear_notificacion(user, titulo, mensaje, tipo="sistema", meta=None, send_email=False):
    """
    Crea una notificación en la base de datos.
    user: Usuario que recibe la notificación
    titulo: Título visible para el usuario
    mensaje: Mensaje principal
    tipo: Tipo de notificación (documento, mantenimiento, qr, sistema)
    meta: Diccionario con información adicional (vehiculo_id, doc_id, etc.)
    send_email: Si es True, también envía un correo al usuario
    """
    #Guardar la notificación en la base de datos
    noti = Notificacion.objects.create(
        user=user,
        titulo=titulo,
        mensaje=mensaje,
        tipo=tipo,
        meta=meta or {}  #Si no recibe meta, usar {}
    )
    #Si se pide enviar correo y el usuario tiene email registrado
    if send_email and user.email:
        try:
            #Enviar correo utilizando Django
            send_mail(
                subject=titulo,
                message=mensaje,
                from_email=getattr(settings, "EMAIL_HOST_USER", None),  #Remitente configurado en settings
                recipient_list=[user.email],  #Enviar solo al usuario
                fail_silently=True,  #No romper el sistema si falla el email
            )

            #Marcar que se envió correo correctamente
            noti.enviada_email = True
            noti.save(update_fields=["enviada_email"])

        except Exception:
            #Si hay error al enviar correo, igual dejamos la notificación creada
            pass

    return noti  #Retornamos la notificación recién creada
