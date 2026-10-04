SITE = "https://aadityakumawat.me"
EMAIL = "aaditya@aadityakumawat.me"
EMAIL2 = "aaditya.kumawat21@gmail.com"
GITHUB = "https://github.com/AadityaK21"
LINKEDIN = "https://www.linkedin.com/in/aaditya-kumawat-9588012b2/"
CODEFORCES = "https://codeforces.com/profile/codeleon"
ORCID = "https://orcid.org/0009-0001-2877-2219"
CV = "/assets/Aaditya_Kumawat_CV.pdf"
VERSION = "4"

ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2.5 8h10.5M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
DOWN = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2v9.5M4.2 7.8 8 11.6l3.8-3.8M3 14.2h10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
COPY = '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="5.2" y="5.2" width="8.3" height="8.3" rx="1.6" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M10.8 3.4V3.2a1.2 1.2 0 0 0-1.2-1.2H3.6a1.2 1.2 0 0 0-1.2 1.2v6a1.2 1.2 0 0 0 1.2 1.2h.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
THEME = '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 1.7a6.3 6.3 0 0 1 0 12.6z" fill="currentColor"/></svg>'
BACK = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M13.5 8H3M7 4 3 8l4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def head(title, desc, path, extra="", og="/og.png"):
    url = SITE + path
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="author" content="Aaditya Kumawat">
<meta name="theme-color" content="#f1f1ef">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Aaditya Kumawat">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}{og}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.png" type="image/png" sizes="64x64">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/atom+xml" title="Notes by Aaditya Kumawat" href="/notes/feed.xml">
<link rel="preload" href="/assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>
<script>try{{if(localStorage.getItem("theme")==="dark")document.documentElement.setAttribute("data-theme","dark")}}catch(e){{}}</script>
<link rel="stylesheet" href="/assets/css/site.css?v={VERSION}">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(home=False):
    pre = "" if home else "/"
    return f"""<header class="site-header wrap" id="top">
  <a class="logo" href="/" aria-label="Aaditya Kumawat, home">ak<span class="logo-dot"></span></a>
  <nav class="nav" aria-label="Main">
    <a href="{pre}#work">Work</a>
    <a href="{pre}#research">Research</a>
    <a href="/notes/">Notes</a>
    <a href="{pre}#about">About</a>
    <a href="{pre}#contact">Contact</a>
  </nav>
  <div class="header-actions">
    <button class="theme-toggle" type="button" data-theme-toggle aria-pressed="false" aria-label="Switch to dark mode">{THEME}</button>
    <a class="btn btn-sm btn-dl header-cv" href="{CV}" download aria-label="Download CV (PDF)"><span class="btn-label">Download CV</span><span class="btn-icon">{DOWN}</span></a>
  </div>
</header>
"""


def footer():
    return f"""<footer class="site-footer wrap">
  <span>&copy; <span data-year>2026</span> Aaditya Kumawat</span>
  <span>New Delhi, <span class="num" data-clock data-short>IST</span></span>
  <span><a href="{GITHUB}">GitHub</a> &nbsp; <a href="{LINKEDIN}">LinkedIn</a> &nbsp; <a href="#top">Back to top</a></span>
</footer>
<script src="/assets/js/site.js?v={VERSION}" defer></script>
<script data-goatcounter="https://aadityakumawat.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
"""
