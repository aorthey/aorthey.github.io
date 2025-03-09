---
title: Publications
nav_order: 2
layout: default
---

<!-- <script src="{{ '/assets/js/copy-bibtex.js' | relative_url }}"></script> -->
<link rel="stylesheet" href="/assets/css/main.css" type="text/css">

# Publications

{% assign pub_types = "Journal,Conference,Other" | split: "," %}
{% for type in pub_types %}
## {{ type }}s

{% assign pubs = site.data.publications | where: "type", type %}
{% for pub in pubs %}
- {{ pub.authors }}, *{{ pub.title }}*, {{ pub.venue }}, {{ pub.year }} 
<a href="{{ pub.pdf }}" class="bibtex-link" target="_blank">PDF</a>
  <details>
    <summary>BibTeX</summary>
    <div class="bibtex-container">
      <pre><code>{{ pub.bibtex }}</code></pre>
    </div>
  </details>
{% endfor %}

{% endfor %}

