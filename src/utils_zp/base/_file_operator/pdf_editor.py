from ..core import *
PyPDF2 = LazyImport('PyPDF2')
# if 0: import PyPDF2
# pip install PyPDF2
# # import PIL
# PIL = LazyImport('PIL')
# # Image = LazyImport('PIL', function_name='Image')
# from PIL import Image


class PDFEditor:
    @classmethod
    def check_is_pdf(cls, filepath):
        assert path(filepath).suffix == '.pdf'

    @staticmethod
    def pdf_to_png(pdf_path, page_numbers=None, output_path=None):
        """
        Convert PDF pages to one PNG image.
        
        Args:
            pdf_path: Path to input PDF
            page_numbers: List of page numbers (1-indexed), or None for all pages
            output_path: Path for output PNG file (uses PDF name + _pages.png if None)
        
        Returns:
            Path to saved PNG file
        """
        # Import pdf2image here to avoid dependency unless needed
        from pdf2image import convert_from_path
        
        # Check if PDF
        if Path(pdf_path).suffix != '.pdf':
            raise ValueError("Input must be a PDF file")
        
        # Determine output path
        if output_path is None:
            pdf_name = Path(pdf_path).stem
            output_path = Path(pdf_path).parent / f"{pdf_name}_pages.png"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert page numbers (1-indexed to 0-indexed for pdf2image)
        if page_numbers is None:
            # Get all pages
            first_page = 1
            last_page = None
        elif isinstance(page_numbers, int):
            first_page = page_numbers
            last_page = page_numbers
        else:
            # Get min and max page numbers
            first_page = min(page_numbers)
            last_page = max(page_numbers)
        
        # Convert PDF pages to images
        images = convert_from_path(
            pdf_path,
            first_page=first_page,
            last_page=last_page,
            dpi=300
        )
        
        # Filter specific pages if needed
        if isinstance(page_numbers, list) and len(page_numbers) > 0:
            filtered_images = []
            for idx, page_num in enumerate(range(first_page, last_page + 1)):
                if page_num in page_numbers:
                    filtered_images.append(images[idx])
            images = filtered_images
        
        # Combine images vertically
        if not images:
            raise ValueError("No pages to convert")
        
        # Calculate total height and max width
        widths, heights = zip(*(img.size for img in images))
        total_height = sum(heights)
        max_width = max(widths)
        
        # Create new image
        from PIL import Image
        new_image = Image.new('RGB', (max_width, total_height), color='white')
        
        # Paste images
        y_offset = 0
        for img in images:
            # Center horizontally if needed
            x_offset = (max_width - img.width) // 2
            new_image.paste(img, (x_offset, y_offset))
            y_offset += img.height
        
        # Save combined image
        new_image.save(output_path, 'PNG')
        
        return str(output_path)
    
    @classmethod
    def crop_pdf(cls, input_path, output_path, start_page, end_page):
        """
        pip install pypdf2
        """
        cls.check_is_pdf(input_path)
        cls.check_is_pdf(output_path)

        reader = PyPDF2.PdfReader(input_path)
        writer = PyPDF2.PdfWriter()
        for page_num in range(start_page - 1, end_page):
            page = reader.pages[page_num]
            writer.add_page(page)
        writer.write(output_path)

    @classmethod
    def combine_pdfs(cls, input_path_list, output_path):
        """
        pip install pypdf2
        """
        cls.check_is_pdf(output_path)

        pdf_writer = PyPDF2.PdfWriter()
        for pdf_file in input_path_list:
            cls.check_is_pdf(pdf_file)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page])
                
        pdf_writer.write(output_path)

