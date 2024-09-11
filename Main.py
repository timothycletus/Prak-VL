import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random

def get_random_text(corpus_file, num_sentences=2):
    """Get a minimal set of sentences from the corpus."""
    with open(corpus_file, 'r') as file:
        lines = file.readlines()
    random_text = random.choice(lines).strip()
    sentences = random_text.split('.')
    return '. '.join(sentences[:min(num_sentences, len(sentences))]).strip() + '.'

def random_color_correction(image):
    """Apply natural random color corrections to the crumpled paper to match the effect."""
    brightness = ImageEnhance.Brightness(image)
    contrast = ImageEnhance.Contrast(image)
    color = ImageEnhance.Color(image)
    image = brightness.enhance(random.uniform(0.9, 1.1))  # Slight brightness adjustment
    image = contrast.enhance(random.uniform(0.9, 1.1))  # Slight contrast adjustment
    image = color.enhance(random.uniform(0.9, 1.1))  # Slight color enhancement
    return image

def get_random_text_color():
    """Return a random text color with a 4:1 ratio of black to red/blue."""
    colors = [(0, 0, 0, 255), (0, 0, 0, 255), (0, 0, 0, 255), (0, 0, 0, 255),  # Black x 4
              (255, 0, 0, 255), (0, 0, 255, 255)]  # Red and Blue x 1 each
    return random.choice(colors)

def apply_random_blur(draw, image, word, font, position):
    """Apply more noticeable Gaussian blur to random text parts, ensuring readability."""
    blur = random.choice([True, True, False])  # Increase chance of blurring
    if blur:
        temp_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_image)
        temp_draw.text(position, word, font=font, fill=get_random_text_color())  # Draw text with random color
        
        # Adjust the blur range here
        blurred_part = temp_image.filter(ImageFilter.GaussianBlur(random.uniform(1, 5)))  # Increase blur range
        image.alpha_composite(blurred_part)
    else:
        draw.text(position, word, font=font, fill=get_random_text_color())  # Normal text with random color

def overlay_paper_with_rotated_text(background_img, paper_img, corpus_file, font_path, output_path):
    # Open and blur the background
    background = Image.open(background_img).convert("RGBA")
    blurred_background = background.filter(ImageFilter.GaussianBlur(5))  # Apply blur to the background

    # Open the crumpled paper image and adjust its size
    paper = Image.open(paper_img).convert("RGBA")
    
    # Ensure the paper size is optimal, neither too small nor too big (40-60% of the background)
    max_paper_width = int(background.width * 0.6)
    min_paper_width = int(background.width * 0.4)
    paper = paper.resize((min(max_paper_width, max(min_paper_width, paper.width)),
                          min(max_paper_width, max(min_paper_width, paper.height))), Image.LANCZOS)

    # Apply random Gaussian blur to the paper and random color corrections
    paper = paper.filter(ImageFilter.GaussianBlur(random.uniform(0, 2)))
    paper = random_color_correction(paper)

    # Random rotation of the paper
    angle = random.randint(-15, 15)  # A more subtle angle for natural placement
    paper_rotated = paper.rotate(angle, expand=True)

    # Ensure the paper fits within the background, otherwise place at (0,0)
    max_x = max(0, background.width - paper_rotated.width)
    max_y = max(0, background.height - paper_rotated.height)
    x = random.randint(0, max_x)
    y = random.randint(0, max_y)

    # Paste the rotated paper on the blurred background
    blurred_background.paste(paper_rotated, (x, y), paper_rotated)

    # Create a new layer for the text
    text_layer = Image.new("RGBA", blurred_background.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    random_text = get_random_text(corpus_file)
    font_size = max(20, int(min(paper_rotated.width, paper_rotated.height) * 0.05))
    font = ImageFont.truetype(font_path, font_size)

    # Define grid size for the text within the paper's bounds
    grid_rows = 10
    grid_cols = 5
    cell_width = paper.width // grid_cols
    cell_height = paper.height // grid_rows

    words = random_text.split()
    word_index = 0

    # Create another image for rotated text and paste it on the background
    text_on_paper = Image.new("RGBA", paper.size, (255, 255, 255, 0))
    draw_on_paper = ImageDraw.Draw(text_on_paper)

    for row in range(grid_rows):
        for col in range(grid_cols):
            if word_index >= len(words):
                break
            word = words[word_index]

            word_bbox = draw_on_paper.textbbox((0, 0), word, font=font)
            word_width = word_bbox[2] - word_bbox[0]
            word_height = word_bbox[3] - word_bbox[1]

            # Calculate position in the grid cell
            word_x = col * cell_width + (cell_width - word_width) // 2
            word_y = row * cell_height + (cell_height - word_height) // 2

            # Randomly place text in some grid cells
            if random.random() > 0.5:  # 50% chance to place text in each cell
                apply_random_blur(draw_on_paper, text_on_paper, word, font, (word_x, word_y))
                word_index += 1

    # Rotate the text layer to match the paper's rotation
    rotated_text = text_on_paper.rotate(angle, expand=True)

    # Paste the rotated text on the blurred background
    blurred_background.alpha_composite(rotated_text, (x, y))

    # Convert to RGB if saving as JPEG
    if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
        blurred_background = blurred_background.convert("RGB")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the final image
    blurred_background.save(output_path)

# Paths to your image folders, corpus text, and font
background_images_folder = 'resources/background'
paper_images_folder = 'resources/papers'
corpus_file = 'resources/corpus/deutch.txt'
font_path = 'resources/fonts/NotoSansDevanagari-Regular.ttf'
output_folder = 'output/deutch_output'


# List of all paper images
paper_images = [os.path.join(paper_images_folder, paper_image) for paper_image in os.listdir(paper_images_folder)]

# Overlay a single paper on each background with text
for bg_image in os.listdir(background_images_folder):
    bg_path = os.path.join(background_images_folder, bg_image)
    paper_path = random.choice(paper_images)  # Randomly pick a paper
    output_image_path = os.path.join(output_folder, f"overlay_{bg_image}.jpg")
    
    overlay_paper_with_rotated_text(bg_path, paper_path, corpus_file, font_path, output_image_path)