from fpdf import FPDF
from PIL import Image

class Notes(FPDF):
    def __init__(self, image_path: str):
        super().__init__()
        # Setting dark theme background
        # creating a new image file with discord dark theme and A4 size dimensions using PIL
        self.bg_path = '%s\\bg_dark.png' % image_path
        img = Image.new('RGB', (210,297), "#36393f" )
        img.save(self.bg_path)
        
        self.set_text_color(255, 255, 255)
        self.add_page(orientation='P') # A5 paper is 148 x 210 mm
        self.set_font("Arial", size = 15)
        
        # Setting dark theme background
        self.image(self.bg_path, x = 0, y = 0, w = 210, h = 297, type = '', link = '')
        
    def _add_scene(self, img, text):
        self.image(img, w=self.w/2)
        self.cell(w=self.w/2)
        self.multi_cell(w=self.w/2, align='l', txt=text)
        
    def save(self, filename: str):
        self.output(filename + ".pdf")
        
    def write_scenes(self, images, speech):
        textline = lambda s, t:  self.multi_cell(w=self.w/2, h=6, align='r', txt="%s [%s]\n" % (s, t))
        
        self.image(images[0][1], w=self.w/2, x=self.w/2)
        image_idx = 1
        for chunk in speech:
            text, stamp = tuple(chunk)
            stamp = stamp[0] # only need starting position
            
            if image_idx + 1 > len(images):
                textline(text, stamp)
            elif stamp < images[image_idx + 1][0]:
                textline(text, stamp)
            else:
                self.image(images[image_idx][1], w=self.w/2, x=self.w/2)
                textline(text, stamp)
                image_idx += 1
        self.image(images[image_idx][1], w=self.w/2, x=self.w/2)
    def header(self):
        # Setting dark theme background
        self.image(self.bg_path, x = 0, y = 0, w = 210, h = 297, type = '', link = '')