import PyPDF2


class PDFEditor:
    @classmethod
    def crop_pdf(cls, input_path, output_path, start_page, end_page):
        reader = PyPDF2.PdfReader(input_path)
        writer = PyPDF2.PdfWriter()
        for page_num in range(start_page - 1, end_page):
            page = reader.pages[page_num]
            writer.add_page(page)
        writer.write(output_path)

    @classmethod
    def combine_pdfs(cls, input_path_list, output_path):
        pdf_writer = PyPDF2.PdfWriter()

        for pdf_file in input_path_list:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page])
                
        pdf_writer.write(output_path)


if __name__ == '__main__':
    from utils_zp import *
    PDFEditor.combine_pdfs(
        listdir_full_path(r'D:\ZpWang\Work\-MasterAffairs\09-研二奖学金~\捐赠奖学金'),
        r'D:\ZpWang\Work\-MasterAffairs\09-研二奖学金~\捐赠奖学金\all.pdf'
    )
    
# # 输入文件路径
# input_file = r'D:\ZpWang\Work\-MasterAffairs\09-研二奖学金~\捐赠奖学金\论文全文.pdf'
# # 输出文件路径
# output_file = r'D:\ZpWang\Work\-MasterAffairs\09-研二奖学金~\捐赠奖学金\论文首页.pdf'
# # 起始页和结束页
# start_page = 1
# end_page = 1
# # start_page = 1
# # end_page =10

# # 裁剪PDF
# crop_pdf(input_file, output_file, start_page, end_page)