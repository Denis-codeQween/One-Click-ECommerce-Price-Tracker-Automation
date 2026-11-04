import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

class ExcelReporter:
    @staticmethod
    def generate_excel_report(df_final):
        """
        Generates a professionally styled Excel report from the final DataFrame.
        """
        report_dir = "data/reports"
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, "Price_Report_Latest.xlsx")

        wb = Workbook()
        ws = wb.active
        ws.title = "Price Monitoring"

        # Enable gridlines display in Excel
        ws.views.sheetView[0].showGridLines = True

        # Populate with data from DataFrame
        for r_idx, row in enumerate(dataframe_to_rows(df_final, index=False, header=True), 1):
            ws.append(row)

        # Styling table header (Row 1)
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid") # Dark Blue
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_alignment = Alignment(horizontal="center", vertical="center")

        for col_num in range(1, len(df_final.columns) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment

        ws.row_dimensions[1].height = 25

        # Styling data cells and applying thin borders
        thin_border = Border(
            left=Side(style='thin', color='D3D3D3'),
            right=Side(style='thin', color='D3D3D3'),
            top=Side(style='thin', color='D3D3D3'),
            bottom=Side(style='thin', color='D3D3D3')
        )

        for row_num in range(2, ws.max_row + 1):
            ws.row_dimensions[row_num].height = 20
            for col_num in range(1, ws.max_column + 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.border = thin_border
                # Alignment: product names (column 2) left-aligned, others centered
                cell.alignment = Alignment(vertical="center", horizontal="left" if col_num == 2 else "center")
                cell.font = Font(name="Calibri", size=11)

        # Auto-adjust column widths based on content
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        wb.save(report_path)
        print(f"[INFO] Excel report saved successfully to {report_path}")
        return report_path

# Wrapper function for direct import in main.py
def generate_excel_report(df_final):
    return ExcelReporter.generate_excel_report(df_final)