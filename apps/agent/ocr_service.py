"""
OCR Service for Lab Exam Analysis
================================

This service provides OCR functionality for processing lab exam PDFs and images.
It extracts text using Tesseract OCR and analyzes results with LLM.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List
import io

# OCR Dependencies
import pytesseract
from PIL import Image
import pdf2image

# LangChain for LLM analysis
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    """Service for OCR processing and lab exam analysis."""
    
    def __init__(self):
        """Initialize OCR service with LLM."""
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        logger.info("🏥 OCR Service initialized")
    
    async def process_lab_exam(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process lab exam file with OCR and LLM analysis.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Dict with extracted text, analysis, and recommendations
        """
        try:
            logger.info(f"📄 Processing file: {filename}")
            
            # 1. Determine file type and convert to images
            images = await self._process_file_to_images(file_content, filename)
            
            # 2. Extract text with OCR
            extracted_text = await self._extract_text_from_images(images)
            
            # 3. Analyze with LLM
            analysis = await self._analyze_lab_results(extracted_text)
            
            logger.info("✅ OCR processing completed successfully")
            
            return {
                "success": True,
                "extracted_text": extracted_text,
                "analysis": analysis,
                "recommendations": [],
                "alerts": [],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing OCR: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_file_to_images(self, file_content: bytes, filename: str) -> List[Image.Image]:
        """Process file (PDF or image) and convert to images."""
        try:
            # Check file extension to determine type
            file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
            
            if file_ext == 'pdf':
                logger.info("🔄 Processing PDF file...")
                return await self._pdf_to_images(file_content, filename)
            elif file_ext in ['png', 'jpg', 'jpeg']:
                logger.info("🖼️ Processing image file...")
                return await self._image_to_images(file_content, filename)
            else:
                raise Exception(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"❌ Error processing file: {e}")
            raise Exception(f"Error processing file: {str(e)}")
    
    async def _image_to_images(self, file_content: bytes, filename: str) -> List[Image.Image]:
        """Convert image file to PIL Image."""
        try:
            from PIL import Image
            import io
            
            # Open image from bytes
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if necessary (for PNG with transparency)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            logger.info(f"🖼️ Converted image: {image.size}, mode: {image.mode}")
            return [image]
            
        except Exception as e:
            logger.error(f"❌ Error converting image: {e}")
            raise Exception(f"Error converting image: {str(e)}")

    async def _pdf_to_images(self, file_content: bytes, filename: str) -> List[Image.Image]:
        """Convert PDF to images."""
        try:
            logger.info("🔄 Converting PDF to images...")
            
            # Convert PDF to images
            images = pdf2image.convert_from_bytes(
                file_content,
                dpi=300,  # High DPI for better OCR accuracy
                first_page=None,
                last_page=None,
                fmt='jpeg'
            )
            
            logger.info(f"📄 Converted PDF to {len(images)} images")
            return images
            
        except Exception as e:
            logger.error(f"❌ Error converting PDF: {e}")
            raise Exception(f"Error converting PDF: {str(e)}")
    
    async def _extract_text_from_images(self, images: List[Image.Image]) -> str:
        """Extract text from images using OCR."""
        try:
            logger.info("🔍 Extracting text with OCR...")
            
            text = ""
            for i, image in enumerate(images):
                # Convert PIL image to text using Tesseract
                page_text = pytesseract.image_to_string(
                    image, 
                    lang='por+eng',  # Portuguese and English
                    config='--psm 6'  # Assume uniform block of text
                )
                text += f"--- Page {i+1} ---\n{page_text}\n\n"
            
            logger.info(f"📝 Extracted {len(text)} characters of text")
            return text.strip()
            
        except Exception as e:
            logger.error(f"❌ Error extracting text: {e}")
            raise Exception(f"Error extracting text: {str(e)}")
    
    async def _analyze_lab_results(self, text: str) -> str:
        """Analyze lab results with LLM."""
        try:
            logger.info("🧠 Analyzing lab results with LLM...")
            
            prompt = f"""
You are a medical AI assistant analyzing laboratory exam results.

Lab Results Text:
{text}

Please analyze and provide a structured response with:

1. **📊 Values Found**: List all lab values with their reference ranges
2. **⚠️ Abnormal Values**: Highlight any values outside normal ranges
3. **🏥 Health Assessment**: Overall health assessment
4. **💡 Recommendations**: Medical recommendations
5. **🚨 Alerts**: Any critical values that need immediate attention

Guidelines:
- Respond in Portuguese
- Be professional but accessible
- Use emojis for better readability
- Format with clear sections
- If no values are found, mention that the text might not contain lab results
- Always recommend consulting a healthcare professional for medical decisions

Response:"""

            response = await self.llm.ainvoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Error analyzing results: {e}")
            raise Exception(f"Error analyzing results: {str(e)}")

# Global OCR service instance
_ocr_service = None

def get_ocr_service() -> OCRService:
    """Get or create OCR service instance."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
