#credits to http://stackoverflow.com/users/739489/bogdan
#code based on this http://stackoverflow.com/questions/9125465/how-to-sort-xls-file-column-wise-and-write-it-to-another-file-with-entire-row-us
import xlwt
from xlrd import open_workbook



def main():
    from sys import argv
    if len(argv)!=3:
        print("Usage: reg2csv.py input_file.xls output_file.xls")
    else:
        #target_column = int(argv[3])
        book = open_workbook(argv[1], formatting_info=True)
        sheet = book.sheets()[0]
        data = [sheet.row_values(i) for i in range(sheet.nrows)]
        labels = data[0]
        data = data[1:]
        data.sort(key=lambda x: x[2]+x[3]+x[1])
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet(sheet.name)
        for idx, label in enumerate(labels):
             sheet.write(0, idx, label)
        for idx_r, row in enumerate(data):
            for idx_c, value in enumerate(row):
                sheet.write(idx_r+1, idx_c, value)
        wbk.save(argv[2])

if __name__ == "__main__":
    main()