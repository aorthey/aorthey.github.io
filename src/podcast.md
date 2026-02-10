---
title: Podcast
layout: default
nav_order: 2
---

<link rel="stylesheet" href="/assets/css/main.css" type="text/css">

<h1>Andreas Orthey Podcast</h1>
<div class="default" margin-left="100px" align="center">
    <p>
    This long-form podcast (around 60-90 minutes per episode) explores the lives and ideas of technological visionaries. Each episode discusses state-of-the-art topics in science and technology while exploring the personal stories and biographies of the people behind those topics.

    Available on
    </p>
    <div class="links-wrapper">
    <a target="_blank" class="general-link" href="https://www.youtube.com/@andreasorthey">@YouTube</a>
    <a target="_blank" class="general-link" href="https://podcasters.spotify.com/pod/show/andreasorthey">@Spotify</a>
    <a target="_blank" class="general-link" href="https://podcasts.apple.com/us/podcast/andreas-orthey-podcast/id1812910570">@Apple</a>
    <a target="_blank" class="general-link" href="https://x.com/andreas_orthey">@X</a>
    <a target="_blank" class="general-link" href="https://anchor.fm/s/fb9fc38c/podcast/rss">RSS Feed</a>

    </div>
</div>

<h2 align="left">List of Episodes</h2>
{% assign total_podcasts = site.data.podcasts | size %}
{% for podcast in site.data.podcasts %}
{% assign episode_number = total_podcasts | minus: forloop.index0 %}

<!-- Reverse podcast order (episode 01 first): -->
<!-- for podcast in site.data.podcasts reversed %} -->
<!-- assign episode_number = forloop.index %} -->
<!-- Normal podcast order (last episode first) -->
<!-- for podcast in site.data.podcasts -->
<!-- assign episode_number = total_podcasts | minus: forloop.index0 -->
<div class="podcast-item">
  <div class="thumbnail-container">
  <a href="https://www.youtube.com/watch?v={{ podcast.youtube_id }}">
    <img align="center" src="{{ podcast.thumbnail }}" alt="{{ podcast.title }} thumbnail">
  </a>
  </div>
  <div class="podcast-content">
    {% assign duration_seconds = podcast.duration | default: 0 %}
    {% assign hours = duration_seconds | divided_by: 3600 %}
    {% assign remainder = duration_seconds | modulo: 3600 %}
    {% assign minutes = remainder | divided_by: 60 %}
    {% assign seconds = remainder | modulo: 60 %}
    <h3>#{{ episode_number }}: {{ podcast.title }}
      [{{ hours | prepend: '0' | slice: -2, 2 }}:{{ minutes | prepend: '0' | slice: -2, 2 }}:{{ seconds | prepend: '0' | slice: -2, 2 }}]
    </h3>
    <p>
      {% if podcast.youtube %}
        <a target="_blank" class="general-link" href="{% if podcast.youtube contains 'http' %}{{ podcast.youtube }}{% else %}https://www.youtube.com/watch?v={{ podcast.youtube }}{% endif %}">Watch on YouTube</a>
      {% endif %}
      {% if podcast.spotify %}
        <a target="_blank" class="general-link" href="{% if podcast.spotify contains 'http' %}{{ podcast.spotify }}{% else %}https://open.spotify.com/episode/{{ podcast.spotify }}{% endif %}">Listen on Spotify</a>
      {% endif %}
      {% if podcast.apple %}
        <a target="_blank" class="general-link" href="{{ podcast.apple }}">Listen on Apple</a>
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
