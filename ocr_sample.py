from PIL import Image
import sys
import pyocr
import pyocr.builders

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]

txt = tool.image_to_string(
    Image.open('images00/image1385.jpg'),
    lang="jpn",
    builder=pyocr.builders.TextBuilder(tesseract_layout=6)
)
print (txt)
