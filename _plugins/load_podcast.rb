require 'yaml'
require 'fastimage' # Add this to check image dimensions

module Jekyll
  class PodcastGenerator < Generator
    safe true
    priority :normal

    # Custom page class for fully virtual pages
    class GeneratedPage < Jekyll::Page
      def initialize(site, dir, name, content, data)
        @site = site
        @dir = dir
        @name = name
        @base = '' # Empty base to avoid source path
        self.process(name) # Sets basename, ext, path, url
        self.content = content
        self.data = data || {}
      end

      # Override to prevent file system access
      def read_yaml(*)
        # Do nothing, as we're not reading from disk
      end

      # Override path to avoid implying a source file
      def path
        File.join(@dir, @name)
      end
    end

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
          metadata_file = File.join(podcast_dir, folder, "metadata.yml")

          if File.exist?(metadata_file)
            begin
              metadata = YAML.load_file(metadata_file)

              required_keys = %w[title youtube]
              if metadata && required_keys.all? { |k| metadata.key?(k) }
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

                # Generate outline.txt from content
                outline_path = nil
                if metadata.key?("content") && metadata["content"]
                   outline_path = "/assets/podcast/#{folder}/outline.txt"
                   outline_content = metadata["content"].join("\n")
                   outline_page = GeneratedPage.new(site, File.join("assets/podcast", folder), "outline.txt", outline_content, { 'layout' => 'none', 'permalink' => outline_path })
                   site.pages << outline_page
                end

                # # Generate errata.txt if errata exists
                errata_path = nil
                if metadata.key?("errata") && metadata["errata"]
                  errata_path = "/assets/podcast/#{folder}/errata.txt"
                  errata_content = metadata["errata"].join("\n")
                  errata_page = GeneratedPage.new(site, File.join("assets/podcast", folder), "errata.txt", errata_content, { 'layout' => 'none', 'permalink' => errata_path })
                  site.pages << errata_page
                end

                podcast_data << {
                  "folder" => folder,
                  "youtube" => metadata["youtube"],
                  "youtube_id" => extract_youtube_id(metadata["youtube"]),
                  "spotify" => metadata["spotify"],
                  "apple" => metadata["apple"],
                  "x" => metadata["x"],
                  "title" => metadata["title"],
                  "outline" => outline_path,
                  "description" => metadata["description"],
                  "duration" => metadata["duration"],
                  "episode_links" => metadata["episode-links"],
                  "references" => metadata["references"],
                  "errata" => errata_path,
                  "transcript" => transcript_path,
                  "thumbnail" => thumbnail_path
                }
              end
            rescue => e
              Jekyll.logger.warn "Podcast Generator:", "Error processing #{metadata_file}: #{e.message}"
            end
          end
        end
      end

      site.data["podcasts"] = podcast_data
    end
  end
end
