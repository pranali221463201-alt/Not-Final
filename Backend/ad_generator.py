import sys
import os
import json
import logging
import base64
import requests
import time
import io
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException

# Add the current directory to sys.path to ensure local modules are found
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from Supplier_Portal_Dashboard.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ads", tags=["advertisements"])

# Using Freepik AI (Mystic) for image generation
FREEPIK_API_URL = "https://api.freepik.com/v1/ai/mystic"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

logger.info("🚀 AD GENERATOR MODULE RELOADED - VERSION: FREEPIK MYSTIC")


class AdRequest:
    def __init__(
        self,
        business_name: str,
        products: str,
        target_audience: str = "",
        location: str = "",
        usp: str = "",
        offer: str = "",
        contact: str = "",
        platform: str = "instagram",
        tone: str = "modern",
    ):
        self.business_name = business_name
        self.products = products
        self.target_audience = target_audience
        self.location = location
        self.usp = usp
        self.offer = offer
        self.contact = contact
        self.platform = platform
        self.tone = tone


def generate_advertisement(ad_req: AdRequest) -> dict:
    """Generate advertisement copy using Groq API"""
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured")

    prompt = f"""You are an AI advertisement creator for a plastic products manufacturer.

Business Name: {ad_req.business_name}
Products: {ad_req.products}
Target Audience: {ad_req.target_audience or 'Retail customers and businesses'}
Location: {ad_req.location}
USP / Strengths: {ad_req.usp}
Offer: {ad_req.offer or 'Limited Stock Available'}
Contact: {ad_req.contact}
Platform: {ad_req.platform}
Tone: {ad_req.tone}

Generate a complete advertisement in this exact JSON format ONLY (no markdown, no extra text):
{{
  "headline": "A catchy headline under 10 words",
  "shortCaption": "1-2 line caption for Instagram/WhatsApp",
  "longCaption": "Longer paragraph for Facebook/LinkedIn with benefits and trust factors",
  "cta": "Call-to-action like 'Call Now' or 'Order Today'",
  "textForAd": ["Line 1", "Line 2", "Line 3", "Line 4"],
  "visualRecommendation": "Detailed visual style and image recommendations",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
  "bestFormat": "Recommended format (Instagram post/reel, Facebook post/ad, LinkedIn post, WhatsApp status, YouTube Shorts)"
}}"""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            timeout=30,
        )

        if response.status_code != 200:
            raise ValueError(f"Groq API returned {response.status_code}: {response.text}")

        data = response.json()
        if not data.get("choices") or not data["choices"][0].get("message"):
            raise ValueError("Invalid response structure from Groq API")

        content = data["choices"][0]["message"]["content"]

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                result = json.loads(content[json_start:json_end])
            else:
                raise ValueError("Could not parse JSON from Groq response")

        return result

    except requests.exceptions.Timeout:
        raise ValueError("Request to Groq API timed out")
    except requests.exceptions.ConnectionError:
        raise ValueError("Connection error to Groq API")
    except Exception as e:
        logger.error(f"Error generating ad: {str(e)}")
        raise


def generate_ad_image_freepik(prompt: str) -> str:
    """Generate ad image using Freepik AI (Mystic) with polling"""
    if not settings.FREEPIK_API_KEY:
        raise ValueError("FREEPIK_API_KEY not configured")

    headers = {
        "x-freepik-api-key": settings.FREEPIK_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    payload = {
        "prompt": prompt,
        "aspect_ratio": "widescreen_16_9"
    }

    try:
        # 1. Trigger the generation task
        response = requests.post(FREEPIK_API_URL, headers=headers, json=payload, timeout=40)
        
        if response.status_code != 200:
            error_text = response.text
            logger.error(f"Freepik API error (start): {response.status_code} - {error_text}")
            raise ValueError(f"Freepik API returned {response.status_code}: {error_text}")

        task_data = response.json()
        task_id = task_data.get("data", {}).get("task_id")
        
        if not task_id:
            # Maybe it's synchronous? Check for data directly
            generated = task_data.get("data", {}).get("generated", [])
            if generated:
                img_url = generated[0]
                img_resp = requests.get(img_url, timeout=30)
                if img_resp.status_code == 200:
                    return base64.b64encode(img_resp.content).decode('utf-8')
            
            logger.error(f"No task_id or sync data in Freepik response: {task_data}")
            raise ValueError("Failed to start generation task on Freepik")

        # 2. Poll for the result (max 60 seconds)
        polling_url = f"{FREEPIK_API_URL}/{task_id}"
        logger.info(f"Polling Freepik Mystic task {task_id}...")
        
        for _ in range(30): # 30 retries * 2 seconds = 60s
            time.sleep(2)
            poll_resp = requests.get(polling_url, headers=headers, timeout=20)
            
            if poll_resp.status_code != 200:
                continue
                
            result = poll_resp.json()
            data_content = result.get("data", {})
            
            if isinstance(data_content, dict):
                status = data_content.get("status")
                if status == "COMPLETED":
                    generated = data_content.get("generated", [])
                    if isinstance(generated, list) and len(generated) > 0:
                        image_url = generated[0]
                        # Download the image and convert to base64
                        img_resp = requests.get(image_url, timeout=30)
                        if img_resp.status_code == 200:
                            return base64.b64encode(img_resp.content).decode('utf-8')
                        else:
                            raise ValueError(f"Failed to download generated image from {image_url}")
                
                if status == "FAILED":
                    error_info = data_content.get("error", "Unknown error")
                    raise ValueError(f"Freepik task failed: {error_info}")

        raise ValueError("Freepik image generation timed out after 60 seconds")

    except requests.exceptions.Timeout:
        raise ValueError("Freepik request timed out")
    except Exception as e:
        logger.error(f"Error generating image with Freepik: {str(e)}")
        raise


def overlay_ad_text(image_b64: str, ad_data: dict, business_name: str) -> str:
    """Overlay Canva-style ad copy text onto the image"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(image_data)).convert("RGBA")
        width, height = img.size
        
        # Create a drawing context
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 1. Canva-style Gradient Overlay (Bottom-up)
        for i in range(int(height * 0.4)):
            alpha = int(200 * (1 - i / (height * 0.4)))
            draw.line([(0, height - i), (width, height - i)], fill=(0, 0, 0, alpha))
        
        # 2. Setup Fonts
        try:
            font_path = "C:/Windows/Fonts/arialbd.ttf"
            font_path_reg = "C:/Windows/Fonts/arial.ttf"
            h_size = int(height * 0.055)
            c_size = int(height * 0.032)
            b_size = int(height * 0.028)
            
            headline_font = ImageFont.truetype(font_path, h_size)
            caption_font = ImageFont.truetype(font_path_reg, c_size)
            brand_font = ImageFont.truetype(font_path, b_size)
            cta_font = ImageFont.truetype(font_path, int(height * 0.025))
        except:
            headline_font = ImageFont.load_default()
            caption_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()
            cta_font = ImageFont.load_default()
            
        headline = ad_data.get("headline", "Premium Quality").upper()
        caption = ad_data.get("shortCaption", "The best choice for your business.")
        cta_text = ad_data.get("cta", "ORDER NOW").upper()
        
        # 3. Draw Stylish Brand Header
        header_bar_h = int(height * 0.06)
        draw.rectangle([0, 0, width, header_bar_h], fill=(0, 0, 0, 100))
        draw.text((30, 15), business_name.upper(), font=brand_font, fill=(0, 255, 255, 255))
        
        # 4. Draw Headline (Left Aligned with Padding)
        padding = 40
        draw.text((padding, height - int(height * 0.22)), headline, font=headline_font, fill=(255, 255, 255, 255))
        
        # 5. Draw Caption
        draw.text((padding, height - int(height * 0.22) + h_size + 10), caption, font=caption_font, fill=(240, 240, 240, 255))
        
        # 6. Draw CTA Button (Bottom Right)
        cta_w = int(width * 0.22)
        cta_h = int(height * 0.07)
        cta_x = width - cta_w - padding
        cta_y = height - cta_h - padding
        
        # Rounded Button (approximated with ellipse/rectangle)
        draw.rounded_rectangle([cta_x, cta_y, cta_x + cta_w, cta_y + cta_h], radius=15, fill=(0, 123, 255, 255))
        
        # Center text in button
        draw.text((cta_x + 20, cta_y + 15), cta_text, font=cta_font, fill=(255, 255, 255, 255))
        
        # Merge and Encode
        combined = Image.alpha_composite(img, overlay).convert("RGB")
        buffered = io.BytesIO()
        combined.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error overlaying Canva-style text: {str(e)}")
        return image_b64


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/generate")
async def generate_ad(
    business_name: str,
    products: str,
    target_audience: str = "",
    location: str = "",
    usp: str = "",
    offer: str = "",
    contact: str = "",
    platform: str = "instagram",
    tone: str = "modern",
):
    """Generate advertisement copy (text) for a plastic manufacturer using Groq"""
    try:
        if not business_name or not products:
            raise HTTPException(status_code=400, detail="Business name and products are required")

        ad_request = AdRequest(
            business_name=business_name,
            products=products,
            target_audience=target_audience,
            location=location,
            usp=usp,
            offer=offer,
            contact=contact,
            platform=platform,
            tone=tone,
        )

        result = generate_advertisement(ad_request)
        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating advertisement: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating advertisement. Please try again.")


@router.post("/generate-image")
async def generate_ad_image(
    business_name: str,
    products: str,
    visual_style: str = "modern product photography",
    platform: str = "instagram",
    tone: str = "professional",
):
    """Generate an advertisement image using Gemini 3 Pro Image (Nano Banana Pro)"""
    try:
        if not business_name or not products:
            raise HTTPException(status_code=400, detail="Business name and products are required")

        # 1. Generate Ad Copy first (to get text for overlay)
        ad_request = AdRequest(
            business_name=business_name,
            products=products,
            platform=platform,
            tone=tone
        )
        try:
            ad_data = generate_advertisement(ad_request)
        except Exception as e:
            logger.error(f"Failed to generate ad copy for image: {e}")
            ad_data = {"headline": business_name, "shortCaption": products}

        # 2. Canva-style prompt for a high-end marketing aesthetic
        image_prompt = (
            f"High-end Canva style marketing poster for {business_name}. "
            f"Featuring {products} in a clean, minimalist professional studio setting. "
            f"Modern graphic design layout, plenty of clean negative space for text, "
            "aspirational mood, high-contrast aesthetics, 8k resolution commercial photography."
        )

        # 3. Generate the Base Image
        image_b64 = generate_ad_image_freepik(image_prompt)
        
        # 4. Overlay Text (The "Proper Advertisement" part)
        final_image_b64 = overlay_ad_text(image_b64, ad_data, business_name)
        
        return {
            "success": True,
            "image_base64": final_image_b64,
            "mime_type": "image/png",
            "prompt_used": image_prompt,
            "ad_copy": ad_data # Return copy as well
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating ad image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating image. Please try again.")


@router.post("/chat-response")
async def get_chat_response(query: str):
    """Get an intelligent chatbot response using Groq"""
    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Groq API not configured")

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are ChainBot, a smart Supply Chain Management assistant for a plastic "
                            "manufacturing company. Help with questions about inventory, supplier risk, "
                            "route optimization, demand forecasting, and supply chain best practices. "
                            "Be concise, friendly and practical."
                        ),
                    },
                    {"role": "user", "content": query},
                ],
                "temperature": 0.6,
                "max_tokens": 400,
            },
            timeout=20,
        )

        if response.status_code != 200:
            logger.error(f"Groq API error: {response.status_code}")
            return {
                "success": True,
                "response": "I'm having trouble connecting right now. Please try again in a moment.",
            }

        data = response.json()
        if not data.get("choices") or not data["choices"][0].get("message"):
            return {
                "success": True,
                "response": "I couldn't understand that. Could you rephrase?",
            }

        bot_response = data["choices"][0]["message"]["content"]
        return {"success": True, "response": bot_response}

    except requests.exceptions.Timeout:
        return {"success": True, "response": "Request timed out. Please try again."}
    except Exception as e:
        logger.error(f"Error getting chat response: {str(e)}")
        return {"success": True, "response": "I encountered an error. Please try again."}
