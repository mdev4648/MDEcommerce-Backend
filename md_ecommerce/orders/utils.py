from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO
from django.core.mail import EmailMessage
from .models import Order
from django.template.loader import render_to_string

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None

def send_invoice_email(order):
    pdf = render_to_pdf("orders/invoice.html", {"order": order})
    if pdf is None:
        return False

    email = EmailMessage(
        subject=f"Invoice for Order #{order.id}",
        body="Thank you for your purchase. Please find attached your invoice.",
        to=[order.user.email],
    )

    email.attach(f"invoice_{order.id}.pdf", pdf, "application/pdf")
    email.send()

    return True

def send_order_confirmation_email(order):
    subject = f"Order Confirmation - Order #{order.id}"
    message = render_to_string("orders/order_confirmation.txt", {
        "order": order
    })

    email = EmailMessage(
        subject=subject,
        body=message,
        to=[order.user.email],
    )

    email.send()