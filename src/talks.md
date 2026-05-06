---
title: Talks
layout: default
nav_order: 2
---
<link rel="stylesheet" href="/assets/css/main.css" type="text/css">

<h1>Invited Talks</h1>

<p>Below is a list of invited talks, conference talks, and guest lectures, sorted by date (most recent first). All talks are in-person if not marked as online.</p>

{% if site.data.talks.talks %}
  <ul class="talks-list">
  {% assign sorted_presentations = site.data.talks.talks | sort_presentations %}

  {% assign total = sorted_presentations | size %}
  {% assign counter = total %}

  {% for presentation in sorted_presentations %}
    <li class="link-item">
      [{{ counter }}] {{ presentation.title }}
      
      <span class="description">
        <em class="talks-location">{{ presentation.venue }} @ {{ presentation.location }}
        {% if presentation.online %}
          (Online)
        {% endif %}
        </em><br>
        
        {{ presentation.type | capitalize }}
        
        <span class="pipe">|</span>
        {{ presentation.month }} {{ presentation.year }}
        
        {% if presentation.youtube %}
          <span class="pipe">|</span>
          <a href="https://youtube.com/watch?v={{ presentation.youtube }}" target="_blank">YouTube</a>
        {% endif %}
      </span>
    </li>
    
    {% assign counter = counter | minus: 1 %}
  {% endfor %}
  </ul>
{% else %}
  <p class="error">Error: No presentation data found. Please check <code>_data/talks/talks.yml</code>.</p>
{% endif %}
