---
title: Publications
layout: default
nav_order: 2
---

<link rel="stylesheet" href="/assets/css/main.css" type="text/css">

<h1>Publications</h1>
<a href="/assets/generate/all_publications.txt" target="_blank">View all publications as BibTeX</a>

{% assign pub_types = "Journal,Conference,Workshop,These" | split: "," %}

{% for type in pub_types %}
<h2>{{ site.data.pub_titles[type] | default: type }}</h2>

{% assign pubs = site.data.publications | where: "type", type %}

{% for pub in pubs %}
- {{ pub.authors }}, *{{ pub.title }}*, {{ pub.venue }}, {{ pub.year }}
  <div class="links-below-publication">
  <details>
    <summary>BibTeX</summary>
    <div class="bibtex-textfield">
      <pre><code>{{ pub.bibtex }}</code></pre>
    </div>
  </details>
  <a href="{{ pub.pdf }}" class="general-link" target="_blank">PDF</a> 
  {% if pub.youtube %}<a href="https://youtube.com/watch?v={{ pub.youtube }}" class="general-link" target="_blank">YouTube</a>{% endif %} 
  {% if pub.website %}<a href="{{ pub.website }}" class="general-link" target="_blank">Website</a>{% endif %}
  {% if pub.code %}<a href="{{ pub.code }}" class="general-link" target="_blank">Code</a>{% endif %}
  </div>

{% endfor %}

{% endfor %}
