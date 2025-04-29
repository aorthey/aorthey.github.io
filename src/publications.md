---
title: Publications
layout: default
nav_order: 2
---

<link rel="stylesheet" href="/assets/css/main.css" type="text/css">

<h1>Publications</h1>

<ul>

<li>
<a href="/assets/generate/all_publications.txt" target="_blank">View all Publications as BibTeX</a>
</li>
<li>
<a href="https://scholar.google.com/citations?user=bQKreEMAAAAJ" target="_blank">Link to Google Scholar Profile</a>
</li>
<li>
<a href="https://arxiv.org/find/all/1/au:+Orthey_Andreas/0/1/0/all/0/1?per_page=50" target="_blank">Link to arXiv Preprints</a>
</li>
<li>
<a href="https://dblp.org/pid/133/2362.html" target="_blank">Link to dblp Profile</a>
</li>

</ul>

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
