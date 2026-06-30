from pdf2docx import Converter

pdf_file = input("Enter PDF file path: ")
word_file = input("Enter output Word filename: ")

cv = Converter(pdf_file)
cv.convert(word_file, start=0, end=None)
cv.close()

print(f"Converted successfully: {word_file}")