import os
import openpyxl
import numpy as np
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    A canvas that enables dynamic two-pass page numbering ('Page X of Y')
    and draws consistent running headers and footers on all pages.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Draw Running Footer
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#475569")) # Slate 600
        
        # Footer text and line
        self.drawString(54, 36, "Confidential - Financial Analysis Report")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_text)
        
        self.setStrokeColor(colors.HexColor("#CBD5E1")) # Slate 200
        self.setLineWidth(0.5)
        self.line(54, 48, 612 - 54, 48) # Horizontal rule above footer
        
        # Draw Running Header (Skip on Page 1)
        if self._pageNumber > 1:
            self.drawString(54, 792 - 36, "FINANCIAL PERFORMANCE & REVENUE TRENDS REPORT")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 792 - 42, 612 - 54, 792 - 42) # Horizontal rule below header
            
        self.restoreState()

def generate_charts(desktop_dir):
    """
    Generates three professional charts using Matplotlib and saves them as temporary PNG files.
    """
    # Chart 1: Total Revenue and Unit Volume Trend (Dual Axis)
    fig, ax1 = plt.subplots(figsize=(6.5, 2.3), dpi=300)
    
    periods = ['Period 1', 'Period 2', 'Period 3']
    revenue = [53011.28, 59159.67, 70307.13]
    units = [862, 953, 1112]
    
    color = '#0F172A' # Slate 900 (Primary)
    ax1.set_xlabel('Reporting Period', fontweight='bold', fontsize=9, color='#475569')
    ax1.set_ylabel('Total Revenue ($)', color=color, fontweight='bold', fontsize=9)
    ax1.plot(periods, revenue, color=color, marker='o', linewidth=2.5, label='Revenue ($)')
    ax1.tick_params(axis='y', labelcolor=color, labelsize=8)
    ax1.yaxis.set_major_formatter('${x:,.0f}')
    ax1.set_ylim(45000, 75000)
    
    ax2 = ax1.twinx()  
    color2 = '#0D9488' # Teal 600 (Accent)
    ax2.set_ylabel('Total Units Sold', color=color2, fontweight='bold', fontsize=9)
    ax2.plot(periods, units, color=color2, marker='s', linestyle='--', linewidth=2, label='Units Sold')
    ax2.tick_params(axis='y', labelcolor=color2, labelsize=8)
    ax2.yaxis.set_major_formatter('{x:,.0f}')
    ax2.set_ylim(750, 1200)
    
    # Hide top spine, add horizontal gridlines on the main axis
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
    
    # Combined legend
    lines = ax1.get_lines() + ax2.get_lines()
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='#F8FAFC', edgecolor='#E2E8F0', fontsize=8)
    
    plt.title('Overall Revenue Growth & Volume Expansion', fontsize=11, fontweight='bold', color='#0F172A', pad=10)
    fig.tight_layout()
    chart1_path = os.path.join(desktop_dir, 'temp_trend.png')
    plt.savefig(chart1_path, bbox_inches='tight')
    plt.close()

    # Chart 2: Product Revenue comparison across Periods (Grouped Bar Chart)
    fig, ax = plt.subplots(figsize=(6.5, 2.3), dpi=300)
    
    products = ['Aero drone', 'EcoWidget Pro', 'Quantum headphones', 'SmartBand Elite', 'SuperCharger v2']
    p1_rev = [5999.88, 4300.00, 22988.50, 16797.90, 2925.00]
    p2_rev = [8999.82, 5100.00, 26486.75, 15198.10, 3375.00]
    p3_rev = [10999.78, 5800.00, 30484.75, 19197.60, 3825.00]
    
    x = np.arange(len(products))
    width = 0.24
    
    rects1 = ax.bar(x - width, p1_rev, width, label='Period 1', color='#94A3B8') # Slate 400
    rects2 = ax.bar(x, p2_rev, width, label='Period 2', color='#0284C7')         # Sky 600
    rects3 = ax.bar(x + width, p3_rev, width, label='Period 3', color='#0F172A') # Slate 900
    
    ax.set_ylabel('Revenue ($)', fontweight='bold', fontsize=9, color='#475569')
    ax.set_title('Product Line Revenue Performance Trends', fontsize=11, fontweight='bold', color='#0F172A', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(products, fontsize=8, color='#334155')
    ax.tick_params(axis='y', labelsize=8)
    ax.yaxis.set_major_formatter('${x:,.0f}')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
    ax.legend(frameon=True, facecolor='#F8FAFC', edgecolor='#E2E8F0', fontsize=8, loc='upper right')
    
    fig.tight_layout()
    chart2_path = os.path.join(desktop_dir, 'temp_products.png')
    plt.savefig(chart2_path, bbox_inches='tight')
    plt.close()

    # Chart 3: Regional Revenue comparison across Periods (Grouped Bar Chart)
    fig, ax = plt.subplots(figsize=(6.5, 2.3), dpi=300)
    
    regions = ['Central', 'East', 'North', 'South', 'West']
    p1_reg = [16797.90, 1275.00, 10396.00, 16642.50, 7899.88]
    p2_reg = [10949.82, 11895.50, 17491.25, 17398.10, 1425.00]
    p3_reg = [13694.75, 19197.60, 4325.00, 10999.78, 22090.00]
    
    x = np.arange(len(regions))
    
    rects1 = ax.bar(x - width, p1_reg, width, label='Period 1', color='#94A3B8')
    rects2 = ax.bar(x, p2_reg, width, label='Period 2', color='#0284C7')
    rects3 = ax.bar(x + width, p3_reg, width, label='Period 3', color='#0F172A')
    
    ax.set_ylabel('Revenue ($)', fontweight='bold', fontsize=9, color='#475569')
    ax.set_title('Regional Sales Revenue Volatility & Trends', fontsize=11, fontweight='bold', color='#0F172A', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=8, color='#334155')
    ax.tick_params(axis='y', labelsize=8)
    ax.yaxis.set_major_formatter('${x:,.0f}')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle=':', alpha=0.6, color='#CBD5E1')
    ax.legend(frameon=True, facecolor='#F8FAFC', edgecolor='#E2E8F0', fontsize=8, loc='upper right')
    
    fig.tight_layout()
    chart3_path = os.path.join(desktop_dir, 'temp_regions.png')
    plt.savefig(chart3_path, bbox_inches='tight')
    plt.close()
    
    return chart1_path, chart2_path, chart3_path

def build_pdf(desktop_dir, chart_paths):
    """
    Compiles the 3-page comprehensive PDF report using ReportLab's flowables.
    """
    pdf_path = os.path.join(desktop_dir, 'Financial_analysis.pdf')
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=60
    )
    
    styles = getSampleStyleSheet()
    
    # Custom, professional styles using a Slate-focused palette
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    table_text_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor('#1E293B')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=colors.white
    )
    
    story = []
    
    # Helper to wrap table cell data in Paragraphs to ensure clean wrapping and styling
    def wrap_table_data(data, header_row_count=1):
        wrapped = []
        for r_idx, row in enumerate(data):
            wrapped_row = []
            for c_idx, cell in enumerate(row):
                style = table_header_style if r_idx < header_row_count else table_text_style
                if isinstance(cell, Paragraph):
                    wrapped_row.append(cell)
                else:
                    wrapped_row.append(Paragraph(str(cell), style))
            wrapped.append(wrapped_row)
        return wrapped

    # Standard table style for professional look
    base_table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')), # Slate 900
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'), # Left-align first column text
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')), # Slate 200
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ])

    # ==================== PAGE 1 ====================
    # Title Block
    story.append(Paragraph("FINANCIAL ANALYSIS REPORT", title_style))
    story.append(Paragraph("Comparative Revenue and Trend Study across Three Sequential Performance Periods", subtitle_style))
    
    # Elegant solid divider
    d_table = Table([[""]], colWidths=[504], rowHeights=[3])
    d_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A'))]))
    story.append(d_table)
    story.append(Spacer(1, 10))
    
    # Executive Summary Heading
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(
        "This financial analysis report evaluates the comparative sales performance, revenue expansion, and "
        "regional market dynamics across three sequential reporting periods (Period 1, 2, and 3) utilizing "
        "the raw datasets extracted from 'sales_1.xlsx', 'sales_2.xlsx', and 'sales_3.xlsx'. Over the observed "
        "intervals, the business demonstrated outstanding momentum. Cumulative revenue grew from <b>$53,011.28</b> "
        "in Period 1 to <b>$70,307.13</b> in Period 3, establishing an exceptional period-over-period expansion of "
        "<b>32.63%</b>. This upward trajectory is firmly underpinned by robust volume growth, as total unit sales "
        "scaled from 862 units to 1,112 units (+29.00%). "
        "This report dissects the granular factors underpinning this growth, mapping product-specific line performance "
        "and evaluating regional trends to isolate the primary growth drivers and expose strategic vulnerabilities.",
        body_style
    ))
    
    story.append(Paragraph("Key Financial Performance Metrics Overview", h1_style))
    
    # Table 1: Executive Overview
    t1_raw_data = [
        ["Key Metric", "Period 1", "Period 2", "Period 3", "Total Cumulative", "Overall Growth (%)"],
        ["Total Revenue ($)", "$53,011.28", "$59,159.67", "$70,307.13", "$182,478.08", "+32.63%"],
        ["Total Units Sold (Qty)", "862", "953", "1,112", "2,927", "+29.00%"],
        ["Average Revenue/Unit ($)", "$61.50", "$62.08", "$63.23", "$62.34", "+2.81%"]
    ]
    
    t1 = Table(wrap_table_data(t1_raw_data), colWidths=[134, 74, 74, 74, 84, 64])
    t1_style = TableStyle([
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,2), (-1,2), colors.white),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#F8FAFC')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#94A3B8')),
    ])
    t1.setStyle(TableStyle(base_table_style.getCommands() + t1_style.getCommands()))
    story.append(t1)
    story.append(Spacer(1, 10))
    
    # Chart 1 inclusion
    story.append(Image(chart_paths[0], width=504, height=178))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<i>Figure 1.1: Multi-axis tracking showing highly correlated, volume-driven revenue expansion. "
        "The steady growth in average revenue per unit indicates strong pricing integrity.</i>",
        body_style
    ))
    
    story.append(PageBreak())
    
    # ==================== PAGE 2 ====================
    story.append(Paragraph("Product Line Performance Portfolio", h1_style))
    story.append(Paragraph(
        "A deep-dive investigation into the product-level transactions reveals varying growth patterns, "
        "high baseline category concentrations, and strict pricing rigidities. Most notably, average selling prices "
        "for each product remained perfectly static across all periods, indicating that all revenue changes "
        "were entirely volume-driven. This suggests high product demand elasticity and excellent pricing power.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Quantum headphones</b> ($99.95) remains the dominant category and the primary engine of corporate revenue. "
        "It accounted for over <b>43.8%</b> of all cumulative revenue, scaling from $22,988.50 to $30,484.75 (+32.61%). "
        "The high-margin, enterprise-tier <b>Aero drone</b> ($499.99) demonstrated the fastest growth rate, expanding "
        "unit volumes by 83.3% to finish Period 3 at $10,999.78. Meanwhile, the mid-tier <b>SmartBand Elite</b> ($79.99) "
        "experienced a brief volume contraction of -9.5% in Period 2 but made a spectacular, full recovery in Period 3, "
        "surging by 26.3% to achieve a period-high of $19,197.60. Low-cost volume staples (EcoWidget Pro and SuperCharger v2) "
        "grew organically and predictably.",
        body_style
    ))
    
    # Table 2: Product Breakdown
    t2_raw_data = [
        ["Product Line", "Price", "P1 Qty", "P1 Rev", "P2 Qty", "P2 Rev", "P3 Qty", "P3 Rev", "Total Rev", "Share"],
        ["Aero drone", "$499.99", "12", "$5,999.88", "18", "$8,999.82", "22", "$10,999.78", "$25,999.48", "14.25%"],
        ["EcoWidget Pro", "$20.00", "215", "$4,300.00", "255", "$5,100.00", "290", "$5,800.00", "$15,200.00", "8.33%"],
        ["Quantum headphones", "$99.95", "230", "$22,988.50", "265", "$26,486.75", "305", "$30,484.75", "$79,960.00", "43.82%"],
        ["SmartBand Elite", "$79.99", "210", "$16,797.90", "190", "$15,198.10", "240", "$19,197.60", "$51,193.60", "28.05%"],
        ["SuperCharger v2", "$15.00", "195", "$2,925.00", "225", "$3,375.00", "255", "$3,825.00", "$10,125.00", "5.55%"],
        ["Total Portfolio", "-", "862", "$53,011.28", "953", "$59,159.67", "1,112", "$70,307.13", "$182,478.08", "100.0%"]
    ]
    
    # Col widths sum to 504: 104 + 38 + 32 + 45 + 32 + 45 + 32 + 45 + 56 + 75 = 504
    t2_cols = [104, 38, 32, 45, 32, 45, 32, 45, 56, 75]
    t2 = Table(wrap_table_data(t2_raw_data), colWidths=t2_cols)
    t2_style = TableStyle([
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,2), (-1,2), colors.white),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,4), (-1,4), colors.white),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,6), (-1,6), colors.white),
        # Highlight total row
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F1F5F9')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor('#94A3B8')),
    ])
    t2.setStyle(TableStyle(base_table_style.getCommands() + t2_style.getCommands()))
    story.append(t2)
    story.append(Spacer(1, 10))
    
    # Chart 2 inclusion
    story.append(Image(chart_paths[1], width=504, height=178))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<i>Figure 1.2: Comparative analysis of product category revenue showing Quantum headphones and "
        "SmartBand Elite as stable bedrock lines, with Aero drones scaling rapidly.</i>",
        body_style
    ))
    
    story.append(PageBreak())
    
    # ==================== PAGE 3 ====================
    story.append(Paragraph("Regional Dynamics & Product Mix Insight", h1_style))
    story.append(Paragraph(
        "An analytical look at geographic performance reveals significant volatility and exposes a strong "
        "<b>'Product Mix'</b> effect. While overall company performance is steadily increasing, individual regions "
        "experienced massive swings in demand. This volatility was driven primarily by localized shifts "
        "in the specific items sold rather than a uniform increase in customer volume.",
        body_style
    ))
    story.append(Paragraph(
        "A striking example occurs in the <b>South region</b>. In Period 3, unit sales collapsed from 300 to just 22 units "
        "(-92.7%). However, because those 22 sales consisted exclusively of high-value Aero drones ($499.99), "
        "regional revenue remained remarkably resilient at $10,999.78. Conversely, the <b>North region</b> experienced "
        "the opposite effect in Period 3: unit sales rose to 245 units, but total revenue collapsed from $17,491.25 to "
        "just $4,325.00 because sales consisted entirely of lower-priced EcoWidget Pro ($20.00) and SuperCharger v2 ($15.00) lines. "
        "The <b>West region</b> performed exceptionally in Period 3, skyrocketing to $22,090.00 (340 units) due to a surge in "
        "Quantum headphone transactions.",
        body_style
    ))
    
    # Table 3: Regional Performance Breakdown
    t3_raw_data = [
        ["Geographic Region", "Period 1 Revenue", "Period 2 Revenue", "Period 3 Revenue", "Total Revenue", "Region Share (%)"],
        ["Central", "$16,797.90", "$10,949.82", "$13,694.75", "$41,442.47", "22.71%"],
        ["East", "$1,275.00", "$11,895.50", "$19,197.60", "$32,368.10", "17.74%"],
        ["North", "$10,396.00", "$17,491.25", "$4,325.00", "$32,212.25", "17.65%"],
        ["South", "$16,642.50", "$17,398.10", "$10,999.78", "$45,040.38", "24.68%"],
        ["West", "$7,899.88", "$1,425.00", "$22,090.00", "$31,414.88", "17.22%"],
        ["Total Company", "$53,011.28", "$59,159.67", "$70,307.13", "$182,478.08", "100.0%"]
    ]
    
    # Col widths sum to 504: 124 + 76 * 5 = 124 + 380 = 504
    t3_cols = [124, 76, 76, 76, 76, 76]
    t3 = Table(wrap_table_data(t3_raw_data), colWidths=t3_cols)
    t3_style = TableStyle([
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,2), (-1,2), colors.white),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,4), (-1,4), colors.white),
        ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#F8FAFC')),
        # Highlight total row
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F1F5F9')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor('#94A3B8')),
    ])
    t3.setStyle(TableStyle(base_table_style.getCommands() + t3_style.getCommands()))
    story.append(t3)
    story.append(Spacer(1, 10))
    
    # Chart 3 inclusion
    story.append(Image(chart_paths[2], width=504, height=178))
    story.append(Spacer(1, 8))
    
    # Strategic Insights & Actions
    story.append(Paragraph("Strategic Insights & Recommended Actions", h1_style))
    recommendations = [
        "<b>1. Optimize Regional Product Mix:</b> Deploy marketing efforts to introduce higher-margin lines (Quantum headphones, Aero drones) in regions with high raw-volume but low-revenue yield (e.g., North region).",
        "<b>2. Capitalize on West & East Momentum:</b> Expand sales infrastructure and inventory reserves in the East and West regions to capture exploding demand.",
        "<b>3. Stabilize Volatile Regions:</b> Audit the South region's sudden volume contraction and the Central region's stagnation to determine if they stem from localized competition or distribution delays.",
        "<b>4. Price Testing:</b> Since unit prices have remained strictly static despite strong volume expansion, conduct selective price testing on inelastic leaders (e.g., Quantum headphones) to capture untapped consumer surplus."
    ]
    
    for rec in recommendations:
        story.append(Paragraph(f"&bull; {rec}", bullet_style))
        
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report compiled successfully: {pdf_path}")

def main():
    desktop_dir = r"C:\Users\Asus\Desktop"
    print("Generating charts...")
    chart_paths = generate_charts(desktop_dir)
    print("Building PDF...")
    build_pdf(desktop_dir, chart_paths)
    
    # Clean up temporary images
    print("Cleaning up temporary chart files...")
    for path in chart_paths:
        try:
            os.remove(path)
            print(f"  Removed: {path}")
        except OSError as e:
            print(f"  Error removing {path}: {e}")
            
    print("All tasks completed successfully!")

if __name__ == '__main__':
    main()
