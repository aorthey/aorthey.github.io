---
title: Podcast
layout: default
nav_order: 2
---

<link rel="stylesheet" href="/assets/css/main.css" type="text/css">

<h1>Andreas Orthey Podcast</h1>
<div class="image-text-container-podcast">
  <img src="/assets/images/podcast-portrait.png" alt="Podcast Logo" title="Podcast Logo" class="circular-image">
      <div margin-left="100px" align="center">
          <p>Conversations on Robotics. Available on</p>
          <div class="links-wrapper">
          <a target="_blank" class="general-link" href="https://www.youtube.com/@andreasorthey">@YouTube</a>
          <a target="_blank" class="general-link" href="https://podcasters.spotify.com/pod/show/andreasorthey">@Spotify</a>
          <a target="_blank" class="general-link" href="https://x.com/andreas_orthey">@X</a>
          </div>
      </div>

</div>

<h2 align="left">List of Episodes</h2>
{% assign total_podcasts = site.data.podcasts | size %}
{% for podcast in site.data.podcasts %}
{% assign episode_number = total_podcasts | minus: forloop.index0 %}
<div class="podcast-item">
  <div class="thumbnail-container">
  <a href="https://www.youtube.com/watch?v={{ podcast.youtube_id }}">
    <img align="center" src="http://img.youtube.com/vi/{{ podcast.youtube_id }}/maxresdefault.jpg" alt="{{ podcast.title }} thumbnail">
  </a>
  </div>
  <div class="podcast-content">
    <h3>#{{ episode_number }}: {{ podcast.title }}</h3>
    <p>
      <a target="_blank" class="general-link" href="https://www.youtube.com/watch?v={{ podcast.youtube_id }}">Watch on YouTube</a>
      {% if podcast.spotify %}
        <a target="_blank" class="general-link" href="{% if podcast.spotify contains 'http' %}{{ podcast.spotify }}{% else %}https://open.spotify.com/episode/{{ podcast.spotify }}{% endif %}">Listen on Spotify</a>
      {% endif %}
      {% if podcast.x %}
        <a target="_blank" class="general-link" href="{% if podcast.x contains 'http' %}{{ podcast.x }}{% else %}https://x.com/i/web/status/{{ podcast.x }}{% endif %}">View on X</a>
      {% endif %}
      {% if podcast.outline %}
        <a target="_blank" class="general-link" href="{{ podcast.outline }}">Outline</a>
      {% endif %}
      {% if podcast.transcript %}
        <a target="_blank" class="general-link" href="{{ podcast.transcript }}">Transcript</a>
      {% endif %}
      {% if podcast.errata %}
        <a target="_blank" class="general-link" href="{{ podcast.errata }}">Errata</a>
      {% endif %}
    </p>
  </div>
</div>
{% endfor %}
