import qrcode


img = make('https://docs.google.com/document/d/11mdaddCwhgKPPWgTnQgJNolNUV_DwiZkjj7vC5En3vw/edit?pli=1')
type(img)  # qrcode.image.pil.PilImage
img.save("some_file.png")
