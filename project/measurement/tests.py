from PIL import Image, ImageDraw, ImageFont
import datetime 

from django.test import TestCase

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class ImageReportTestCase(TestCase):
    fnt = ImageFont.truetype('NanumGothicExtraBold.ttf', 13)
    attr_position = {
        'year' : (470, 95),
        'month' : (530, 95),
        'day' : (570, 95),
        'name' : (115, 150),
        'birth' : (290, 150),
        'height' : (135, 190),
        'weight' : (290, 190),
        'bmi' : (475, 190),
        'sex_man': (540, 156),
        'sex_woman': (568, 156),
        'walk_grade' : (115, 328),
        'walk_count' : (195, 328),
        'seated_up_grade' : (115, 493),
        'seated_up_count' : (195, 493),
    }

    def test_pdf(self):
        today = datetime.datetime.today()

        year = str(today.year)
        month = str(today.month)
        day = str(today.day)
    
        self.name = '김현수'
        self.birth = '19950623'
        self.sex = '남'
        self.height = '180cm'
        self.weight = '70kg'
        self.bmi = f'{21.6} kg/m2'

        self.walk_grade = '1'
        self.walk_count = '30'
        self.seated_up_grade = '2'
        self.seated_up_count = '30'

        img = self.create_image('/home/marketian/myfitnote/project/manager/static/manager/img/pdf_background.png')
        img = self.add_text_to_img(img, year, *ImageReportTestCase.attr_position.get('year'))
        img = self.add_text_to_img(img, month, *ImageReportTestCase.attr_position.get('month'))
        img = self.add_text_to_img(img, day, *ImageReportTestCase.attr_position.get('day'))

        img = self.add_text_to_img(img, self.name, *ImageReportTestCase.attr_position.get('name'))
        img = self.add_text_to_img(img, self.birth, *ImageReportTestCase.attr_position.get('birth'))
        img = self.add_text_to_img(img, self.height, *ImageReportTestCase.attr_position.get('height'))
        img = self.add_text_to_img(img, self.weight, *ImageReportTestCase.attr_position.get('weight'))
        img = self.add_text_to_img(img, self.bmi, *ImageReportTestCase.attr_position.get('bmi'))

        img = self.add_text_to_img(img, self.walk_grade, *ImageReportTestCase.attr_position.get('walk_grade'))
        img = self.add_text_to_img(img, self.walk_count, *ImageReportTestCase.attr_position.get('walk_count'))
        img = self.add_text_to_img(img, self.seated_up_grade, *ImageReportTestCase.attr_position.get('seated_up_grade'))
        img = self.add_text_to_img(img, self.seated_up_count, *ImageReportTestCase.attr_position.get('seated_up_count'))

        img = self.add_circle_to_img(img,*ImageReportTestCase.attr_position.get('sex_woman'), 8)
        img.save('test.png')
        print(img)

    def create_image(self, image_path):
        # Open the image file
        img = Image.open(image_path)
        return img

    def add_text_to_img(self, img, text, x, y):
        # Get drawing context
        draw = ImageDraw.Draw(img)
        # Add the text to the image at the specified coordinates
        draw.text((x, y), text, font=ImageReportTestCase.fnt, fill=(0, 0, 0))
        return img
    
    def add_circle_to_img(self, img, x, y, r):
        draw = ImageDraw.Draw(img)
        draw.ellipse((x-r, y-r, x+r, y+r), outline=(0, 0, 0))
        return img

class PdfTestCase(TestCase):
    pass
    # def test_pdf(self):
    #     c = self.create_pdf_from_image('/home/marketian/myfitnote/project/manager/static/manager/img/pdf_background.png', 
    #                                'test.pdf')
    #     # c = self.add_text_to_pdf(c, 'Hello World!', 100, 100)
    #     c = self.add_text_to_pdf_dummy(c)
    #     c.save()
    #     print(c)
    # def create_pdf_from_image(self, image_path, output_pdf_path):
    #     # Open the image file
    #     img = Image.open(image_path)
    #     # Get image size
    #     img_width, img_height = img.size

    #     print(img.size)

    #     # Create a new PDF with Reportlab
    #     c = canvas.Canvas(output_pdf_path, pagesize=letter)

    #     # Add the image to the PDF. Adjust the position as needed.
    #     c.drawImage(image_path, 0, 0, width=img_width, height=img_height)

    #     # Save the PDF
    #     # c.save()
    #     return c

    # def add_text_to_pdf(self, c, text, x, y):
    #     # Add the text to the PDF at the specified coordinates
    #     c.drawString(x, y, text)
    #     return c
    
    # def add_text_to_pdf_dummy(self, c):
    #     for i in range(20):
    #         self.add_text_to_pdf(c,'{i} position [문자열]',  i * 10, i * 10)
        
    #     return c