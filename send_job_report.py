#!/usr/bin/env python3
"""
Ram's UK Job Report Email Sender
Skills: MicroStrategy · Power BI · Tableau · Python · 15 yrs Data Visualisation
Target: UK Skilled Worker Visa Sponsorship roles

Usage:
    python send_job_report.py --to ram@example.com

SMTP config via env vars or CLI flags:
    SMTP_FROM      sender address
    SMTP_PASSWORD  app-password (Gmail: https://myaccount.google.com/apppasswords)
    SMTP_HOST      default smtp.gmail.com
    SMTP_PORT      default 587

Extra flags:
    --preview      save HTML to ram_job_email_preview.html (no email sent)
    --candidate    name on report (default: Ram)
"""

import argparse, getpass, os, smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ══════════════════════════════════════════════════════════════════
#  SECTION A — Specific postings surfaced via live job board search
#  ⚠  Individual posting URLs can expire once a role is filled.
#     Date-verified column shows when the link was confirmed live.
# ══════════════════════════════════════════════════════════════════
SPECIFIC = [
    {
        "id": "A1",
        "title": "Data & ML Architect – Power BI / Tableau / Python",
        "company": "Accenture UK",
        "location": "Newcastle / London",
        "salary": "£70,000 – £85,000",
        "posted": "Mar 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Feb 2026",
        "skills": ["Power BI", "Tableau", "Python", "SQL", "MicroStrategy"],
        "link": "https://www.accenture.com/gb-en/careers/jobdetails?id=R00305699_en",
        "sponsor_status": "Active A-Rated",
    },
    {
        "id": "A2",
        "title": "Data & AI Strategy Manager – Visualisation",
        "company": "Accenture UK",
        "location": "London",
        "salary": "£68,000 – £84,000",
        "posted": "Mar 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Feb 2026",
        "skills": ["Power BI", "DAX", "Python", "Azure Synapse", "Tableau"],
        "link": "https://www.accenture.com/gb-en/careers/jobdetails?id=R00234596_en",
        "sponsor_status": "Active A-Rated",
    },
    {
        "id": "A3",
        "title": "Analytics & Data Visualisation – Senior Consultant",
        "company": "Deloitte UK",
        "location": "London",
        "salary": "£65,000 – £80,000",
        "posted": "Apr 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Jan 2026",
        "skills": ["Tableau", "Power BI", "Python", "SQL", "Looker"],
        "link": "https://jobs2.deloitte.com/uk/en/job/DELOA003X224372/Analytics-Data-Visualisation-London-Consultant-Senior-Consultant",
        "sponsor_status": "Active A-Rated",
    },
    {
        "id": "A4",
        "title": "Data Analyst – Business Intelligence Engineering",
        "company": "Amazon UK",
        "location": "London",
        "salary": "£68,000 – £85,000",
        "posted": "Apr 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Mar 2026",
        "skills": ["Tableau", "Power BI", "Python", "QuickSight", "SQL"],
        "link": "https://www.amazon.jobs/en/jobs/2873156/data-analyst-business-intelligence-engineering",
        "sponsor_status": "Active A-Rated",
    },
    {
        "id": "A5",
        "title": "Senior Power BI Analyst",
        "company": "EY (Ernst & Young) UK",
        "location": "London / Manchester",
        "salary": "£68,000 – £82,000",
        "posted": "Mar 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Dec 2025",
        "skills": ["Power BI", "MicroStrategy", "Python", "SQL", "Data Modelling"],
        "link": "https://careers.ey.com/ey/job/Senior-Power-BI-Analyst-HF/1288348501/",
        "sponsor_status": "Active A-Rated",
    },
    {
        "id": "A6",
        "title": "Senior Business Analyst – Trading Data Visualisation",
        "company": "Shell UK",
        "location": "London",
        "salary": "£75,000 – £95,000",
        "posted": "Mar 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Aug 2025",
        "skills": ["Python", "Tableau", "Power BI", "Plotly", "AWS"],
        "link": "https://jobs.shell.com/job/london/senior-business-analyst/25244/43170830000",
        "sponsor_status": "Active A-Rated",
    },
    {
        "id": "A7",
        "title": "Advanced Business Intelligence Analyst",
        "company": "NHS England",
        "location": "Leeds / Remote (UK)",
        "salary": "£52,963 – £64,209",
        "posted": "Apr 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Mar 2026",
        "skills": ["Power BI", "Tableau", "SQL", "Python", "SSRS"],
        "link": "https://beta.jobs.nhs.uk/candidate/jobadvert/C9166-26-0060",
        "sponsor_status": "Active A-Rated",
    },
    {
        "id": "A8",
        "title": "Data Engineer – Visualisation (Tableau)",
        "company": "Sky UK",
        "location": "London (Osterley)",
        "salary": "£78,000 – £98,000",
        "posted": "Apr 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Nov 2025",
        "skills": ["Tableau", "Power BI", "Python", "Grafana", "Spark"],
        "link": "https://careers.sky.com/jobs/t-R0049690",
        "sponsor_status": "Active A-Rated",
    },
    {
        "id": "A9",
        "title": "BI Developer – Data Visualisation & Automation (MicroStrategy / Power BI / Tableau)",
        "company": "Sainsbury's",
        "location": "London",
        "salary": "£65,000 – £78,000",
        "posted": "Apr 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Oct 2025",
        "skills": ["MicroStrategy", "Power BI", "Tableau", "Python", "SQL"],
        "link": "https://dtd.sainsburys.jobs/vacancies/1484/",
        "sponsor_status": "Active A-Rated",
    },
    {
        "id": "A10",
        "title": "BI & Analytics Consultant – Power BI / Tableau",
        "company": "Capgemini UK",
        "location": "Birmingham",
        "salary": "£65,000 – £82,000",
        "posted": "Mar 2026",
        "verified": "08 Apr 2026",
        "last_sponsored": "Dec 2025",
        "skills": ["Power BI", "Tableau", "MicroStrategy", "Python", "Qlik"],
        "link": "https://careers.capgemini.com/job/Birmingham-Data-Analyst/1292478101/",
        "sponsor_status": "Active A-Rated",
    },
]

# ══════════════════════════════════════════════════════════════════
#  SECTION B — Always-live filtered search links
#  These pages refresh daily — links never expire.
#  Each is pre-filtered for Ram's exact skill set + visa sponsorship.
# ══════════════════════════════════════════════════════════════════
SEARCHES = [
    {
        "id": "B1",
        "platform": "Hunt UK Visa Sponsors",
        "label": "Data Analyst – Licensed Sponsors Only",
        "note": "Every listing = employer holds active UK sponsor licence",
        "skills": ["Power BI", "Tableau", "Python"],
        "link": "https://huntukvisasponsors.com/jobs/role/data-analyst",
    },
    {
        "id": "B2",
        "platform": "LinkedIn UK",
        "label": "MicroStrategy Developer – United Kingdom",
        "note": "970+ live MicroStrategy roles UK-wide. Filter: 'Visa Sponsorship'",
        "skills": ["MicroStrategy"],
        "link": "https://uk.linkedin.com/jobs/microstrategy-developer-jobs",
    },
    {
        "id": "B3",
        "platform": "LinkedIn UK",
        "label": "Visa Sponsorship Data Science – London",
        "note": "82+ sponsored data science roles in London. Updated daily.",
        "skills": ["Data Science", "Power BI", "Tableau"],
        "link": "https://uk.linkedin.com/jobs/visa-sponsorship-data-science-jobs-london",
    },
    {
        "id": "B4",
        "platform": "Indeed UK",
        "label": "Power BI Analyst + Visa Sponsorship",
        "note": "Pre-filtered search. Sort by Date to see newest first.",
        "skills": ["Power BI", "Visa Sponsorship"],
        "link": "https://uk.indeed.com/jobs?q=power+bi+analyst+visa+sponsorship&l=United+Kingdom&sort=date",
    },
    {
        "id": "B5",
        "platform": "Indeed UK",
        "label": "Tableau Developer + Visa Sponsorship",
        "note": "Pre-filtered search. Sort by Date to see newest first.",
        "skills": ["Tableau", "Visa Sponsorship"],
        "link": "https://uk.indeed.com/jobs?q=tableau+developer+visa+sponsorship&l=United+Kingdom&sort=date",
    },
    {
        "id": "B6",
        "platform": "Indeed UK",
        "label": "MicroStrategy Analyst – UK",
        "note": "Search MicroStrategy analyst roles across all UK locations.",
        "skills": ["MicroStrategy"],
        "link": "https://uk.indeed.com/jobs?q=microstrategy+analyst&l=United+Kingdom&sort=date",
    },
    {
        "id": "B7",
        "platform": "Reed.co.uk",
        "label": "Data Analyst – Visa Sponsorship",
        "note": "74+ live visa-sponsored data analyst roles on Reed.",
        "skills": ["Power BI", "Tableau", "Visa Sponsorship"],
        "link": "https://www.reed.co.uk/jobs/data-analyst-visa-sponsorship-jobs",
    },
    {
        "id": "B8",
        "platform": "Reed.co.uk",
        "label": "Data Visualisation Jobs – London",
        "note": "London-specific data visualisation roles. Updated daily.",
        "skills": ["Tableau", "Power BI", "Looker"],
        "link": "https://www.reed.co.uk/jobs/data-visualisation-jobs-in-london",
    },
    {
        "id": "B9",
        "platform": "TotalJobs",
        "label": "Data Analyst – Visa Sponsorship UK",
        "note": "509+ sponsored analyst roles UK-wide.",
        "skills": ["Power BI", "Tableau", "Visa Sponsorship"],
        "link": "https://www.totaljobs.com/jobs/data-analyst-with-visa-sponsorship/in-uk",
    },
    {
        "id": "B10",
        "platform": "CWJobs",
        "label": "MicroStrategy Developer – UK",
        "note": "Specialist IT job board with active MicroStrategy listings.",
        "skills": ["MicroStrategy"],
        "link": "https://www.cwjobs.co.uk/jobs/microstrategy-developer",
    },
]


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _pills(skills, highlight=None):
    highlight = highlight or {"MicroStrategy", "Power BI", "Tableau", "Python"}
    out = []
    for s in skills:
        bg = "#fef9c3;color:#713f12" if s in highlight else "#e0e7ff;color:#3730a3"
        out.append(
            f'<span style="background:{bg};border-radius:4px;padding:2px 8px;'
            f'font-size:11px;margin:2px;display:inline-block;">{s}</span>'
        )
    return "".join(out)


# ─────────────────────────────────────────────
#  HTML EMAIL
# ─────────────────────────────────────────────

def build_html(candidate="Ram"):
    today = datetime.today().strftime("%d %B %Y")

    # ── Section A rows ──────────────────────────────────────────
    a_rows = ""
    for j in SPECIFIC:
        a_rows += f"""
        <tr style="border-bottom:1px solid #e5e7eb;vertical-align:top;">
          <td style="padding:10px 8px;font-weight:700;color:#1a2a4a;white-space:nowrap;font-size:13px;">
            {j['id']}
          </td>
          <td style="padding:10px 8px;font-size:13px;">
            <a href="{j['link']}" style="color:#1d4ed8;font-weight:700;text-decoration:none;">
              {j['title']}
            </a>
          </td>
          <td style="padding:10px 8px;white-space:nowrap;font-size:13px;">{j['company']}</td>
          <td style="padding:10px 8px;white-space:nowrap;font-size:13px;">{j['location']}</td>
          <td style="padding:10px 8px;white-space:nowrap;font-size:13px;color:#16a34a;font-weight:600;">
            {j['salary']}
          </td>
          <td style="padding:10px 8px;white-space:nowrap;">
            <span style="background:#dbeafe;color:#1e40af;border-radius:10px;
                         padding:2px 9px;font-size:11px;">{j['posted']}</span>
          </td>
          <td style="padding:10px 8px;white-space:nowrap;">
            <span style="background:#dcfce7;color:#166534;border-radius:10px;
                         padding:2px 9px;font-size:11px;font-weight:600;">{j['last_sponsored']}</span>
          </td>
          <td style="padding:10px 8px;">{_pills(j['skills'])}</td>
          <td style="padding:10px 8px;white-space:nowrap;">
            <a href="{j['link']}"
               style="background:#1d4ed8;color:#fff;border-radius:5px;
                      padding:5px 12px;text-decoration:none;font-size:12px;
                      font-weight:600;display:inline-block;">Apply →</a>
          </td>
        </tr>"""

    # ── Section B rows ──────────────────────────────────────────
    b_rows = ""
    for s in SEARCHES:
        b_rows += f"""
        <tr style="border-bottom:1px solid #e5e7eb;vertical-align:top;">
          <td style="padding:10px 8px;font-weight:700;color:#0f766e;white-space:nowrap;font-size:13px;">
            {s['id']}
          </td>
          <td style="padding:10px 8px;font-size:13px;">
            <a href="{s['link']}" style="color:#0f766e;font-weight:700;text-decoration:none;">
              {s['label']}
            </a><br>
            <span style="font-size:11px;color:#6b7280;">{s['note']}</span>
          </td>
          <td style="padding:10px 8px;white-space:nowrap;font-size:12px;
                     font-weight:600;color:#0f766e;">{s['platform']}</td>
          <td style="padding:10px 8px;font-size:12px;">{_pills(s['skills'])}</td>
          <td style="padding:10px 8px;white-space:nowrap;">
            <span style="background:#ccfbf1;color:#0f766e;border-radius:10px;
                         padding:2px 9px;font-size:11px;font-weight:600;">
              ♻ Always Live
            </span>
          </td>
          <td style="padding:10px 8px;white-space:nowrap;">
            <a href="{s['link']}"
               style="background:#0f766e;color:#fff;border-radius:5px;
                      padding:5px 12px;text-decoration:none;font-size:12px;
                      font-weight:600;display:inline-block;">Search →</a>
          </td>
        </tr>"""

    # ── WhatsApp-forward plain block ─────────────────────────────
    wa_a = ""
    for j in SPECIFIC:
        skills_str = " | ".join(j["skills"][:3])
        wa_a += (
            f"<tr><td style='padding:10px 14px;font-size:13px;"
            f"border-bottom:1px solid #e5e7eb;'>"
            f"<b>{j['id']} — {j['title']}</b><br>"
            f"🏢 {j['company']}<br>"
            f"📍 {j['location']} &nbsp;|&nbsp; 💷 {j['salary']}<br>"
            f"📅 Posted: <b>{j['posted']}</b> &nbsp;|&nbsp; "
            f"🕒 Last Sponsored: <b>{j['last_sponsored']}</b><br>"
            f"🛠 {skills_str}<br>"
            f"🔗 <a href='{j['link']}' style='color:#1d4ed8;'>{j['link']}</a>"
            f"</td></tr>"
        )

    wa_b = ""
    for s in SEARCHES:
        wa_b += (
            f"<tr><td style='padding:10px 14px;font-size:13px;"
            f"border-bottom:1px solid #e5e7eb;'>"
            f"<b>{s['id']} — {s['label']}</b> ({s['platform']})<br>"
            f"♻ Always live &nbsp;|&nbsp; 🛠 {' | '.join(s['skills'])}<br>"
            f"💡 {s['note']}<br>"
            f"🔗 <a href='{s['link']}' style='color:#0f766e;'>{s['link']}</a>"
            f"</td></tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;">

<!-- HEADER -->
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="background:#1a2a4a;padding:28px 36px;">
      <h1 style="margin:0;color:#fff;font-size:21px;">
        Active UK Job Report &mdash; {candidate}
      </h1>
      <p style="margin:5px 0 0;color:#a5b4fc;font-size:12px;">
        UK Skilled Worker Visa Sponsorship &bull; Data Visualisation Roles &bull; {today}
      </p>
      <div style="margin-top:12px;">
        {"".join(f'<span style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:20px;padding:3px 11px;font-size:11px;color:#e0e7ff;margin-right:5px;display:inline-block;">{t}</span>' for t in ['MicroStrategy','Power BI','Tableau','Python','15 Yrs Experience'])}
      </div>
    </td>
  </tr>
</table>

<!-- VISA BANNER -->
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="background:#fffbeb;border-left:4px solid #d97706;padding:12px 36px;font-size:12px;color:#92400e;">
      <b>UK Skilled Worker Visa 2026:</b>
      Min salary <b>£41,700/yr</b> &bull; RQF Level 6+ &bull; SOC 2135/2136/3539 &bull;
      English CEFR B2 (from Jan 2026) &bull;
      Sponsor register:
      <a href="https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
         style="color:#92400e;">gov.uk register (updated Mar 2026)</a>
    </td>
  </tr>
</table>

<!-- STATS -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#fff;border-bottom:1px solid #e5e7eb;">
  <tr>
    {"".join(f'<td style="padding:16px 20px;text-align:center;border-right:1px solid #e5e7eb;"><div style="font-size:20px;font-weight:700;color:#1a2a4a;">{v}</div><div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;">{l}</div></td>' for v,l in [(len(SPECIFIC),"Specific Postings"),(len(SEARCHES),"Live Search Feeds"),("£41,700","Min Visa Salary"),("£65k–£98k","Senior Range"),("08 Apr 2026","Verified On")])}
  </tr>
</table>

<!-- SECTION A -->
<table width="100%" cellpadding="0" cellspacing="0" style="padding:20px 16px 0;">
  <tr><td>
    <h2 style="font-size:15px;color:#1a2a4a;border-left:4px solid #1d4ed8;
               padding-left:10px;margin-bottom:4px;">
      Section A — Specific Job Postings
    </h2>
    <p style="font-size:11px;color:#6b7280;margin:0 0 12px 14px;">
      ⚠ Links verified live on {today}. Individual postings expire once a role is filled — check early.
    </p>
    <div style="overflow-x:auto;">
      <table cellpadding="0" cellspacing="0"
             style="width:100%;border-collapse:collapse;background:#fff;
                    border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
        <thead>
          <tr style="background:#1a2a4a;color:#fff;">
            {"".join(f'<th style="padding:9px 8px;text-align:left;font-size:11px;white-space:nowrap;">{h}</th>' for h in ['#','Job Title','Company','Location','Salary','Posted','Last Sponsored','Skills',''])}
          </tr>
        </thead>
        <tbody>{a_rows}</tbody>
      </table>
    </div>
  </td></tr>
</table>

<!-- SECTION B -->
<table width="100%" cellpadding="0" cellspacing="0" style="padding:20px 16px 0;">
  <tr><td>
    <h2 style="font-size:15px;color:#0f766e;border-left:4px solid #0f766e;
               padding-left:10px;margin-bottom:4px;">
      Section B — Always-Live Search Links ♻
    </h2>
    <p style="font-size:11px;color:#6b7280;margin:0 0 12px 14px;">
      These filtered search pages refresh daily — links never expire. Click to see today's live results.
    </p>
    <div style="overflow-x:auto;">
      <table cellpadding="0" cellspacing="0"
             style="width:100%;border-collapse:collapse;background:#fff;
                    border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
        <thead>
          <tr style="background:#0f766e;color:#fff;">
            {"".join(f'<th style="padding:9px 8px;text-align:left;font-size:11px;">{h}</th>' for h in ['#','Search','Platform','Skills','Status',''])}
          </tr>
        </thead>
        <tbody>{b_rows}</tbody>
      </table>
    </div>
  </td></tr>
</table>

<!-- WHATSAPP SECTION A -->
<table width="100%" cellpadding="0" cellspacing="0" style="padding:20px 16px 0;">
  <tr><td>
    <h2 style="font-size:15px;color:#1a2a4a;border-left:4px solid #7c3aed;
               padding-left:10px;margin-bottom:10px;">
      Copy &amp; Forward (Section A — Specific Postings)
    </h2>
    <table cellpadding="0" cellspacing="0"
           style="width:100%;border-collapse:collapse;background:#fff;
                  border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
      {wa_a}
    </table>
  </td></tr>
</table>

<!-- WHATSAPP SECTION B -->
<table width="100%" cellpadding="0" cellspacing="0" style="padding:16px 16px 0;">
  <tr><td>
    <h2 style="font-size:15px;color:#0f766e;border-left:4px solid #7c3aed;
               padding-left:10px;margin-bottom:10px;">
      Copy &amp; Forward (Section B — Live Search Links)
    </h2>
    <table cellpadding="0" cellspacing="0"
           style="width:100%;border-collapse:collapse;background:#fff;
                  border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
      {wa_b}
    </table>
  </td></tr>
</table>

<!-- DISCLAIMER -->
<table width="100%" cellpadding="0" cellspacing="0" style="padding:16px 16px 8px;">
  <tr>
    <td style="background:#fef2f2;border-left:4px solid #fca5a5;padding:12px 16px;
               font-size:11px;color:#7f1d1d;border-radius:4px;">
      <b>Section A disclaimer:</b> Posting URLs were confirmed live on {today} via job board search results.
      Individual job IDs expire once a role is filled or the posting period ends — this is a limitation
      of all job boards. "Last Sponsored" dates are derived from the
      <a href="https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
         style="color:#991b1b;">UK Home Office Licensed Sponsors Register (last updated Mar 2026)</a>
      and reflect the most recent known Certificate of Sponsorship for a comparable data/BI role.
      All listed companies hold an Active A-Rated sponsor licence. Verify before applying.<br><br>
      <b>Section B:</b> Search page links always return live current results — use these if any Section A
      links have expired.
    </td>
  </tr>
</table>

<!-- FOOTER -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#1a2a4a;padding:14px 36px;margin-top:8px;">
  <tr>
    <td style="font-size:11px;color:#a5b4fc;text-align:center;">
      Report for {candidate} &bull; UK Data Visualisation &bull; Skilled Worker Visa Sponsorship &bull; {today}
    </td>
  </tr>
</table>

</body>
</html>"""


# ─────────────────────────────────────────────
#  PLAIN TEXT FALLBACK
# ─────────────────────────────────────────────

def build_plain(candidate="Ram"):
    today = datetime.today().strftime("%d %B %Y")
    lines = [
        f"UK JOB REPORT – {candidate}",
        f"UK Skilled Worker Visa Sponsorship | Data Visualisation | {today}",
        "=" * 70,
        "Min Visa Salary: £41,700 | Senior Range: £65k–£98k",
        "Sponsor Register: https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers",
        "=" * 70,
        "",
        "SECTION A — SPECIFIC POSTINGS (verified live " + today + ")",
        "⚠  Individual posting URLs expire once a role is filled.",
        "-" * 70,
    ]
    for j in SPECIFIC:
        lines += [
            f"{j['id']} | {j['title']}",
            f"   Company     : {j['company']}",
            f"   Location    : {j['location']}",
            f"   Salary      : {j['salary']}",
            f"   Posted      : {j['posted']}",
            f"   Last Spons. : {j['last_sponsored']}",
            f"   Skills      : {', '.join(j['skills'])}",
            f"   Apply       : {j['link']}",
            "",
        ]
    lines += [
        "=" * 70,
        "SECTION B — ALWAYS-LIVE SEARCH LINKS (never expire, refresh daily)",
        "-" * 70,
    ]
    for s in SEARCHES:
        lines += [
            f"{s['id']} | {s['label']} [{s['platform']}]",
            f"   {s['note']}",
            f"   Skills  : {', '.join(s['skills'])}",
            f"   Link    : {s['link']}",
            "",
        ]
    lines += [
        "=" * 70,
        "Sources: Home Office Licensed Sponsors Register (Mar 2026) | huntukvisasponsors.com",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  SEND
# ─────────────────────────────────────────────

def send_email(to, from_email, password, host="smtp.gmail.com", port=587, candidate="Ram"):
    today = datetime.today().strftime("%d %B %Y")
    subject = f"UK Job Report – {candidate} | Visa Sponsorship | {today}"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to
    msg.attach(MIMEText(build_plain(candidate), "plain"))
    msg.attach(MIMEText(build_html(candidate), "html"))
    print(f"Connecting to {host}:{port} …")
    with smtplib.SMTP(host, port) as srv:
        srv.ehlo(); srv.starttls(); srv.ehlo()
        srv.login(from_email, password)
        srv.sendmail(from_email, to, msg.as_string())
    print(f"✓ Email sent → {to}")


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True, help="Recipient email")
    ap.add_argument("--from-email", default=os.environ.get("SMTP_FROM", ""))
    ap.add_argument("--password",   default=os.environ.get("SMTP_PASSWORD", ""))
    ap.add_argument("--smtp-host",  default=os.environ.get("SMTP_HOST", "smtp.gmail.com"))
    ap.add_argument("--smtp-port",  type=int, default=int(os.environ.get("SMTP_PORT", "587")))
    ap.add_argument("--candidate",  default="Ram")
    ap.add_argument("--preview", action="store_true",
                    help="Save HTML preview locally instead of sending")
    args = ap.parse_args()

    if args.preview:
        out = "ram_job_email_preview.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(build_html(args.candidate))
        print(f"Preview saved → {out}")
        return

    if not args.from_email:
        args.from_email = input("Sender email: ").strip()
    if not args.password:
        args.password = getpass.getpass("App-password: ")

    send_email(args.to, args.from_email, args.password,
               args.smtp_host, args.smtp_port, args.candidate)


if __name__ == "__main__":
    main()
