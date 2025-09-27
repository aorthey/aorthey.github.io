# Step to Publish a Podcast Episode

0. We assume that you have finished editing a podcast episode, which is already
   rendered from blender and which we call here `podcast.mp4`. 
1. Create a new episode folder in `assets/podcast`. Formatting: Increasing
   number with `_` as delimiter and lowercase name of guest.
2. Add a `headshot.png` file to this folder with the face of the podcast guest
3. Run script `podcast_generate_thumbnails.py` and verify that output looks
   correct for both `thumbnail.png` and `thumbnail_squared.png`
4. Create a file `metadata.yml` in the episode folder (you can use `metadata-template.yml` as a template)
5. Add title, description, content (and optionally episode-links, references, errata, clips) to `metadata.yml` file.
6. Upload the episode `podcast.mp4` to youtube (as unlisted) and add link to `metadata.yml`. Do
   not add the episode to any playlist, because that would make it public.
7. Run `scripts/update_titles_and_description.py` to update title and
   description on youtube from `metadata.yml` file (do that such that
`metadata.yml` represents always the ground truth).
8. Send youtube link to podcast guest and wait for approval/comments.
9. Upload episode to spotify (Link is creators.spotify.com/pod/). Use the script
   `scripts/update_titles_and_description.py --generate-spotify` to generate
title and description (you have to copy them manually to spotify). Upload the
`thumbnail.png` and the `thumbnail_square.png` as episode art.
10. Update the spotify link in `metadata.yml` file.
11. Refresh the RSS feed on apple until the episode has been updated: https://podcastsconnect.apple.com/. Add the link to the `metadata.yml` file.
12. Write a post on X using the description as the post and the content as the first comment. Add the `podcast.mp4` video directly to the post.
13. Update the X link in `metadata.yml` file and verify that all links are correct (youtube, spotify, x, apple)
14. Go to youtube and set the episode to public.
15. Write LinkedIn post using the description, references, and links. Use
    `scripts/make_linkedin_post.py` to generate the post.

Additional Steps:
- Generate transcripts using the script `scripts/generate_transcript.py`.
