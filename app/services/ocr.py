import os
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from pdf2image import convert_from_path
from docx import Document
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

subscription_key = os.getenv('AZURE_SUBSCRIPTION_KEY')
endpoint = os.getenv('AZURE_ENDPOINT')

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def ocr_file(path):
    _, file_extension = os.path.splitext(path)

    if file_extension.lower() == '.pdf':
        return ocr_pdf(path)
    elif file_extension.lower() == '.docx':
        return ocr_docx(path)
    else:
        return "Unsupported file format"

def ocr_pdf(path):
    images = convert_from_path(path)
    text = ""
    for image in images:
        text += ocr_image(image)
    return text

def ocr_docx(path):
    doc = Document(path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def ocr_image(image):
    temp_image_path = "temp_image.png"
    image.save(temp_image_path)
    with open(temp_image_path, "rb") as image_stream:
        read_response = computervision_client.read_in_stream(image_stream, raw=True)
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)
    text = ""
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                text += line.text + "\n"
    os.remove(temp_image_path)
    return text