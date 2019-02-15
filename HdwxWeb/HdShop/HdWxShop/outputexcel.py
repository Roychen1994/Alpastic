import xlwt
import os

class outputexcel():

    def __init__(self,filename,title):
        self.filename =filename
        self.title = title
        self.wb = xlwt.Workbook(encoding = 'utf-8')
        self.ws = self.wb.add_sheet('sheet1')
        self.irow = 1
        self.style_heading = xlwt.easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x19;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """
                                       )

        self.style_body = xlwt.easyxf("""
                font:
                    name Arial,
                    bold off,
                    height 0XA0;
                align:
                    wrap on,
                    vert center,
                    horiz left;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """
                                 )

        for i,titlestr in enumerate(self.title):
            self.ws.write(0,i,titlestr, self.style_heading)


    def writeline(self,lines):
        for i,line in enumerate(lines):
            self.ws.write(self.irow,i,line,self.style_body)
        self.irow += 1


    def Opworkbook(self):
        return self.wb


