import os
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from pdf2image import convert_from_bytes
from docx import Document
from PIL import Image
from dotenv import load_dotenv
from io import BytesIO
import pytesseract
from app.config import Config


class OCRService:
    def __init__(self):
        subscription_key: str = Config.AZURE_SUBSCRIPTION_KEY
        endpoint: str = Config.AZURE_ENDPOINT
        self.computervision_client: ComputerVisionClient = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    
    def __ocr_image_azure(self, image: Image.Image) -> str:
        with BytesIO as image_buffer:
            image.save(image_buffer, format='PNG')
            image_buffer.seek(0)
            read_response = self.computervision_client.read_in_stream(image_buffer, raw=True)
        
        read_operation_location: str = read_response.headers["Operation-Location"]
        operation_id: str = read_operation_location.split("/")[-1]

        while True:
            read_result = self.computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)
        
        text = ""
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    text += line.text + "\n"
        
        return text
    
    @staticmethod
    def __ocr_image_tesseract(image: Image.Image) -> str:
        try:
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error in ORC process: {str(e)}")
            return ""
    
    def __ocr_pdf_azure(self, file_content: bytes) -> str:
        images = convert_from_bytes(file_content)
        text = ""
        for image in images:
            text += self.__ocr_image_azure(image)
        return text
    
    @staticmethod
    def __ocr_pdf_tesseract(content: bytes) -> str:
        images = convert_from_bytes(content)
        text = ""
        for image in images:
            text += OCRService.__ocr_image_tesseract(image)
        return text

    @staticmethod
    def __ocr_docx(file_content: bytes) -> str:
        doc = Document(BytesIO(file_content))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    def ocr_file_azure(self, file_content: bytes, file_extension: str) -> str:
        if file_extension.lower() == '.pdf':
            return self.__ocr_pdf_azure(file_content)
        elif file_extension.lower() == '.docx':
            return OCRService.__ocr_docx(file_content)
        else:
            return "Unsupported file format"
    
    @staticmethod
    def ocr_file(file_content: bytes, file_extension: str) -> str:
        if file_extension.lower() == '.pdf':
            return OCRService.__ocr_pdf_tesseract(file_content)
        elif file_extension.lower() == '.docx':
            return OCRService.__ocr_docx(file_content)
        else:
            return "Unsupported file format"