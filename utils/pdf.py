from fpdf import FPDF
from PIL import Image

class Notes(FPDF):
    """Handler class for filling and writing to a PDF file.
    """
    def __init__(self, image_path: str):
        """
        Args:
            image_path (str): Path to store temporary images (for now, just the grey background)
            
        Returns:
            None
        """
        super().__init__()
        # creating a new image file with discord dark theme and A4 size dimensions using PIL
        self.bg_path = '%s\\bg_dark.png' % image_path
        img = Image.new('RGB', (210,297), "#36393f" )
        img.save(self.bg_path)
        
        self.set_text_color(255, 255, 255)
        self.add_page(orientation='P') # A5 paper is 148 x 210 mm
        self.set_font("Arial", size = 15)
        
        # Setting dark theme background
        self.image(self.bg_path, x = 0, y = 0, w = 210, h = 297, type = '', link = '')
        
    def _add_scene(self, img, text): # TODO: Delete...?
        """Adds an image with the provided text next to it. Used for testing only.

        Args:
            img (str): The image file path.
            text (str): The caption text.
        """
        self.image(img, w=self.w/2)
        self.cell(w=self.w/2)
        self.multi_cell(w=self.w/2, align='l', txt=text)
        
    def save(self, filename: str):
        """Save the contents of the PDF to a file.

        Args:
            filename (str): File name (and optionally path) to save the PDF in.
        """
        self.output(filename + ".pdf")
        
    def write_scenes(self, images, speech):
        """Generates images with corrosponding transcriptions on the PDF.

        Args:
            images (list[list[str, float]]): List of image file paths with corrosponding timestamps
            speech (list[list[str, float]]): List of caption text with corrosponding timestamps
        """
        # Convenience function to write a cell with formatted captions and a timestamp
        textline = lambda s, t:  self.multi_cell(w=self.w/2, h=6, align='r', txt="%s [%s]\n" % (s, t))
        
        self.image(images[0][1], w=self.w/2, x=self.w/2)
        image_idx = 1
        for chunk in speech:
            # Unpack the text and corrosponding timestamps
            text, stamp = tuple(chunk)
            
            # Only need to compute and record the starting position of each timestamp
            stamp = stamp[0]
            
            # Recording each caption with an image, based on timestamp
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
        """Sets the dark image background. Automatically gets called with add_page().
        """
        self.image(self.bg_path, x = 0, y = 0, w = 210, h = 297, type = '', link = '')