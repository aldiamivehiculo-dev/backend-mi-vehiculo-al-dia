from django.core.mail import send_mail
from django.conf import settings
from .models import Notificacion

def crear_notificacion(user, titulo, mensaje, tipo="sistema", meta=None, send_email=False):
    """
    Crea una notificación en BD y opcionalmente envía correo.
    """
    noti = Notificacion.objects.create(
        user=user,
        titulo=titulo,
        mensaje=mensaje,
        tipo=tipo,
        meta=meta or {}
    )

    if send_email and user.email:
        try:
            send_mail(
                subject=titulo,
                message=mensaje,
                from_email=getattr(settings, "EMAIL_HOST_USER", None),
                recipient_list=[user.email],
                fail_silently=True,
            )
            noti.enviada_email = True
            noti.save(update_fields=["enviada_email"])
        except Exception:
            # Si falla el mail, dejamos igual la notificación en app
            pass

    return noti
