# _plugins/bibtex_parser.rb
require 'bibtex'

module Jekyll
  class BibtexDataGenerator < Generator
    safe true
    priority :high

    def clean_latex(text)
      cleaned = text
                .gsub(/{\~n}/, 'ñ')
                .gsub(/{~n}/, 'ñ')
                .gsub(/~n/, 'ñ')
                .gsub(/{\'e}/, 'é')
                .gsub(/{'e}/, 'é')
                .gsub(/'e/, 'é')
                .gsub(/{\`e}/, 'è')
                .gsub(/{`e}/, 'è')
                .gsub(/`e/, 'è')
                .gsub(/{\"o}/, 'ö')
                .gsub(/{"o}/, 'ö')
                .gsub(/"o/, 'ö')
                .gsub(/{\"a}/, 'ä')
                .gsub(/{"a}/, 'ä')
                .gsub(/"a/, 'ä')
                .gsub(/{\"u}/, 'ü')
                .gsub(/{"u}/, 'ü')
                .gsub(/"u/, 'ü')
                .gsub(/{\"u}/, 'ü')
                .gsub(/{"u}/, 'ü')
                .gsub(/"u/, 'ü')
                .gsub(/{\"i}/, 'ï')
                .gsub(/{"i}/, 'ï')
                .gsub(/"i/, 'ï')
                .gsub(/{\"I}/, 'Ï')
                .gsub(/{"I}/, 'Ï')
                .gsub(/"I/, 'Ï')
                .gsub(/{}/, '')
                .gsub(/\\/, '')
                .gsub(/[{}]/, '')
      if cleaned != text
        Jekyll.logger.debug "Raw author text: #{text}"
        Jekyll.logger.debug "Cleaned author text: #{cleaned}"
      end

      return cleaned
    end

    def format_authors(authors_raw)
      if authors_raw.nil? || authors_raw.empty?
        raise ArgumentError, "No authors found in BibTeX entry"
      end

      my_name = 'A Orthey'

      # Convert each author to "Initials Lastname" format
      author_list = authors_raw.map do |author|
        prenames = clean_latex(author.first&.to_s) || ''
        lastname = clean_latex(author.last&.to_s) || ''

        initials = prenames.scan(/\b\w/).join('')
        formatted_name = "#{initials} #{lastname}".strip
        # Bold your name if it matches
        formatted_name == my_name ? "**#{formatted_name}**" : formatted_name
      end

      # Apply the "et al" rule for > 10 authors
      if author_list.size > 10
        # Ensure your name is bold in "et al" case if it's the first author
        first_author = author_list.first
        "#{first_author} et al"
      else
        author_list.join(', ')
      end
    end

    def get_venue_type(entry)
      return case entry.type
             when :article
               'Journal'
             when :inproceedings, :conference
               'Conference'
             when :misc
               'Workshop'
             when :masterthesis, :phdthesis
               'These'
             else
               'Other'
             end
    end

    def format_bibtex(entry)
      lines = ["@#{entry.type}{#{entry.key},"]
      entry.fields.each do |key, value|
        lines << "\t#{key} = {#{value}}," # Indent with one tab
      end
      lines << "}"
      lines.join("\n").strip
    end

    def generate(site)
      bibtex_dir = File.join(site.source, 'bibtex')
      papers_dir = File.join(site.source, 'papers')
      publications = []

      # Iterate over BibTeX files
      Dir.glob(File.join(bibtex_dir, '*.bib')).each do |bib_file|
        filename = File.basename(bib_file, '.bib')
        pdf_path = File.join(papers_dir, "#{filename}.pdf")

        if not File.exist?(pdf_path)
          raise ArgumentError, "Requires pdf file #{filename}.pdf, but found none."
        end

        begin
          bib = BibTeX.open(bib_file)
          entry = bib.entries.first[1]

          authors = format_authors(entry.author)
          title = entry.title&.to_s || 'Untitled'
          venue = entry.journal&.to_s || entry.booktitle&.to_s || entry.publisher&.to_s || entry.school&.to_s || entry.howpublished&.to_s || 'Unknown Venue'
          year = entry.year&.to_s || 'Unknown Year'

          bibtex_formatted = format_bibtex(entry)

          publication = {
            'authors' => authors,
            'title' => title,
            'venue' => venue,
            'year' => year,
            'type' => get_venue_type(entry),
            'bibtex' => bibtex_formatted,
            'pdf' => "/papers/#{filename}.pdf"
          }
          youtube = entry[:youtube]&.to_s # Extract youtube field if it exists
          publication['youtube'] = youtube if youtube # Add youtube only if it exists
          website = entry[:web]&.to_s # Extract web field if it exists
          publication['website'] = website if website # Add youtube only if it exists

          publications << publication
          Jekyll.logger.debug "Parsed entry: #{publication}"

        rescue StandardError => e
          Jekyll.logger.warn "Error parsing BibTeX file #{filename}.bib: #{e.message}"
          raise ArgumentError, "Error parsing BibTeX file #{filename}.bib: #{e.message}"
          next
        end
      end

      # Sort by year (descending), handle non-numeric years gracefully
      publications.sort_by! { |p| p['year'].to_i }.reverse!

      # Store in site.data for use in templates
      site.data['publications'] = publications
    end
  end
end
