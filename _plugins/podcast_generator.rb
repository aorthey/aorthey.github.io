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
                  "title" => title || folder,
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
      url = "https://www.youtube.com/watch?v=#{video_id}"
      response = HTTParty.get(url, {
        headers: { "User-Agent" => "Mozilla/5.0" } # YouTube might block requests without a proper User-Agent
      })
      
      if response.success?
        match = response.body.match(/<title>(.*?) - YouTube<\/title>/)
        if match && match[1]
          # Split on '|' and take the first part, then strip whitespace
          Jekyll.logger.warn "Found #{match} | #{match[1]}"
          return match[1].split('|').first
        end
      end
      nil
    rescue => e
      Jekyll.logger.warn "YouTube Scraper:", "Error fetching title for #{video_id}: #{e.message}"
      nil
    end
  end
end
