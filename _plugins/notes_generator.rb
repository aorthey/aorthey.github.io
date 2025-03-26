require 'pdf-reader'

module Jekyll
  class PdfListGenerator < Generator
    safe true

    def humanize_filename(filename)
      # Split camelCase at uppercase letters, join with spaces
      filename.gsub(/([A-Z])/, ' \1').strip.split.map(&:capitalize).join(' ')
    end

    def generate(site)
      pdf_dir = File.join(site.source, "assets", "notes")
      return unless Dir.exist?(pdf_dir)

      pdf_data = []
      keyword_groups = Hash.new { |h, k| h[k] = [] }
      ungrouped = []

      Dir.glob(File.join(pdf_dir, "*.pdf")).each do |pdf_path|
        begin
          filename = File.basename(pdf_path, ".pdf")
          reader = PDF::Reader.new(pdf_path)

          # Get metadata
          info = reader.info
          title = info[:Title] || humanize_filename(filename)
          keywords = info[:Keywords] || ""

          # Process keywords
          keyword_list = keywords.split(',').map { |k| k.strip.downcase }.reject(&:empty?)
          pdf_url = "/assets/notes/#{File.basename(pdf_path)}"

          # Create PDF data entry
          pdf_entry = {
            "title" => title,
            "url" => pdf_url,
            "keywords" => keyword_list
          }
          puts "Keywords: #{keyword_list}"

          # Add to basic list
          pdf_data << pdf_entry

          # Group by keywords
          if keyword_list.any?
            keyword_list.each do |keyword|
              keyword_groups[keyword] << pdf_entry
            end
          else
            ungrouped << pdf_entry
          end

        rescue StandardError => e
          Jekyll.logger.warn "PDF Processing Error:", "Could not process #{pdf_path}: #{e.message}"
          next
        end
      end

      # Structure the data for Jekyll
      grouped_data = keyword_groups.map { |keyword, entries|
        { "keyword" => keyword, "pdfs" => entries }
      }

      site.data["notes_list"] = {
        "all" => pdf_data,
        "grouped" => grouped_data,
        "ungrouped" => ungrouped
      }
    end
  end
end
