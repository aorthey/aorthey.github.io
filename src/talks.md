---
title: Talks
layout: default
nav_order: 2
---

<link rel="stylesheet" href="/assets/css/main.css" type="text/css">
<h1>Invited Talks</h1>

Below is a list of invited talks, conference talks, and guest lectures, sorted by date (most recent
first). All talks are in-person if not marked as online.

<!-- {% if site.data.talks.talks %} -->
<!--   <dl class="talks-list"> -->
<!--   {% assign sorted_presentations = site.data.talks.talks | sort_presentations %} -->
<!--   {% for presentation in sorted_presentations %} -->
<!--     <dt><strong>{{ presentation.name }}</strong></dt> -->
<!--     <dd> -->
<!--       <em>{{ presentation.location }}</em><br> -->
<!--       {{ presentation.type | capitalize }} <span class="pipe">|</span> {{ presentation.month }} {{ presentation.year }} -->
<!--     </dd> -->
<!--   {% endfor %} -->
<!--   </dl> -->
<!-- {% else %} -->
<!--   <p class="error">Error: No presentation data found. Please check <code>_data/talks/talks.yml</code>.</p> -->
<!-- {% endif %} -->

{% if site.data.talks.talks %}
  <ul class="talks-list">
  {% assign sorted_presentations = site.data.talks.talks | sort_presentations %}
  {% for presentation in sorted_presentations %}
    <li class="link-item"><strong>{{ presentation.name }}</strong>
    <span class="description">
      <em class="talks-location">{{ presentation.location }}</em><br>
      {{ presentation.type | capitalize }} 
      {% if presentation.online %}
        <span class="online">(Online)</span>
      {% endif %}
      <span class="pipe">|</span> {{ presentation.month }} {{ presentation.year }}
    </span>
    </li>
  {% endfor %}
  </ul>
{% else %}
  <p class="error">Error: No presentation data found. Please check <code>_data/talks/talks.yml</code>.</p>
{% endif %}
