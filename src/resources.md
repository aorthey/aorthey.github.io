---
title: Resources
layout: default
nav_order: 2
---

<link rel="stylesheet" href="/assets/css/main.css" type="text/css">

<h1>Resources</h1>

Here are some learning resources that I created. This includes teaching notes, motion planning
lecture slides (created jointly with <a href="https://imrclab.github.io/teaching/motion-planning" target="_blank">Wolfgang Hönig</a>), and code libraries which you might find helpful.

<!-- ------------------------------------------------------------------------------ -->

<h2>Teaching Notes</h2>

<ul>

{% assign pdfs = site.data.pdf-notes %}

{% for pdf in pdfs %}

<li class="link-item"> 
<a href="{{ pdf.filename }}" target="_blank">{{ pdf.title }} ({{ pdf.date }})</a>
<span class="description">{{ pdf.description }}</span>
</li>

{% endfor %}

</ul>
 
<!-- ------------------------------------------------------------------------------ -->

<h2>Motion Planning Lecture Slides</h2>

Please check <a href="https://imrclab.github.io/teaching/motion-planning" target="_blank">here</a> for an up-to-date version and videos.

<ul>
<li class="link-item"> 
<a href="/assets/lectures/motion-planning/01_lecture.pdf" target="_blank">Lecture 1</a>
<span class="description">Organization, Introduction, Problem Formulation</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/02_lecture.pdf" target="_blank">Lecture 2</a>
<span class="description">Transformations, Angular Representations, Metrics, Efficient Collision Checking</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/03_lecture.pdf" target="_blank">Lecture 3</a>
<span class="description">Graph-based Planning: Representations, A*, Admissible Heuristics</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/04_lecture.pdf" target="_blank">Lecture 4</a>
<span class="description">Advanced Search-Based Motion Planning</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/05_lecture.pdf" target="_blank">Lecture 5</a>
<span class="description">Sampling-Based Geometric Motion Planning: PRMs</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/06_lecture.pdf" target="_blank">Lecture 6</a>
<span class="description">Introduction to the Open Motion Planning Library
(OMPL)</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/07_lecture.pdf" target="_blank">Lecture 7</a>
<span class="description">RRT, RRT*, Kinodynamic RRT</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/08_lecture.pdf" target="_blank">Lecture 8</a>
<span class="description">Kinodynamic Planning: SST*, AO-x,
Geometric Planning: Informed RRT*, BIT*</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/09_lecture.pdf" target="_blank">Lecture 9</a>
<span class="description">Sampling-Based Motion Planning: Theory and
Advanced Planners; Intro to Optimization</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/10_lecture.pdf" target="_blank">Lecture 10</a>
<span class="description">Optimization-Based Motion Planning</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/11_lecture.pdf" target="_blank">Lecture 11</a>
<span class="description">Optimization-Based Motion Planning: Differential Flatness and SCP</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/12_lecture.pdf" target="_blank">Lecture 12</a>
<span class="description">Advanced Optimization, Comparison, and Hybrid
Approaches</span>
</li>

<li class="link-item"> 
<a href="/assets/lectures/motion-planning/13_lecture.pdf" target="_blank">Lecture 13</a>
<span class="description">Multi-robot Motion Planning</span>
</li>

</ul>

<!-- ------------------------------------------------------------------------------ -->

<h2>Code</h2>

<ul>

<li class="link-item"> 
<a href="https://github.com/aorthey/MotionExplorer" target="_blank">Motion Explorer</a>
<span class="description">
A framework to visualize the structure of planning problems using local-minima trees</span>
</li>

<li class="link-item"> 
<a href="https://github.com/aorthey/ompl_benchmark_plotter" target="_blank">OMPL Benchmark Plotter</a>
<span class="description">Plot benchmarks from the Open Motion Planning Library (OMPL)</span>
</li>

<li class="link-item"> 
<a href="https://github.com/aorthey/configuration-space-visualizer" target="_blank">Configuration Space Visualizer</a>
<span class="description">A visualization tool to visualize 2D configuration spaces for point robots.</span>
</li>

<li class="link-item"> 
<a href="https://github.com/aorthey/cpp-util" target="_blank">CPP Util</a>
<span class="description">Several handy C/C++ utility functions</span>
</li>

<li class="link-item"> 
<a href="https://github.com/aorthey/video_manipulation" target="_blank">FFmpeg Video Manipulation</a>
<span class="description">Interface to create and edit videos in python using ffmpeg-python.</span>
</li>

<li class="link-item"> 
<a href="https://github.com/aorthey/vim-snippets-additional" target="_blank">Vim Snippets Additional</a>
<span class="description">Vim snippets to optimize my workflow</span>
</li>

<li class="link-item"> 
<a href="https://github.com/aorthey/bpy-scripting" target="_blank">BPY Scripting</a>
<span class="description">Blender python bpy scripts</span>
</li>

</ul>
