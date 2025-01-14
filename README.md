# PDF Image Extractor

A Python script that extracts images and their captions from PDF files. It processes large PDF files efficiently and creates a detailed list of all extracted images.

## Features

- Extracts all images from PDF files
- Attempts to find and associate captions with images
- Saves images with original quality
- Creates a detailed list of all extracted images including:
  - Page numbers
  - Image dimensions
  - File sizes
  - Captions
- Shows real-time progress for large files
- Handles errors gracefully

## Requirements

- Python 3.6+
- PyMuPDF
- Pillow

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place your PDF file in the project directory
2. Run the script:
   ```
   python pdf_extractor.py
   ```
3. Find extracted images in the `extracted_images` folder
4. Check `image_list.txt` in the same folder for detailed information

## Output

The script creates:
- An `extracted_images` folder containing all extracted images
- An `image_list.txt` file with detailed information about each image
