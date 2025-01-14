import fitz  # PyMuPDF
import os
from PIL import Image
import io
import time
from datetime import datetime

def extract_images_and_captions(pdf_path, output_dir):
    """
    Extract images and their captions from a PDF file
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save extracted images
    
    Returns:
        list: List of dictionaries containing page numbers, image info and captions
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    total_pages = len(pdf_document)
    print(f"\nProcessing PDF with {total_pages} pages...")
    
    results = []
    image_count = 0
    start_time = time.time()
    
    # Iterate through each page
    for page_num in range(total_pages):
        try:
            # Show progress
            if (page_num + 1) % 10 == 0 or page_num == 0:
                elapsed_time = time.time() - start_time
                pages_per_second = (page_num + 1) / elapsed_time if elapsed_time > 0 else 0
                estimated_remaining = (total_pages - (page_num + 1)) / pages_per_second if pages_per_second > 0 else 0
                print(f"Processing page {page_num + 1}/{total_pages} "
                      f"({((page_num + 1)/total_pages*100):.1f}%) - "
                      f"Images found so far: {image_count} - "
                      f"Est. remaining time: {estimated_remaining/60:.1f} minutes")
            
            page = pdf_document[page_num]
            
            # Get images from the page
            images = page.get_images()
            
            # Get text from the page
            text = page.get_text()
            
            # Process each image on the page
            for img_index, img in enumerate(images):
                try:
                    # Get the image data
                    xref = img[0]  # Cross-reference number of the image
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Try to find caption (look for "Figure", "Image", or "Exhibit" near the image)
                    caption = "No caption found"
                    text_lines = text.split('\n')
                    keywords = ["Figure", "Image", "Exhibit", "Fig.", "Illustration"]
                    
                    for line in text_lines:
                        if any(keyword in line for keyword in keywords):
                            caption = line.strip()
                            break
                    
                    # Save the image
                    image_filename = f"image_{page_num + 1}_{img_index + 1}.png"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    
                    # Get image size
                    with Image.open(image_path) as img:
                        width, height = img.size
                    
                    # Add to results
                    results.append({
                        "page_number": page_num + 1,
                        "image_filename": image_filename,
                        "caption": caption,
                        "location": image_path,
                        "size": f"{width}x{height} pixels",
                        "file_size": f"{os.path.getsize(image_path) / 1024:.1f} KB"
                    })
                    
                    image_count += 1
                    
                except Exception as img_error:
                    print(f"Warning: Error processing image {img_index + 1} on page {page_num + 1}: {str(img_error)}")
                    continue
                
        except Exception as page_error:
            print(f"Warning: Error processing page {page_num + 1}: {str(page_error)}")
            continue
    
    pdf_document.close()
    
    # Save results to a text file
    output_txt = os.path.join(output_dir, "image_list.txt")
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(f"Images extracted from: {pdf_path}\n")
        f.write(f"Extraction date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total pages processed: {total_pages}\n")
        f.write(f"Total images found: {len(results)}\n\n")
        
        for item in results:
            f.write(f"Page {item['page_number']}:\n")
            f.write(f"Image: {item['image_filename']}\n")
            f.write(f"Caption: {item['caption']}\n")
            f.write(f"Size: {item['size']}\n")
            f.write(f"File size: {item['file_size']}\n")
            f.write(f"Location: {item['location']}\n")
            f.write("-" * 50 + "\n\n")
    
    total_time = time.time() - start_time
    print(f"\nProcessing complete!")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Images extracted: {len(results)}")
    print(f"Average processing speed: {total_pages/total_time:.1f} pages/second")
    
    return results

# Example usage
if __name__ == "__main__":
    # Replace these with your actual PDF path and desired output directory
    pdf_path = "sample.pdf"
    output_dir = "extracted_images"
    
    try:
        results = extract_images_and_captions(pdf_path, output_dir)
        print(f"\nDetailed list saved to: {os.path.join(output_dir, 'image_list.txt')}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
