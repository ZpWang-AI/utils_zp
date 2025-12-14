from ..core import *
PyPDF2 = LazyImport('PyPDF2')
# if 0: import PyPDF2


class PDFEditor:
    @classmethod
    def check_is_pdf(cls, filepath):
        assert path(filepath).suffix == '.pdf'

    @classmethod
    def crop_pdf(cls, input_path, output_path, start_page, end_page):
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
        cls.check_is_pdf(output_path)

        pdf_writer = PyPDF2.PdfWriter()
        for pdf_file in input_path_list:
            cls.check_is_pdf(pdf_file)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page])
                
        pdf_writer.write(output_path)

