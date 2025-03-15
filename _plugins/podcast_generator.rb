require 'httparty'
require 'yaml'

module Jekyll
  class PodcastGenerator < Generator
    safe true
    priority :normal

    def generate(site)
      podcast_data = []
      podcast_dir = File.join(site.source, "assets", "podcast")

      if Dir.exist?(podcast_dir)
        Dir.foreach(podcast_dir) do |folder|
          next if folder == '.' || folder == '..'

          folder_path = File.join(podcast_dir, folder)
          links_file = File.join(podcast_dir, folder, "links.yml")

          if File.exist?(links_file)
            begin
              links_data = YAML.load_file(links_file)

              if links_data && links_data["youtube"]
                youtube_id = links_data["youtube"]
                title = fetch_youtube_title(youtube_id)

                outline_path = File.exist?(File.join(folder_path, "outline.txt")) ? "/assets/podcast/#{folder}/outline.txt" : nil
                errata_path = File.exist?(File.join(folder_path, "errata.txt")) ? "/assets/podcast/#{folder}/errata.txt" : nil

                podcast_data << {
                  "folder" => folder,
                  "youtube_id" => youtube_id,
                  "spotify" => links_data["spotify"],
                  "x" => links_data["x"],
                  "title" => title || links_data["title"],
                  "outline" => outline_path,
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

    private

    def fetch_youtube_title(video_id)
      max_attempts = 5
      attempt = 1
      url = "https://www.youtube.com/watch?v=#{video_id}"

      while attempt <= max_attempts
        begin
          response = HTTParty.get(url, {
            headers: { "User-Agent" => "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" },
            timeout: 30 # Add timeout to prevent hanging
          })

          if response.success?
            match = response.body.match(/<title>(.*?) - YouTube<\/title>/)
            if match && match[1]
              Jekyll.logger.warn "Found #{match} | #{match[1]}"
              return match[1].split('|').first.strip
            end
          end

          # If we got here, title wasn't found - wait and retry
          return nil if attempt == max_attempts
          sleep_time = attempt * 2 # Increasing delay: 2, 4, 6, 8 seconds
          Jekyll.logger.warn "YouTube Scraper:", "Attempt #{attempt} failed for #{video_id}, retrying in #{sleep_time}s..."
          sleep(sleep_time)

        rescue => e
          if attempt == max_attempts
            Jekyll.logger.warn "YouTube Scraper:", "All attempts failed for #{video_id}: #{e.message}"
            return nil
          end
          sleep_time = attempt * 2
          Jekyll.logger.warn "YouTube Scraper:", "Attempt #{attempt} error for #{video_id}: #{e.message}, retrying in #{sleep_time}s..."
          sleep(sleep_time)
        end

        attempt += 1
      end
    end
  end
end
