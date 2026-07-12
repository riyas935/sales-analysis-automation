import openpyxl

# Define columns (using the exact spelling 'Revvenue' as requested)
headers = ["product", "Units sold", "Revvenue", "region"]

# Fictional sales datasets for three periods (e.g., Q1, Q2, Q3)
data_1 = [
    ["EcoWidget Pro", 120, 2400.00, "North"],
    ["SuperCharger v2", 85, 1275.00, "East"],
    ["Quantum headphones", 150, 14992.50, "South"],
    ["Aero drone", 12, 5999.88, "West"],
    ["SmartBand Elite", 210, 16797.90, "Central"],
    ["EcoWidget Pro", 95, 1900.00, "West"],
    ["Quantum headphones", 80, 7996.00, "North"],
    ["SuperCharger v2", 110, 1650.00, "South"],
]

data_2 = [
    ["EcoWidget Pro", 145, 2900.00, "East"],
    ["SuperCharger v2", 95, 1425.00, "West"],
    ["Quantum headphones", 175, 17491.25, "North"],
    ["Aero drone", 18, 8999.82, "Central"],
    ["SmartBand Elite", 190, 15198.10, "South"],
    ["EcoWidget Pro", 110, 2200.00, "South"],
    ["Quantum headphones", 90, 8995.50, "East"],
    ["SuperCharger v2", 130, 1950.00, "Central"],
]

data_3 = [
    ["EcoWidget Pro", 160, 3200.00, "Central"],
    ["SuperCharger v2", 115, 1725.00, "North"],
    ["Quantum headphones", 200, 19990.00, "West"],
    ["Aero drone", 22, 10999.78, "South"],
    ["SmartBand Elite", 240, 19197.60, "East"],
    ["EcoWidget Pro", 130, 2600.00, "North"],
    ["Quantum headphones", 105, 10494.75, "Central"],
    ["SuperCharger v2", 140, 2100.00, "West"],
]

def create_excel(filename, data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Data"
    
    # Append headers
    ws.append(headers)
    
    # Append data
    for row in data:
        ws.append(row)
        
    # Auto-fit column widths so the columns look clean and readable
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
        
    wb.save(filename)
    print(f"Successfully created: {filename}")

# Run creation
create_excel("sales_1.xlsx", data_1)
create_excel("sales_2.xlsx", data_2)
create_excel("sales_3.xlsx", data_3)
input("All tasks completed successfully! Press Enter to exit...")
