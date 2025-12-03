# ** H - 003 : CreativeForge – AI Creative Ad Studio**

*Turn a brand logo + product image into 10 ready-made ad creatives in under 30 seconds.*

---

## **1. Why I Built This**

Running ads on Instagram, Meta Ads, Google Display, or even outdoor screens requires a lot of creative variations.
In most teams, designers spend hours tweaking the same visual:

* moving text
* testing layouts
* rewriting captions
* adjusting tones
* regenerating variations

It’s repetitive work — and it slows down campaign execution.

I wanted a simple way to speed this up.

**CreativeForge** does exactly that:
Upload a logo + product image → get **10 polished ads**, each with a caption already blended into the design.

No manual editing. No PSDs. No time wasted.

---

## **2. What You Get**

After uploading two images and clicking **Generate**, you receive a ZIP containing:

```
creative_01.png
creative_02.png
...
creative_10.png
```

Each creative is a **final, production-ready ad**, meaning:

* The base image is generated using **DALL·E 3**
* A short caption is written using **GPT-4o**
* The caption is **blended directly into the image**
* Text color adapts to the background for readability
* Placement adjusts automatically
* All ads use the same premium typography for consistency

You only get finished ads — nothing extra.

---

## **3. How It Works**

### **1️ Image Generation**

Your logo + product photo are passed to **DALL·E 3**, which produces 10 creative variations based on your chosen tone:

* minimal
* premium
* luxury
* playful

### **2️ Caption Writing**

GPT-4o generates 10 captions that follow a few rules:

* 8–14 words
* subtle CTA
* clean tone
* no emojis or hashtags

### **3️ Caption Blending (The Smart Part)**

For each image:

* Extract dominant colors
* Measure brightness and contrast
* Test 6 possible caption positions
* Pick the best spot based on readability & composition
* Apply a modern semi-bold font
* Add soft shadow/outline if needed
* Auto-wrap and scale text

The caption looks like part of the ad — not pasted over it.

### **4️ Packaging**

All 10 final PNGs are zipped into **creative_pack.zip** for download.

---

## **4. Tech Stack**

* **Python 3.10**
* **FastAPI** (backend)
* **OpenAI DALL·E 3** (image generation)
* **OpenAI GPT-4o** (captions)
* **Pillow (PIL)** (caption blending + image edits)
* **ColorThief** (extract image colors)
* **zipfile** (final package)
* **HTML + JavaScript** (simple upload UI)

Runs completely **locally**.
No Docker required.

---

## **5. How to Run**

### **1. Clone the repo**

```bash
git clone https://github.com/ROHIT-UDUTHA/Groundtruth_ai_hackathon
cd Groundtruth_ai_hackathon
```

### **2. Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### **3. Install dependencies**

```bash
pip install -r backend/requirements.txt
```

### **4. Add your OpenAI API key**

```bash
export OPENAI_API_KEY="your_key_here"
```

Windows (PowerShell):

```powershell
setx OPENAI_API_KEY "your_key_here"
```

### **5. Start the backend**

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### **6. Open the frontend**

Open:

```
frontend/index.html
```

Upload → Generate → Download your premium ad pack.

---

## **6.Challenges **
1. Choosing the best caption position

Captions sometimes hid the product or looked awkward.
-> Implemented a 6-zone placement check and picked the clearest area dynamically.

2. Keeping captions visually consistent

Different images made text look mismatched in size and style.
-> Used fixed premium fonts + autoscaling + 3 preset styles.

3. Preventing DALL·E from distorting the logo

The model occasionally warped the brand logo.
-> Added strict “do not modify logo” constraints and refined the prompt.

4. Balancing speed and cost

10 images + captions can be slow or expensive.
-> Batched caption generation and optimized image calls.


---
## **7. Screenshot **
* <img width="1536" height="1024" alt="ChatGPT Image Dec 3, 2025, 11_47_57 AM" src="https://github.com/user-attachments/assets/ceb44a49-dda1-4820-983e-aa56832676cf" />

---

## **8. Notes / Learnings**

* Making captions readable on any background required color extraction, brightness checks, and smart placement. After tuning this, the ads started looking much more professional.
* DALL·E 3 works well with product + logo inputs, but prompts needed refining to keep things brand-consistent.
* Keeping font size, glow, and alignment consistent across all ads was essential — so I built three small presets and locked the typography.

---

<<<<<<< HEAD
## **8. Future Add-Ons**
=======
## **9. Future Add-Ons**
** if i can complete the above model before time i will do aspect ratios and seasonal/holiday themes so checkout the output for that **

>>>>>>> 867ae358eb77683582e9eaa013e8bfddd2a0958e
* Support for 4:5, 9:16, and other aspect ratios
* Seasonal/holiday themes
* Built-in upscaler for print-quality ads
* Multi-language caption generation
