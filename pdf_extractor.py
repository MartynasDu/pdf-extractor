import fitz
import os
from PIL import Image
import io
import time
import re

def process_pdf(pdf_path, output_dir="extracted_images"):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Create or overwrite the image list file
    list_file_path = os.path.join(output_dir, "image_list.txt")
    
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    total_pages = len(pdf_document)
    print(f"\nProcessing PDF with {total_pages} pages...")
    
    # Initialize counters and timer
    start_time = time.time()
    images_found = 0
    images_with_captions = 0
    last_update_time = start_time
    update_interval = 10  # Update progress every 10 pages
    
    with open(list_file_path, "w", encoding="utf-8") as list_file:
        for page_num in range(total_pages):
            # Update progress
            if page_num % update_interval == 0:
                current_time = time.time()
                elapsed_time = current_time - start_time
                if elapsed_time > 0:
                    pages_per_second = (page_num + 1) / elapsed_time
                    remaining_pages = total_pages - (page_num + 1)
                    est_remaining_time = remaining_pages / pages_per_second / 60  # Convert to minutes
                    print(f"Processing page {page_num + 1}/{total_pages} ({((page_num + 1)/total_pages*100):.1f}%) - "
                          f"Images with captions: {images_with_captions}/{images_found} - "
                          f"Est. remaining time: {est_remaining_time:.1f} minutes")
            
            try:
                # Get the page
                page = pdf_document[page_num]
                
                # Get text blocks with position information
                blocks = page.get_text("dict")["blocks"]
                
                # First pass: collect all image blocks and their positions
                image_blocks = []
                for block in blocks:
                    if block["type"] == 1:  # Image block
                        image_blocks.append(block)
                
                # Process each image block
                for img_num, image_block in enumerate(image_blocks):
                    try:
                        images_found += 1
                        
                        # Get image position
                        image_rect = image_block["bbox"]
                        image_bottom = image_rect[3]
                        
                        # Try to find caption using position-based approach
                        caption = None
                        closest_text_distance = float('inf')
                        
                        # Look through text blocks that are below the image
                        for block in blocks:
                            if block["type"] != 0:  # Skip non-text blocks
                                continue
                                
                            block_top = block["bbox"][1]
                            
                            # Check if text block is below the image (within reasonable distance)
                            if block_top > image_bottom and block_top - image_bottom < 50:  # Reduced threshold
                                block_text = ""
                                for line in block["lines"]:
                                    for span in line["spans"]:
                                        block_text += span["text"] + " "
                                block_text = block_text.strip()
                                
                                # Check if this block contains a caption pattern
                                caption_patterns = [
                                    r"^(?:Figure|Fig\.)\s+\d+(?:\.\d+)?[\.:]\s*.*?[\.!?]",  # Starts with Figure/Fig.
                                    r"^FIGURE\s+\d+(?:\.\d+)?[\.:]\s*.*?[\.!?]"            # Starts with FIGURE
                                ]
                                
                                for pattern in caption_patterns:
                                    matches = re.findall(pattern, block_text, re.IGNORECASE)
                                    if matches:
                                        # Calculate distance from image to text
                                        distance = block_top - image_bottom
                                        
                                        # If this caption is closer to the image than previous ones
                                        if distance < closest_text_distance:
                                            caption = matches[0].strip()
                                            closest_text_distance = distance
                                            
                                            # Look for continuation of caption
                                            for line in block["lines"]:
                                                for span in line["spans"]:
                                                    span_text = span["text"].strip()
                                                    if span_text and not any(span_text.lower().startswith(p.lower()) 
                                                                           for p in ["Figure", "Fig.", "Table"]):
                                                        if not caption.endswith(span_text):
                                                            caption += " " + span_text
                        
                        # Only process images that have captions
                        if caption:
                            images_with_captions += 1
                            
                            # Extract the image using get_pixmap
                            clip = fitz.Rect(image_rect)
                            pix = page.get_pixmap(clip=clip)
                            
                            # Save the image
                            image_filename = f"image_{page_num + 1}_{img_num + 1}.png"
                            img_path = os.path.join(output_dir, image_filename)
                            pix.save(img_path)
                            
                            # Get image info using PIL
                            with Image.open(img_path) as pil_img:
                                width, height = pil_img.size
                            
                            # Write image info to list file
                            list_file.write(f"Page: {page_num + 1}\n")
                            list_file.write(f"Image: {image_filename}\n")
                            list_file.write(f"Caption: {caption}\n")
                            list_file.write(f"Dimensions: {width}x{height}\n")
                            list_file.write(f"File size: {os.path.getsize(img_path)} bytes\n")
                            list_file.write(f"Location: {img_path}\n")
                            list_file.write("-" * 80 + "\n")
                        
                    except Exception as e:
                        print(f"Warning: Error processing image {img_num + 1} on page {page_num + 1}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Warning: Error processing page {page_num + 1}: {str(e)}")
                continue
    
    # Calculate and print summary
    end_time = time.time()
    total_time = (end_time - start_time) / 60  # Convert to minutes
    pages_per_second = total_pages / (end_time - start_time)
    
    print(f"\nProcessing complete!")
    print(f"Total time: {total_time:.1f} minutes")
    print(f"Total images found: {images_found}")
    print(f"Images with captions: {images_with_captions}")
    print(f"Images without captions (skipped): {images_found - images_with_captions}")
    print(f"Average processing speed: {pages_per_second:.1f} pages/second")
    print(f"\nDetailed list saved to: {list_file_path}")

if __name__ == "__main__":
    process_pdf("sample.pdf")
