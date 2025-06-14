require 'httparty'
require 'yaml'
require 'fastimage' # Add this to check image dimensions

module Jekyll
  class PodcastGenerator < Generator
    safe true
    priority :normal

    def extract_youtube_id(link)
      return link unless link.include?('http')

      patterns = [
        /(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
        /youtube\.com\/clip\/([a-zA-Z0-9_-]+)/
      ]

      patterns.each do |pattern|
        match = link.match(pattern)
        return match[1] if match
      end

      return link
    end

    def generate(site)
      podcast_data = []
      podcast_dir = File.join(site.source, "assets", "podcast")

      if Dir.exist?(podcast_dir)
        folders = Dir.entries(podcast_dir)
            .select { |f| File.directory?(File.join(podcast_dir, f)) && f != '.' && f != '..' }
            .sort
            .reverse
        folders.each do |folder|
          next if folder == '.' || folder == '..'

          folder_path = File.join(podcast_dir, folder)
          links_file = File.join(podcast_dir, folder, "links.yml")

          if File.exist?(links_file)
            begin
              links_data = YAML.load_file(links_file)

              if links_data && links_data["youtube"]
                outline_path = File.exist?(File.join(folder_path, "outline.txt")) ? "/assets/podcast/#{folder}/outline.txt" : nil
                errata_path = File.exist?(File.join(folder_path, "errata.txt")) ? "/assets/podcast/#{folder}/errata.txt" : nil
                transcript_path = File.exist?(File.join(folder_path, "transcript.txt")) ? "/assets/podcast/#{folder}/transcript.txt" : nil
                thumbnail_path = File.exist?(File.join(folder_path, "thumbnail.png")) ? "/assets/podcast/#{folder}/thumbnail.png" : nil

                # Check thumbnail dimensions if thumbnail exists
                if thumbnail_path
                  thumbnail_full_path = File.join(site.source, thumbnail_path)
                  dimensions = FastImage.size(thumbnail_full_path)
                  unless dimensions == [1280, 720]
                    raise "Thumbnail at #{thumbnail_path} has dimensions #{dimensions}, expected 1280x720"
                  end
                end

                podcast_data << {
                  "folder" => folder,
                  "youtube" => links_data["youtube"],
                  "youtube_id" => extract_youtube_id(links_data["youtube"]),
                  "spotify" => links_data["spotify"],
                  "apple" => links_data["apple"],
                  "x" => links_data["x"],
                  "title" => links_data["title"],
                  "outline" => outline_path,
                  "transcript" => transcript_path,
                  "thumbnail" => thumbnail_path,
                  "errata" => errata_path
                }
              end
            rescue => e
              Jekyll.logger.warn "Podcast Generator:", "Error processing #{links_file}: #{e.message}"
            end
          end
        end
      end

      site.data["podcasts"] = podcast_data
    end
  end
end
