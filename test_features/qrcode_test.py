import qrcode

img = qrcode.make('Some data here')
type(img)
img.save("some_file.png")


import qrcode

def save_qr_code_to_file(data, file_name):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_code_img = qr.make_image(fill_color="brown", back_color="white")
    qr_code_img.save(file_name)

if __name__ == "__main__":
    data_to_encode = "https://res.cloudinary.com/dzqp39gll/image/upload/v1690616375/rfetd7h0sdqjoatwtorg.jpg"
    file_name = "qr_code.png"
    save_qr_code_to_file(data_to_encode, file_name)
