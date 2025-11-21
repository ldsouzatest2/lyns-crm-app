from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from datetime import datetime

# Create PDF
pdf_file = "Partner_User_Guide.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=letter)
story = []
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f77b4'),
    spaceAfter=30,
    alignment=TA_CENTER
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=colors.HexColor('#1f77b4'),
    spaceAfter=12,
    spaceBefore=12
)

# Title
story.append(Paragraph("🏠 Lyns Real Estate CRM", title_style))
story.append(Paragraph("Partner User Guide", styles['Heading2']))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph(f"Version 1.0 | {datetime.now().strftime('%B %Y')}", styles['Normal']))
story.append(Spacer(1, 0.5*inch))

# Table of Contents
story.append(Paragraph("📋 Table of Contents", heading_style))
toc_data = [
    ["1.", "Logging In"],
    ["2.", "Dashboard Overview"],
    ["3.", "Managing Clients"],
    ["4.", "Viewing Listings"],
    ["5.", "Commission Structure"],
    ["6.", "Email Notifications"],
    ["7.", "Best Practices"],
    ["8.", "FAQ & Support"]
]
toc_table = Table(toc_data, colWidths=[0.5*inch, 5*inch])
toc_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 11),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
]))
story.append(toc_table)
story.append(PageBreak())

# Section 1: Logging In
story.append(Paragraph("🔐 1. LOGGING IN", heading_style))
story.append(Paragraph("<b>Step 1:</b> Open your web browser and go to your CRM URL", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("<b>Step 2:</b> Enter your <b>username</b> and <b>password</b> (provided by Admin/Lyndon)", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("<b>Step 3:</b> Click the <b>'Login'</b> button", styles['Normal']))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("<i>Note: Keep your login credentials secure and do not share them.</i>", styles['Italic']))
story.append(Spacer(1, 0.3*inch))

# Section 2: Dashboard
story.append(Paragraph("📊 2. DASHBOARD OVERVIEW", heading_style))
story.append(Paragraph("After logging in, your dashboard displays:", styles['Normal']))
story.append(Spacer(1, 0.1*inch))

dashboard_items = [
    ["<b>My Clients</b>", "Total number of clients assigned to you"],
    ["<b>My Listings</b>", "Properties available for you to show"],
    ["<b>My Commission</b>", "Your total earnings (10% share)"],
    ["<b>Client Status</b>", "Visual breakdown of client progress"]
]
dashboard_table = Table(dashboard_items, colWidths=[1.5*inch, 4*inch])
dashboard_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f2ff')),
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(dashboard_table)
story.append(Spacer(1, 0.3*inch))

# Section 3: Managing Clients
story.append(PageBreak())
story.append(Paragraph("👥 3. MANAGING CLIENTS", heading_style))
story.append(Paragraph("<b>What You Can Do:</b>", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
client_features = """
- View all clients assigned to you by Admin<br/>
- See complete client details: Name, contact, budget, property preferences<br/>
- Update client status as you progress<br/>
- Track communication history
"""
story.append(Paragraph(client_features, styles['Normal']))
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("<b>How to Update Client Status:</b>", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
update_steps = """
1. Navigate to <b>"My Clients"</b> from the sidebar menu<br/>
2. Select the client you want to update from the dropdown<br/>
3. Choose the appropriate status from the list<br/>
4. Click <b>"✅ Update Status"</b><br/>
5. Admin receives automatic email notification
"""
story.append(Paragraph(update_steps, styles['Normal']))
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("<b>Client Status Options:</b>", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
status_data = [
    ["New Lead", "Just assigned to you"],
    ["Contacted", "You've reached out to client"],
    ["Site Visit Scheduled", "Appointment confirmed"],
    ["Site Visit Done", "Property shown to client"],
    ["Interested", "Client likes the property"],
    ["Negotiation", "Discussing price/terms"],
    ["Deal in Progress", "Close to closing"],
    ["On Hold", "Temporarily paused"],
    ["Not Interested", "Client not proceeding"]
]
status_table = Table(status_data, colWidths=[1.8*inch, 3.7*inch])
status_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f8ff')),
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
story.append(status_table)
story.append(Spacer(1, 0.3*inch))

# Section 4: Listings
story.append(PageBreak())
story.append(Paragraph("🏢 4. VIEWING LISTINGS", heading_style))
story.append(Paragraph("<b>What You Can See:</b>", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
listing_info = """
You can view properties assigned to you that are marked <b>"Visible to Partner"</b>. Each listing shows:<br/>
<br/>
- Property address and location<br/>
- Property type (Apartment, Villa, Office, Warehouse, etc.)<br/>
- BHK/Size specifications<br/>
- Price and pricing currency<br/>
- Total area in square feet<br/>
- Furnishing status (for residential)<br/>
- <b>Broker name and contact number</b> - Use this to schedule site visits<br/>
- Amenities and features<br/>
- Current listing status
"""
story.append(Paragraph(listing_info, styles['Normal']))
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("<b>How to Update Listing Status:</b>", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
listing_steps = """
1. Go to <b>"My Listings"</b> from sidebar<br/>
2. Click on a property to expand full details<br/>
3. Note the <b>Broker Contact</b> - Call them to arrange site visits<br/>
4. After showing property, update the status<br/>
5. <b>Important:</b> When selecting "Shown to Client", choose which client(s) you showed it to<br/>
6. Click <b>"✅ Update"</b><br/>
7. Admin receives notification with client names
"""
story.append(Paragraph(listing_steps, styles['Normal']))
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("<b>Listing Status Options:</b>", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
listing_status = [
    ["Available", "Ready to show to clients"],
    ["Shown to Client", "You've presented this property"],
    ["Client Interested", "Client expressed interest"],
    ["Under Negotiation", "Terms being discussed"],
    ["Not Available", "No longer available"]
]
listing_table = Table(listing_status, colWidths=[1.8*inch, 3.7*inch])
listing_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fff0')),
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
story.append(listing_table)
story.append(Spacer(1, 0.3*inch))

# Section 5: Commission
story.append(PageBreak())
story.append(Paragraph("💰 5. COMMISSION STRUCTURE", heading_style))
commission_info = """
<b>Your Commission Share:</b> 10% of total brokerage<br/>
<b>Admin Share:</b> 90% of total brokerage<br/>
<br/>
<b>Example Calculation:</b><br/>
- Brokerage from Owner: ₹25,000<br/>
- Brokerage from Client: ₹25,000<br/>
- Total Brokerage: ₹50,000<br/>
- Number of Brokers: 1<br/>
- <b>Your Commission: ₹5,000</b><br/>
- Admin Share: ₹45,000<br/>
<br/>
<i>Note: Admin handles all deal closures and commission calculations. 
You can view your total commission on the dashboard.</i>
"""
story.append(Paragraph(commission_info, styles['Normal']))
story.append(Spacer(1, 0.3*inch))

# Section 6: Email Notifications
story.append(Paragraph("📧 6. EMAIL NOTIFICATIONS", heading_style))
story.append(Paragraph("<b>You Will Receive Emails When:</b>", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
partner_emails = """
✅ Admin assigns a new client to you<br/>
- Email includes: Client name, contact number, budget range, property preferences, location
"""
story.append(Paragraph(partner_emails, styles['Normal']))
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("<b>Admin Receives Emails When:</b>", styles['Normal']))
story.append(Spacer(1, 0.1*inch))
admin_emails = """
✅ You update a client status<br/>
✅ You mark a listing as "Shown to Client"<br/>
<br/>
<i>All emails come from: Lyns Estate Agency (lynsestateagency@gmail.com)</i>
"""
story.append(Paragraph(admin_emails, styles['Normal']))
story.append(Spacer(1, 0.3*inch))

# Section 7: Best Practices
story.append(PageBreak())
story.append(Paragraph("📝 7. BEST PRACTICES", heading_style))
best_practices = """
<b>1. Check Dashboard Daily</b><br/>
- Review new client assignments<br/>
- Monitor your commission progress<br/>
- Track overall status distribution<br/>
<br/>
<b>2. Update Status Regularly</b><br/>
- Keep Admin informed of all progress<br/>
- Update immediately after client interactions<br/>
- Use accurate status descriptions<br/>
<br/>
<b>3. Use Broker Contacts Effectively</b><br/>
- Call brokers to schedule site visits<br/>
- Coordinate timing with client availability<br/>
- Confirm property availability before showing<br/>
<br/>
<b>4. Link Clients to Listings</b><br/>
- When showing a property, always update the listing status<br/>
- Select the correct client name(s) in the dropdown<br/>
- This helps Admin track which properties were shown to whom<br/>
<br/>
<b>5. Maintain Professionalism</b><br/>
- Respond promptly to new assignments<br/>
- Follow up with clients consistently<br/>
- Keep accurate records of all interactions<br/>
<br/>
<b>6. Communication</b><br/>
- If you face any issues, contact Admin immediately<br/>
- Provide feedback on client preferences<br/>
- Report any property concerns
"""
story.append(Paragraph(best_practices, styles['Normal']))
story.append(Spacer(1, 0.3*inch))

# Section 8: FAQ
story.append(PageBreak())
story.append(Paragraph("❓ 8. FREQUENTLY ASKED QUESTIONS", heading_style))
story.append(Spacer(1, 0.2*inch))

faq_items = [
    ("Can I add new clients?", 
     "No, only Admin can add clients to the system. New clients will be assigned to you by Admin."),
    
    ("Can I see all listings in the system?", 
     "You can only see listings that Admin has marked as 'Visible to Partner'. This ensures you focus on relevant properties."),
    
    ("How do I schedule a site visit?", 
     "Use the Broker Contact number shown in the listing details. Call the broker directly to coordinate the visit."),
    
    ("When do I get paid my commission?", 
     "Admin closes all deals and handles payment processing. Your commission share will be calculated automatically, and you can track it on your dashboard."),
    
    ("What if a client is not responding?", 
     "Update the status to 'On Hold' and inform Admin. You can also add notes in the requirements field."),
    
    ("Can I see other partners' clients?", 
     "No, you can only see clients assigned specifically to you for privacy and efficiency."),
    
    ("What if I have technical issues?", 
     "Contact Admin (Lyndon) immediately via email or phone. Include screenshots if possible."),
    
    ("Can I change my password?", 
     "Contact Admin to reset your password. For security, don't share your credentials with anyone.")
]

for question, answer in faq_items:
    story.append(Paragraph(f"<b>Q: {question}</b>", styles['Normal']))
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph(f"<b>A:</b> {answer}", styles['Normal']))
    story.append(Spacer(1, 0.15*inch))

# Support Section
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("🆘 SUPPORT & CONTACT", heading_style))
support_info = """
<b>For any questions, issues, or support:</b><br/>
<br/>
<b>Email:</b> lynsestateagency@gmail.com<br/>
<b>Admin:</b> Lyndon<br/>
<br/>
<i>Response time: Within 24 hours on business days</i><br/>
<br/>
---<br/>
<br/>
<b>Thank you for being part of Lyns Real Estate!</b><br/>
Your dedication helps us serve our clients better.
"""
story.append(Paragraph(support_info, styles['Normal']))

# Build PDF
doc.build(story)
print(f"✅ PDF created successfully: {pdf_file}")
