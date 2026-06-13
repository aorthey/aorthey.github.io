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
                .gsub(/{\"O}/, 'Ö')
                .gsub(/{"O}/, 'Ö')
                .gsub(/"O/, 'Ö')
                .gsub(/{\"a}/, 'ä')
                .gsub(/{"a}/, 'ä')
                .gsub(/"a/, 'ä')
                .gsub(/{\"A}/, 'Ä')
                .gsub(/{"A}/, 'Ä')
                .gsub(/"A/, 'Ä')
                .gsub(/{\"u}/, 'ü')
                .gsub(/{"u}/, 'ü')
                .gsub(/"u/, 'ü')
                .gsub(/{\"U}/, 'Ü')
                .gsub(/{"U}/, 'Ü')
                .gsub(/"U/, 'Ü')
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

    def check_bibtex_structure(bib)
      return false unless bib.is_a?(BibTeX::Bibliography)

      valid = true
      seen_keys = Set.new
      required_fields = {
        'article' => %w[author title journal year],
        'book' => %w[author title publisher year],
        'inproceedings' => %w[author title booktitle year],
        'conference' => %w[author title booktitle year],
        'techreport' => %w[author title institution year],
        'unpublished' => %w[author title note],
        'misc' => %w[author title],
        'online' => %w[author title year url]
      }

      bib.entries.each do |key, entry|
        # Check for duplicate keys
        if seen_keys.include?(key)
          puts "Error: Duplicate key '#{key}' found in .bib file"
          valid = false
        else
          seen_keys.add(key)
        end

        # Check for valid key format (no spaces, valid characters)
        unless key.match?(/^[a-zA-Z0-9:_-]+$/)
          puts "Warning: Key '#{key}' contains invalid characters or spaces"
          valid = false
        end

        # Check required fields based on entry type
        entry_type = entry.type.to_s.downcase
        fields_to_check = required_fields[entry_type] || %w[title]

        fields_to_check.each do |field|
          unless entry[field] && !entry[field].to_s.strip.empty?
            puts "Error: Entry '#{key}' (#{entry_type}) missing or empty field: #{field}"
            valid = false
          end
        end

        # Check author field format (should use 'and' for multiple authors)
        if entry[:author] && entry[:author].include?(',')
          unless entry[:author].match?(/\band\b/)
            puts "Warning: Entry '#{key}' has incorrect author format (use 'and' instead of commas)"
          end
        end

        # Check pages format for article/inproceedings
        if %w[article inproceedings].include?(entry_type) && entry[:pages]
          unless entry[:pages].match?(/\d+\s*--\s*\d+/)
            puts "Warning: Entry '#{key}' has invalid pages format (expected '1--10')"
          end
        end
      end

      valid
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

    def format_venue(entry)
      entry_type = entry.type.to_s.downcase.to_sym

      case entry_type
      when :article, :incollection
        entry[:journal]&.to_s || 'Journal'

      when :inproceedings, :conference
        if entry[:series] && !entry[:series].to_s.strip.empty?
          entry[:booktitle]&.to_s || 'Workshop'
        else
          entry[:booktitle]&.to_s || 'Conference'
        end

      when :misc
        # Workshops using @misc
        entry[:howpublished]&.to_s || entry[:booktitle]&.to_s || 'Workshop'

      when :online
        # arXiv and other online-first / preprint entries
        if entry[:eprint] || entry[:archiveprefix]&.to_s.downcase.include?('arxiv')
          eprint = entry[:eprint]&.to_s
          "arXiv preprint#{eprint ? " #{eprint}" : ''}"
        else
          entry[:url]&.to_s || entry[:howpublished]&.to_s || 'Online'
        end

      when :masterthesis, :phdthesis
        entry[:school]&.to_s || 'Thesis'

      else
        entry[:booktitle]&.to_s || entry[:journal]&.to_s || entry[:howpublished]&.to_s || 'Other'
      end
    end

    def get_venue_type(entry)
      return case entry.type
             when :article, :incollection
               'Journal'
             when :inproceedings, :conference
               'Conference'
             when :misc
               'Workshop'
             when :masterthesis, :phdthesis
               'Thesis'
             when :online
               'Preprint'
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
      bibtex_dir = File.join(site.source, 'assets/bib')
      papers_dir = File.join(site.source, 'assets/pdf')
      publications = []
      all_bibtex_entries = [] # Array to store all BibTeX entries

      # Iterate over BibTeX files
      Dir.glob(File.join(bibtex_dir, '*.bib')).each do |bib_file|
        filename = File.basename(bib_file, '.bib')
        pdf_path = File.join(papers_dir, "#{filename}.pdf")

        if not File.exist?(pdf_path)
          raise ArgumentError, "Requires pdf file #{filename}.pdf, but found none."
        end

        begin
          bib = BibTeX.open(bib_file)
          if not check_bibtex_structure(bib)
            raise ArgumentError, "Found an error or warning in bibtex file #{bib_file}. Please see messages above."
          end
          entry = bib.entries.first[1]

          authors = format_authors(entry.author)
          title = entry.title&.to_s || 'Untitled'
          venue = format_venue(entry)
          #venue = entry.journal&.to_s || entry.booktitle&.to_s || entry.publisher&.to_s || entry.school&.to_s || entry.howpublished&.to_s || entry.archivePrefix&.to_s || 'Unknown Venue'
          year = entry.year&.to_s || 'Unknown Year'

          bibtex_formatted = format_bibtex(entry)
          all_bibtex_entries << bibtex_formatted # Collect BibTeX entry


          publication = {
            'authors' => authors,
            'title' => title,
            'venue' => venue,
            'year' => year,
            'type' => get_venue_type(entry),
            'bibtex' => bibtex_formatted,
            'pdf' => "/assets/pdf/#{filename}.pdf"
          }
          youtube = entry[:youtube]&.to_s # Extract youtube field if it exists
          publication['youtube'] = youtube if youtube # Add youtube only if it exists
          website = entry[:web]&.to_s # Extract web field if it exists
          publication['website'] = website if website # Add youtube only if it exists
          code = entry[:code]&.to_s
          publication['code'] = code if code
          arxiv = entry[:arxiv]&.to_s
          publication['arxiv'] = arxiv if arxiv

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
      all_bibtex_entries.sort_by! { |p| p['year'].to_i }.reverse!

      # Store in site.data for use in templates
      site.data['publications'] = publications

      ################################################################################
      # Generate single .bib file
      ################################################################################
      output_dir = File.join(site.source, 'assets', 'generate')
      FileUtils.mkdir_p(output_dir) # Create directory if it doesn't exist
      filename = 'all_publications.txt'
      output_file = File.join(output_dir, filename)

      File.write(output_file, all_bibtex_entries.join("\n\n")) # Separate entries with blank lines
      Jekyll.logger.info "Generated #{output_file} with #{all_bibtex_entries.length} entries."

      # Ensure the file is kept in the site output
      unless site.static_files.any? { |sf| sf.relative_path == '/assets/generate/'+filename }
        site.static_files << Jekyll::StaticFile.new(site, site.source, 'assets/generate', filename)
      end

    end
  end
end
