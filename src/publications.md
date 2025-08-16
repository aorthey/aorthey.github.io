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


</ul>

{% assign pub_types = "Journal,Conference,Workshop,These" | split: "," %}

{% for type in pub_types %}
<h2>{{ site.data.pub_titles[type] | default: type }}</h2>

{% assign pubs = site.data.publications | where: "type", type %}

{% for pub in pubs %}
- {{ pub.authors }}, *{{ pub.title | replace: '*', '\*' | replace: '_', '\_' | replace: '[', '\[' | replace: ']', '\]' }}*, {{ pub.venue }}, {{ pub.year }}

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

<h2>Student Theses</h2>

- Nicolas Hargus, _Multi-Robot Motion Planning for Disassembly Tasks_, M.Sc. Thesis, Technische Universität Berlin, 2025 (Expected)

- Servet Bora Bayraktar, _Large-Scale Disassembly: Efficient Planning for Recycling using Path Defragmentation_, M.Sc. Thesis, Technische Universität Berlin, 2025 (Expected)

- Lennart Julian Droß, _Synthetic Datasets for Robot Manipulation Tasks using Procedural Content Generation_, B.Sc. Thesis, Technische Universität Berlin, 2025

- Theo Valentin Kern, _Rearrangement Planning for Construction Assembly using Teams of Multirotors_, M.Sc. Thesis, Technische Universität Berlin, 2023

- Andrey Solano, _Real-Time Multi-Robot Motion Planning using Decomposed Sampling-Based Methods_, M.Sc. Thesis, KTH Royal Institute of Technology, 2023

- Janis Eric Freund, _Asymptotically Optimal Belief Space Planning_, M.Sc. Thesis, Technische Universität Berlin, 2023

- Servet Bora Bayraktar, _Solving Rearrangement Puzzles Optimally using Fragmentation-Based Motion Planning_, B.Sc. Thesis, Technische Universität Berlin, 2022

- Ilyes Toumi, _Real-Time Task and Motion Planning for Dual-Arm Robots in a Bin-Picking Application_, M.Sc. Thesis, RWTH Aachen University, 2022

- Jay Prabodh Kamat, _Multimodal Optimization for Manipulation Tasks_, M.Sc. Thesis, Birla Institute of Technology and Science, 2022

- Noran Abdelsalam, _Assembly Sequence Planning of Architectural Structures_, B.Sc. Thesis, Technische Universität Berlin, 2021

- Francesco Grothe, _Bidirectional Tree Search Through Space-Time for Prioritized Multi-Robot Planning_, B.Sc. Thesis, Technische Universität Berlin, 2021

- Marie-Therese Khoury, _Efficient Sampling of Transition Constraints for Motion Planning under Sliding Contacts_, B.Sc. Thesis, Universität Stuttgart, 2020

- Alexander Harner, _Method to Optimize and Enumerate Local Minima in Probabilistic Roadmaps_, B.Sc. Thesis, Universität Stuttgart, 2020

- Azer Messaoudi, _An Optimization Algorithm for Dynamical Systems under Non-holonomic Constraints_, B.Sc. Thesis, Universität Stuttgart, 2020

- Sohaib Akbar, _Sparse and Optimal Planning Algorithms for Multilevel Motion Planning_, M.Sc. Thesis, Universität Stuttgart, 2020

- Benjamin Frész, _Visualization of Holonomic and Non-Holonomic Planning Problems_, B.Sc. Thesis, Universität Stuttgart, 2019
