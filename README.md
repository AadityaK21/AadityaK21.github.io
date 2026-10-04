# aadityakumawat.me

Personal site of Aaditya Kumawat, served by GitHub Pages at https://aadityakumawat.me.

Plain HTML, CSS and JavaScript. No build step and no framework: edit a file, commit, push, and Pages publishes it in about a minute.

## Layout

| Path | What it is |
|---|---|
| `index.html` | Home page: hero, selected work, research, recognition, about, contact |
| `work/<project>/index.html` | One case study per project (sextant, nanoserve, legal-audio, st-bemd, company-hub) |
| `404.html` | Not-found page |
| `assets/css/site.css` | All styles. Colours, fonts and spacing are tokens at the top of the file |
| `assets/js/site.js` | Local clock, hero name sizing, copy-email button, the fingerprint canvas |
| `assets/img/` | Project figures (WebP) |
| `assets/fonts/` | Archivo variable font, self-hosted |
| `assets/Aaditya_Kumawat_CV.pdf` | The CV behind every "Download CV" button. Replace the file to update it |
| `og.png` | Link preview image for WhatsApp, LinkedIn, Slack and so on |
| `CNAME` | Custom domain. Do not delete |
| `.nojekyll` | Tells Pages to serve the files as they are |

## Common edits

- **Update the CV:** replace `assets/Aaditya_Kumawat_CV.pdf`, keeping the same file name.
- **Change the email:** search for `aaditya@aadityakumawat.me` across the HTML files (it forwards to Gmail via Namecheap).
- **Add a photo to the hero:** put the image in `assets/img/` and, in `index.html`, replace the `<canvas data-ridges ...>` line inside `<figure class="portrait">` with `<img src="/assets/img/your-photo.webp" alt="Aaditya Kumawat">`.
- **Change the accent colour:** edit `--signal` at the top of `assets/css/site.css`.
- After changing CSS or JS, bump `?v=1` in the `<link>` and `<script>` tags so browsers fetch the new file.

## DNS (Namecheap)

Apex `A` records point at GitHub Pages: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`. `www` is a `CNAME` to the apex.
