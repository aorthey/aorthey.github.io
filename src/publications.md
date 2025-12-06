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
<a href="https://arxiv.org/search/?query=Andreas+Orthey&searchtype=all&abstracts=show&order=-announced_date_first&size=100" target="_blank">Link to arXiv Preprints</a>
</li>
<li>
<a href="https://dblp.org/pid/133/2362.html" target="_blank">Link to dblp Profile</a>
</li>
<li>
<a href="https://orcid.org/0000-0002-1478-1405" target="_blank">Link to orcid Profile</a>
</li>

<script src="{{ '/assets/js/copy-bibtex.js' | relative_url }}"></script>
<script src="{{ '/assets/js/toggle-bibtex.js' | relative_url }}"></script>

</ul>

{% assign pub_types = "Journal,Conference,Workshop,These" | split: "," %}

{% for type in pub_types %}
<h2>{{ site.data.pub_titles[type] | default: type }}</h2>

{% assign pubs = site.data.publications | where: "type", type %}

{% for pub in pubs %}
- {{ pub.authors }}, *{{ pub.title | replace: '*', '\*' | replace: '_', '\_' | replace: '[', '\[' | replace: ']', '\]' }}*, {{ pub.venue }}, {{ pub.year }}

  <div class="links-below-publication">
    <button class="general-link toggle-bibtex" data-target="bibtex-{{ forloop.index }}">
      BibTeX
    </button>
    <a href="{{ pub.pdf }}" class="general-link" target="_blank">PDF</a> 
    {% if pub.youtube %}<a href="https://youtube.com/watch?v={{ pub.youtube }}" class="general-link" target="_blank">YouTube</a>{% endif %} 
    {% if pub.website %}<a href="{{ pub.website }}" class="general-link" target="_blank">Website</a>{% endif %}
    {% if pub.code %}<a href="{{ pub.code }}" class="general-link" target="_blank">Code</a>{% endif %}
  </div>
  <div id="bibtex-{{ forloop.index }}" class="bibtex-textfield hidden">
    <button class="general-link copy-bibtex-button" title="Copy BibTeX to clipboard">
      <img src="{{ '/assets/icons/copy-icon.png' | relative_url }}" alt="Copy" class="copy-icon">
      Copy to Clipboard
    </button>
    <pre><code>{{ pub.bibtex }}</code></pre>
  </div>

{% endfor %}

{% endfor %}

<h2>Supervised Student Theses</h2>

{% assign sorted_students = site.data.students.students | sort_students %} 

{% for student in sorted_students %}

{% if student.type == 'bsc' %}
  {% assign display_type = 'B.Sc.' %}
{% elsif student.type == 'msc' %}
  {% assign display_type = 'M.Sc.' %}
{% elsif student.type == 'phd' %}
  {% assign display_type = 'Ph.D.' %}
{% else %}
  {% assign display_type = student.type %}
{% endif %}
- {{ student.name }}, *{{ student.title }}*, 
  {{ display_type }} Thesis,
  {{ student.institution }},
  {{ student.year }}
  {% if student.expected %} (Expected){% endif %}

{% endfor %}
