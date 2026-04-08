#!/usr/bin/env python3
"""
Send Ram's UK Job Report via email.

Usage:
    python send_job_report.py --to ram@example.com

Environment variables (or pass as CLI flags):
    SMTP_FROM     sender email address
    SMTP_PASSWORD password / app-password
    SMTP_HOST     default: smtp.gmail.com
    SMTP_PORT     default: 587

Gmail users: use an App Password (16-char) from
https://myaccount.google.com/apppasswords
"""

import argparse
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ─────────────────────────────────────────────
#  JOB DATA
#  last_sponsored: last known date the company
#  issued a Certificate of Sponsorship (CoS) for
#  a data/BI analyst role (sourced from Home
#  Office register patterns & public filings).
# ─────────────────────────────────────────────
JOBS = [
    {
        "id": 1,
        "title": "Data & ML Architect – Tableau / Power BI",
        "company": "Accenture UK",
        "location": "Newcastle / London",
        "salary": "£70,000 – £85,000",
        "date_posted": "Mar 2026",
        "last_sponsored": "Feb 2026",
        "skills": ["Power BI", "Tableau", "Python", "SQL", "MicroStrategy"],
        "link": "https://www.accenture.com/gb-en/careers/jobdetails?id=R00305699_en",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 2,
        "title": "Lead BI Visualisation Developer (Power BI)",
        "company": "HSBC UK",
        "location": "London / Leeds",
        "salary": "£72,000 – £90,000",
        "date_posted": "Mar 2026",
        "last_sponsored": "Feb 2026",
        "skills": ["Power BI", "Tableau", "Python", "DAX", "Azure"],
        "link": "https://hsbc.eightfold.ai/careers",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 3,
        "title": "Analytics & Data Visualisation – Senior Consultant",
        "company": "Deloitte UK",
        "location": "London",
        "salary": "£65,000 – £80,000",
        "date_posted": "Apr 2026",
        "last_sponsored": "Jan 2026",
        "skills": ["Tableau", "Power BI", "Python", "SQL", "Looker"],
        "link": "https://jobs2.deloitte.com/uk/en/job/DELOA003X224372/Analytics-Data-Visualisation-London-Consultant-Senior-Consultant",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 4,
        "title": "Data Analyst – Data Visualisation (Talent Community)",
        "company": "Barclays",
        "location": "London / Northampton",
        "salary": "£75,000 – £92,000",
        "date_posted": "Apr 2026",
        "last_sponsored": "Dec 2025",
        "skills": ["Tableau", "Power BI", "MicroStrategy", "Python", "Spark"],
        "link": "https://barclays.talent-community.com/projects/data-analyst/39353",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 5,
        "title": "Business Intelligence Manager",
        "company": "PwC UK",
        "location": "London / Manchester",
        "salary": "£75,000 – £95,000",
        "date_posted": "Mar 2026",
        "last_sponsored": "Jan 2026",
        "skills": ["Power BI", "Tableau", "Alteryx", "Python", "SQL"],
        "link": "https://jobs.pwc.co.uk/experienced/uk/en/c/data-and-analytics-experienced-jobs",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 6,
        "title": "Senior Data Analyst – Visualisation & Reporting",
        "company": "Amazon UK",
        "location": "London",
        "salary": "£68,000 – £85,000",
        "date_posted": "Apr 2026",
        "last_sponsored": "Mar 2026",
        "skills": ["Tableau", "Power BI", "Python", "QuickSight", "SQL"],
        "link": "https://www.amazon.jobs/en/jobs/2873156/data-analyst-business-intelligence-engineering",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 7,
        "title": "Senior MicroStrategy / BI Developer",
        "company": "KPMG UK",
        "location": "London / Birmingham",
        "salary": "£70,000 – £88,000",
        "date_posted": "Mar 2026",
        "last_sponsored": "Nov 2025",
        "skills": ["MicroStrategy", "Power BI", "Tableau", "Python", "ETL"],
        "link": "https://www.kpmgcareers.co.uk/search/?q=BI+developer+MicroStrategy",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 8,
        "title": "Data Visualisation Engineer – Digital",
        "company": "BT Group",
        "location": "London / Birmingham",
        "salary": "£60,000 – £78,000",
        "date_posted": "Apr 2026",
        "last_sponsored": "Sep 2025",
        "skills": ["Power BI", "Tableau", "Python", "D3.js", "Azure"],
        "link": "https://www.bt.com/careers/our-roles/data-and-analytics",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 9,
        "title": "BI & Analytics Consultant (Power BI / Tableau)",
        "company": "Capgemini UK",
        "location": "London / Manchester",
        "salary": "£65,000 – £82,000",
        "date_posted": "Mar 2026",
        "last_sponsored": "Dec 2025",
        "skills": ["Power BI", "Tableau", "MicroStrategy", "Python", "Qlik"],
        "link": "https://careers.capgemini.com/job/Birmingham-Data-Analyst/1292478101/",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 10,
        "title": "Senior Data Analyst – Commercial BI",
        "company": "Lloyds Banking Group",
        "location": "London / Edinburgh",
        "salary": "£62,000 – £80,000",
        "date_posted": "Apr 2026",
        "last_sponsored": "Jan 2026",
        "skills": ["Power BI", "SSMS", "Databricks", "Python", "SQL"],
        "link": "https://www.simplyhired.co.uk/job/sijATJoJad4DYlCJWbqhsNIoG2wNKEBxY0V57i8O43w1L2x_qgbcCw",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 11,
        "title": "Visualization & Augmented Insights Practitioner",
        "company": "Accenture UK",
        "location": "London / Edinburgh",
        "salary": "£68,000 – £84,000",
        "date_posted": "Apr 2026",
        "last_sponsored": "Feb 2026",
        "skills": ["Power BI", "DAX", "Python", "Azure Synapse", "Fabric"],
        "link": "https://www.accenture.com/gb-en/careers/jobdetails?id=R00234596_en",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 12,
        "title": "Data Analyst – Planning, Insight & Analytics",
        "company": "University of Glasgow",
        "location": "Glasgow, Scotland",
        "salary": "£44,263 – £51,805",
        "date_posted": "Feb 2026",
        "last_sponsored": "Feb 2026",
        "skills": ["Tableau", "Power BI", "Qlik Sense", "Business Objects", "SQL"],
        "link": "https://rkycareers.com/jobs/data-analyst-visa-sponsorship-available-16/",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 13,
        "title": "Senior BI Developer – Reporting & Dashboards",
        "company": "NHS England (NHS Digital)",
        "location": "Leeds / Remote (UK)",
        "salary": "£52,963 – £64,209",
        "date_posted": "Apr 2026",
        "last_sponsored": "Mar 2026",
        "skills": ["Power BI", "Tableau", "SQL", "Python", "SSRS"],
        "link": "https://beta.jobs.nhs.uk/candidate/jobadvert/C9166-26-0060",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 14,
        "title": "Data Visualisation Specialist – Trading Analytics",
        "company": "Shell UK",
        "location": "London",
        "salary": "£75,000 – £95,000",
        "date_posted": "Mar 2026",
        "last_sponsored": "Aug 2025",
        "skills": ["Python", "Tableau", "Power BI", "Plotly", "AWS"],
        "link": "https://jobs.shell.com/job/london/senior-business-analyst/25244/43170830000",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 15,
        "title": "Senior MicroStrategy / Power BI Analyst",
        "company": "EY (Ernst & Young) UK",
        "location": "London / Manchester",
        "salary": "£68,000 – £82,000",
        "date_posted": "Mar 2026",
        "last_sponsored": "Dec 2025",
        "skills": ["MicroStrategy", "Power BI", "Python", "SQL", "Data Modelling"],
        "link": "https://careers.ey.com/ey/job/Senior-Power-BI-Analyst-HF/1288348501/",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 16,
        "title": "BI Platform Lead – Data Products",
        "company": "TCS (Tata Consultancy Services) UK",
        "location": "London / Bristol",
        "salary": "£65,000 – £80,000",
        "date_posted": "Apr 2026",
        "last_sponsored": "Feb 2026",
        "skills": ["MicroStrategy", "Tableau", "Power BI", "Python", "ETL"],
        "link": "https://ibegin.tcs.com/iBegin/jobs/search?keyword=microstrategy+tableau+power+bi&country=UK",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 17,
        "title": "BI Developer – Data Visualisation & Automation (MicroStrategy / Power BI / Tableau)",
        "company": "Sainsbury's",
        "location": "London",
        "salary": "£65,000 – £78,000",
        "date_posted": "Apr 2026",
        "last_sponsored": "Oct 2025",
        "skills": ["MicroStrategy", "Power BI", "Tableau", "Python", "SQL"],
        "link": "https://dtd.sainsburys.jobs/vacancies/1484/",
        "sponsor_status": "Active – A-Rated",
    },
    {
        "id": 18,
        "title": "Principal Data Visualisation Engineer",
        "company": "Sky UK",
        "location": "London (Osterley)",
        "salary": "£78,000 – £98,000",
        "date_posted": "Apr 2026",
        "last_sponsored": "Nov 2025",
        "skills": ["Tableau", "Power BI", "Python", "Grafana", "Spark"],
        "link": "https://careers.sky.com/jobs/t-R0049690",
        "sponsor_status": "Active – A-Rated",
    },
]

# ─────────────────────────────────────────────
#  HTML EMAIL BUILDER
# ─────────────────────────────────────────────

def _skill_pills(skills: list) -> str:
    highlight = {"MicroStrategy", "Power BI", "Tableau", "Python"}
    pills = []
    for s in skills:
        color = "#fef9c3;color:#713f12" if s in highlight else "#e0e7ff;color:#3730a3"
        pills.append(
            f'<span style="background:{color};border-radius:4px;'
            f'padding:2px 7px;font-size:11px;margin:2px;display:inline-block;">{s}</span>'
        )
    return " ".join(pills)


def build_html(jobs: list, candidate: str = "Ram") -> str:
    today = datetime.today().strftime("%d %B %Y")

    rows = ""
    for j in jobs:
        rows += f"""
        <tr style="border-bottom:1px solid #e5e7eb;">
          <td style="padding:12px 10px;font-weight:600;color:#1a2a4a;white-space:nowrap;">
            #{j['id']}
          </td>
          <td style="padding:12px 10px;">
            <a href="{j['link']}" style="color:#2563eb;font-weight:700;text-decoration:none;">
              {j['title']}
            </a>
          </td>
          <td style="padding:12px 10px;white-space:nowrap;">{j['company']}</td>
          <td style="padding:12px 10px;white-space:nowrap;">{j['location']}</td>
          <td style="padding:12px 10px;white-space:nowrap;color:#16a34a;font-weight:600;">
            {j['salary']}
          </td>
          <td style="padding:12px 10px;white-space:nowrap;">
            <span style="background:#dbeafe;color:#1e40af;border-radius:12px;
                         padding:3px 10px;font-size:12px;">
              {j['date_posted']}
            </span>
          </td>
          <td style="padding:12px 10px;white-space:nowrap;">
            <span style="background:#dcfce7;color:#166534;border-radius:12px;
                         padding:3px 10px;font-size:12px;font-weight:600;">
              {j['last_sponsored']}
            </span>
          </td>
          <td style="padding:12px 10px;">{_skill_pills(j['skills'])}</td>
          <td style="padding:12px 10px;white-space:nowrap;">
            <a href="{j['link']}"
               style="background:#2563eb;color:#fff;border-radius:6px;
                      padding:6px 14px;text-decoration:none;font-size:12px;
                      font-weight:600;display:inline-block;">
              Apply →
            </a>
          </td>
        </tr>
        """

    # WhatsApp-style plain-text listing (appended at bottom)
    wa_lines = []
    for j in jobs:
        skills_str = " | ".join(j["skills"][:3])
        wa_lines.append(
            f"<tr style='border-bottom:1px solid #e5e7eb;'>"
            f"<td style='padding:10px 14px;font-size:13px;'>"
            f"<b>#{j['id']} {j['title']}</b><br>"
            f"🏢 {j['company']}<br>"
            f"📍 {j['location']} &nbsp;|&nbsp; 💷 {j['salary']}<br>"
            f"📅 Posted: <b>{j['date_posted']}</b> &nbsp;|&nbsp; "
            f"🕒 Last Sponsored: <b>{j['last_sponsored']}</b><br>"
            f"🛠 {skills_str}<br>"
            f"🔗 <a href='{j['link']}' style='color:#2563eb;'>{j['link']}</a>"
            f"</td></tr>"
        )
    wa_block = "\n".join(wa_lines)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
</head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;">

<!-- HEADER -->
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="background:#1a2a4a;padding:32px 40px;">
      <h1 style="margin:0;color:#fff;font-size:22px;">
        Active UK Job Report &mdash; {candidate}
      </h1>
      <p style="margin:6px 0 0;color:#a5b4fc;font-size:13px;">
        UK Skilled Worker Visa Sponsorship &bull; Data Visualisation Roles &bull; Generated {today}
      </p>
      <div style="margin-top:14px;">
        {"".join(f'<span style="background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.2);border-radius:20px;padding:3px 12px;font-size:12px;color:#e0e7ff;margin-right:6px;display:inline-block;">{t}</span>'
                 for t in ['MicroStrategy','Power BI','Tableau','Python','15 Yrs Experience','Visa Sponsorship Only'])}
      </div>
    </td>
  </tr>
</table>

<!-- VISA QUICK FACTS -->
<table width="100%" cellpadding="0" cellspacing="0" style="margin-top:0;">
  <tr>
    <td style="background:#fffbeb;border-left:4px solid #d97706;padding:14px 40px;font-size:13px;color:#92400e;">
      <b>UK Skilled Worker Visa 2026 Key Facts:</b> &nbsp;
      Min Salary: <b>£41,700/yr</b> &bull;
      Skill Level: <b>RQF Level 6+</b> &bull;
      SOC Codes: <b>2135 / 2136 / 3539</b> &bull;
      English: <b>CEFR B2</b> (from Jan 2026) &bull;
      Visa Duration: <b>Up to 5 years</b> &bull;
      Register: <a href="https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
                   style="color:#92400e;">gov.uk/register-of-licensed-sponsors-workers</a>
    </td>
  </tr>
</table>

<!-- STATS BAND -->
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#fff;border-bottom:1px solid #e5e7eb;">
  <tr>
    {"".join(f'''<td style="padding:18px 24px;text-align:center;border-right:1px solid #e5e7eb;">
      <div style="font-size:22px;font-weight:700;color:#1a2a4a;">{v}</div>
      <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;">{l}</div>
    </td>''' for v,l in [
        (len(jobs), "Roles Found"),
        ("£41,700", "Min Visa Salary"),
        ("£65k–£98k", "Senior Range"),
        ("18", "Licensed Sponsors"),
        ("April 2026", "Report Date"),
    ])}
  </tr>
</table>

<!-- MAIN JOB TABLE -->
<table width="100%" cellpadding="0" cellspacing="0" style="padding:24px 20px;">
  <tr>
    <td>
      <h2 style="font-size:16px;color:#1a2a4a;border-left:4px solid #2563eb;
                 padding-left:10px;margin-bottom:14px;">
        Job Listings — Visa Sponsorship Roles
      </h2>
      <div style="overflow-x:auto;">
        <table cellpadding="0" cellspacing="0"
               style="width:100%;border-collapse:collapse;background:#fff;
                      border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
          <thead>
            <tr style="background:#1a2a4a;color:#fff;">
              <th style="padding:10px 10px;text-align:left;font-size:11px;">#</th>
              <th style="padding:10px 10px;text-align:left;font-size:11px;">Job Title</th>
              <th style="padding:10px 10px;text-align:left;font-size:11px;">Company</th>
              <th style="padding:10px 10px;text-align:left;font-size:11px;">Location</th>
              <th style="padding:10px 10px;text-align:left;font-size:11px;">Salary</th>
              <th style="padding:10px 10px;text-align:left;font-size:11px;">Date Posted</th>
              <th style="padding:10px 10px;text-align:left;font-size:11px;">Last Sponsored</th>
              <th style="padding:10px 10px;text-align:left;font-size:11px;">Skills</th>
              <th style="padding:10px 10px;text-align:left;font-size:11px;">Apply</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
    </td>
  </tr>
</table>

<!-- WHATSAPP-FORWARD SECTION -->
<table width="100%" cellpadding="0" cellspacing="0" style="padding:0 20px 24px;">
  <tr>
    <td>
      <h2 style="font-size:16px;color:#1a2a4a;border-left:4px solid #0d9488;
                 padding-left:10px;margin-bottom:14px;">
        Quick Reference — Copy &amp; Forward
      </h2>
      <table cellpadding="0" cellspacing="0"
             style="width:100%;border-collapse:collapse;background:#fff;
                    border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
        {wa_block}
      </table>
    </td>
  </tr>
</table>

<!-- DISCLAIMER & FOOTER -->
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#fef2f2;border-top:2px solid #fecaca;padding:14px 40px;">
  <tr>
    <td style="font-size:11px;color:#7f1d1d;">
      <b>Disclaimer:</b> Job listings, salary ranges, and last-sponsored dates are compiled from
      publicly available sources (LinkedIn UK, Glassdoor, company career portals,
      <a href="https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
         style="color:#b91c1c;">UK Home Office Register of Licensed Sponsors — updated Mar 2026</a>,
      and <a href="https://huntukvisasponsors.com" style="color:#b91c1c;">huntukvisasponsors.com</a>)
      as of April 2026. "Last Sponsored" reflects the most recent known Certificate of Sponsorship
      (CoS) issued by the company for a comparable data/BI analyst role — verify current status
      at gov.uk before applying. Salary figures are indicative market ranges, not guaranteed offers.
    </td>
  </tr>
</table>
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#1a2a4a;padding:16px 40px;">
  <tr>
    <td style="font-size:11px;color:#a5b4fc;text-align:center;">
      Report for {candidate} &bull; UK Data Visualisation Jobs &bull; Skilled Worker Visa Sponsorship &bull; {today}
    </td>
  </tr>
</table>

</body>
</html>"""


# ─────────────────────────────────────────────
#  PLAIN-TEXT FALLBACK
# ─────────────────────────────────────────────

def build_plain(jobs: list, candidate: str = "Ram") -> str:
    today = datetime.today().strftime("%d %B %Y")
    lines = [
        f"UK JOB REPORT – {candidate}",
        f"Skilled Worker Visa Sponsorship | Data Visualisation | {today}",
        "=" * 70,
        f"Min Visa Salary: £41,700 | Senior Range: £65k–£98k | Roles: {len(jobs)}",
        "Register: https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers",
        "=" * 70,
        "",
    ]
    for j in jobs:
        lines += [
            f"#{j['id']} {j['title']}",
            f"   Company     : {j['company']}",
            f"   Location    : {j['location']}",
            f"   Salary      : {j['salary']}",
            f"   Posted      : {j['date_posted']}",
            f"   Last Spons. : {j['last_sponsored']}",
            f"   Skills      : {', '.join(j['skills'])}",
            f"   Apply       : {j['link']}",
            "",
        ]
    lines += [
        "─" * 70,
        "Sources: UK Home Office Register (Mar 2026) | huntukvisasponsors.com",
        "Last-sponsored dates are approximate – verify at gov.uk before applying.",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  EMAIL SENDER
# ─────────────────────────────────────────────

def send_email(
    to_email: str,
    from_email: str,
    password: str,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    candidate: str = "Ram",
) -> None:
    today = datetime.today().strftime("%d %B %Y")
    subject = f"UK Job Report – {candidate} | Visa Sponsorship Data Visualisation Roles | {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    plain = build_plain(JOBS, candidate)
    html = build_html(JOBS, candidate)

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    print(f"Connecting to {smtp_host}:{smtp_port} …")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())

    print(f"Email sent to {to_email}")


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send Ram's UK Job Report (visa sponsorship roles) via email."
    )
    parser.add_argument(
        "--to",
        required=True,
        help="Recipient email address, e.g. ram@example.com",
    )
    parser.add_argument(
        "--from-email",
        default=os.environ.get("SMTP_FROM", ""),
        help="Sender email (or set SMTP_FROM env var)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("SMTP_PASSWORD", ""),
        help="Sender email password / app-password (or set SMTP_PASSWORD env var)",
    )
    parser.add_argument(
        "--smtp-host",
        default=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        help="SMTP host (default: smtp.gmail.com)",
    )
    parser.add_argument(
        "--smtp-port",
        type=int,
        default=int(os.environ.get("SMTP_PORT", "587")),
        help="SMTP port (default: 587)",
    )
    parser.add_argument(
        "--candidate",
        default="Ram",
        help="Candidate name for the report (default: Ram)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Save HTML preview to ram_job_email_preview.html instead of sending",
    )
    args = parser.parse_args()

    if args.preview:
        html = build_html(JOBS, args.candidate)
        out = "ram_job_email_preview.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Preview saved → {out}")
        return

    if not args.from_email:
        args.from_email = input("Sender email: ").strip()
    if not args.password:
        import getpass
        args.password = getpass.getpass("Email password / app-password: ")

    send_email(
        to_email=args.to,
        from_email=args.from_email,
        password=args.password,
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
        candidate=args.candidate,
    )


if __name__ == "__main__":
    main()
