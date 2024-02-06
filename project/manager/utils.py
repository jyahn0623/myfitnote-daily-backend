from PIL import Image, ImageDraw, ImageFont
import datetime 
import os

from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class AgeConverter:
    @staticmethod
    def convert(birth) -> str:
        today = datetime.datetime.today()
        age = today.year - int(birth[:4]) + 1
        return str(age)

class BmiCalculator:
    @staticmethod
    def calculate(weight, height) -> str:
        weight = float(weight)
        height = float(height) / 100

        bmi = round(weight / (height * height), 2)
        return str(bmi)
    
class ImageReportGenerator:
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
        'walk_grade' : (110, 328),
        'walk_count' : (199, 328),
        'seated_up_grade' : (110, 493),
        'seated_up_count' : (199, 493),
        'age' : (370, 150)
    }

    def create(self, name, birth, sex, weight, height, bmi, walk_grade, walk_count, seated_up_grade, seated_up_count):
        filename = f'{name}_{birth}.jpg'
        self.path = os.path.join(settings.MEDIA_ROOT, 'report', filename)
        print(self.path)
        today = datetime.datetime.today()

        year = str(today.year)
        month = str(today.month)
        day = str(today.day)

        self.name = name
        self.birth = birth
        self.age = AgeConverter.convert(birth)
        self.sex = sex
        self.height = height
        self.weight = weight
        self.bmi = BmiCalculator.calculate(weight, height)
        self.walk_grade = walk_grade
        self.walk_count = walk_count
        self.seated_up_grade = seated_up_grade
        self.seated_up_count = seated_up_count

        sex_type = 'sex_man' if self.sex == '남' else 'sex_woman'

        # self.name = '김현수'
        # self.birth = '19950623'
        # self.sex = '남'
        # self.height = '180cm'
        # self.weight = '70kg'
        # self.bmi = f'{21.6} kg/m2'

        # self.walk_grade = '1'
        # self.walk_count = '30'
        # self.seated_up_grade = '2'
        # self.seated_up_count = '30'

        img = self.create_image('/home/marketian/myfitnote/project/manager/static/manager/img/pdf_background.png')
        img = self.add_text_to_img(img, year, *ImageReportGenerator.attr_position.get('year'))
        img = self.add_text_to_img(img, month, *ImageReportGenerator.attr_position.get('month'))
        img = self.add_text_to_img(img, day, *ImageReportGenerator.attr_position.get('day'))

        img = self.add_text_to_img(img, self.name, *ImageReportGenerator.attr_position.get('name'))
        img = self.add_text_to_img(img, self.birth, *ImageReportGenerator.attr_position.get('birth'))
        img = self.add_text_to_img(img, self.height, *ImageReportGenerator.attr_position.get('height'))
        img = self.add_text_to_img(img, self.weight, *ImageReportGenerator.attr_position.get('weight'))
        img = self.add_text_to_img(img, self.bmi, *ImageReportGenerator.attr_position.get('bmi'))
        img = self.add_text_to_img(img, self.age, *ImageReportGenerator.attr_position.get('age'))

        img = self.add_text_to_img(img, self.walk_grade, *ImageReportGenerator.attr_position.get('walk_grade'))
        img = self.add_text_to_img(img, self.walk_count, *ImageReportGenerator.attr_position.get('walk_count'))
        img = self.add_text_to_img(img, self.seated_up_grade, *ImageReportGenerator.attr_position.get('seated_up_grade'))
        img = self.add_text_to_img(img, self.seated_up_count, *ImageReportGenerator.attr_position.get('seated_up_count'))

        img = self.add_circle_to_img(img, *ImageReportGenerator.attr_position.get(sex_type), 8)
        img = img.convert('RGB')
        img.save(self.path, 'JPEG')

        return self.path, filename
        # return self.path

    def create_image(self, image_path):
        # Open the image file
        img = Image.open(image_path)
        return img

    def add_text_to_img(self, img, text, x, y):
        # Get drawing context
        draw = ImageDraw.Draw(img)
        # Add the text to the image at the specified coordinates
        draw.text((x, y), text, font=ImageReportGenerator.fnt, fill=(0, 0, 0))
        return img
    
    def add_circle_to_img(self, img, x, y, r):
        draw = ImageDraw.Draw(img)
        draw.ellipse((x-r, y-r, x+r, y+r), outline=(0, 0, 0))
        return img
