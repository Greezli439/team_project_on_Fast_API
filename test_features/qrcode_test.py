import qrcode
import io
import base64
from PIL import Image

def get_qr_code_base64(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_code_img = qr.make_image(fill_color="black", back_color="white")

    # Конвертуємо зображення PilImage у байтовий потік (BytesIO)
    img_byte_array = io.BytesIO()
    qr_code_img.save(img_byte_array, format='PNG')

    # Кодуємо зображення в Base64
    base64_encoded_img = base64.b64encode(img_byte_array.getvalue()).decode('utf-8')

    return base64_encoded_img

def create(base64_encoded_img):
    img_data = base64.b64decode(base64_encoded_img)
    img = Image.open(io.BytesIO(img_data))


    return img

if __name__ == "__main__":
    data_to_encode = "https://res.cloudinary.com/dzqp39gll/image/upload/v1690616355/x6q3tttik7wr5sqovxar.webp"
    base64_encoded_img = get_qr_code_base64(data_to_encode)
    # отримавши рядок тепер йошо перетворимо на фото.
    img = create(base64_encoded_img)
    img.show()
    print(base64_encoded_img)
    print(type(base64_encoded_img))