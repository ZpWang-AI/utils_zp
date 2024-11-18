import PyPDF2

def crop_pdf(input_path, output_path, start_page, end_page):
    with open(input_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        # 裁剪指定页面
        # print(len(reader.pages))
        for page_num in range(start_page - 1, end_page):
            page = reader.pages[page_num]
            writer.add_page(page)

        # 保存裁剪后的页面到新的PDF文件
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

# 输入文件路径
input_file = r'D:\0--data\projects\04.00-IDRR_data\tmp\Khanna 等 - 2022 - PRICAI 2022 Trends in Artificial Intelligence 19.pdf'
# 输出文件路径
output_file = r'D:\0--data\projects\04.00-IDRR_data\tmp\b.pdf'
# 起始页和结束页
start_page = 366
end_page = 377
# start_page = 1
# end_page =10

# 裁剪PDF
crop_pdf(input_file, output_file, start_page, end_page)