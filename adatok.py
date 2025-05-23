import sqlite3
from fpdf import FPDF

def create_table_pdf(cursor, table_name, pdf):
    
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]
    
    
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Table: {table_name.upper()}", ln=True)
    pdf.ln(5)
    
    
    pdf.set_font('Arial', 'B', 10)
    col_width = pdf.w / (len(columns) + 1)
    

    for col in columns:
        pdf.cell(col_width, 10, col, border=1)
    pdf.ln()
    

    pdf.set_font('Arial', '', 10)
    for row in rows:
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

def main():
    
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    
    
    for table_name in tables:
        create_table_pdf(cursor, table_name, pdf)
        pdf.ln(10)  
    
    
    pdf.output('cinema_database_export.pdf')
    print("Az exportálás megtörtént")
    
    conn.close()

if __name__ == "__main__":
    main()