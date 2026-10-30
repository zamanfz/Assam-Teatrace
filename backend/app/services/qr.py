import io
import qrcode


def generate_qr_png(public_url: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(public_url)
    qr.make(fit=True)

    image = qr.make_image()

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()