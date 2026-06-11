require 'yaml'
require 'date'

module Jekyll
  class PresentationsGenerator < Generator
    safe true

    ALLOWED_TYPES = [
      "invited talk",
      "conference talk",
      "guest lecture"
    ].freeze

    def generate(site)
      yaml_file = File.join(site.source, 'assets', 'talks', 'talks.yml')

      if File.exist?(yaml_file)
        data = YAML.load_file(yaml_file)

        # Support both wrapped structure and direct array
        presentations = data.is_a?(Hash) && data['talks'] ? data['talks'] : data

        # Validate all talks
        presentations.each_with_index do |talk, index|
          verify_talk_data(talk, index)
        end

        # Store in site.data for access in templates
        site.data['talks'] ||= {}
        site.data['talks']['talks'] = presentations
      else
        Jekyll.logger.warn "PresentationsGenerator:", "Could not find assets/talks/talks.yml"
      end
    end

    def verify_talk_data(talk, index)
      return unless talk.is_a?(Hash)

      title = talk['title']
      raise ArgumentError.new("Talk ##{index + 1} is missing or has empty 'title'") if title.nil? || title.to_s.strip.empty?

      # Type validation
      type = talk['type']
      if type.nil? || type.to_s.strip.empty?
        raise ArgumentError.new("Talk ##{index + 1} '#{title}' is missing or has empty 'type'")
      end

      cleaned_type = type.to_s.strip
      unless ALLOWED_TYPES.include?(cleaned_type)
        Jekyll.logger.error "PresentationsGenerator: Invalid 'type' (talk ##{index + 1}): #{type.inspect}"
        Jekyll.logger.error " Allowed values: #{ALLOWED_TYPES.join(', ')}"
        raise ArgumentError.new("Invalid talk type (talk ##{index + 1}): #{type.inspect}")
      end

      # Venue & Location
      %w[venue location].each do |field|
        value = talk[field]
        if value.nil? || value.to_s.strip.empty?
          raise ArgumentError.new("Talk ##{index + 1} '#{title}' is missing or has empty '#{field}'")
        end
      end

      # Date validation (supports YYYY-MM or YYYY-MM-DD)
      date_str = talk['date']
      if date_str.nil? || date_str.to_s.strip.empty?
        raise ArgumentError.new("Talk ##{index + 1} '#{title}' is missing or has empty 'date'")
      end

      date_str = date_str.to_s.strip
      begin
        if date_str.match?(/\A\d{4}-\d{2}\z/)           # YYYY-MM
          Date.strptime(date_str, '%Y-%m')
        elsif date_str.match?(/\A\d{4}-\d{2}-\d{2}\z/) # YYYY-MM-DD
          Date.strptime(date_str, '%Y-%m-%d')
        else
          raise ArgumentError.new("Invalid date format")
        end
      rescue
        raise ArgumentError.new(
          "Talk ##{index + 1} '#{title}' has invalid 'date': #{date_str.inspect} — " \
          "use YYYY-MM or YYYY-MM-DD"
        )
      end

      # Optional URL and Video
      url = talk['url']
      video = talk['video']

    end
  end

  module PresentationFilter
    # Sort presentations by date (newest first)
    def sort_presentations(presentations)
      return [] unless presentations

      presentations.sort_by do |p|
        date_str = p['date'].to_s.strip
        begin
          if date_str.length == 7 # YYYY-MM
            Date.strptime(date_str, '%Y-%m')
          else
            Date.strptime(date_str, '%Y-%m-%d')
          end
        rescue
          Date.new(1900) # fallback
        end
      end.reverse
    end

    # Format date as "Month YYYY" (e.g. "June 2026")
    def format_talk_date(talk)
      return "" unless talk && talk['date']

      date_str = talk['date'].to_s.strip
      begin
        if date_str.length == 7 # YYYY-MM
          Date.strptime(date_str, '%Y-%m').strftime('%B %Y')
        else
          Date.strptime(date_str, '%Y-%m-%d').strftime('%B %Y')
        end
      rescue
        date_str # fallback
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::PresentationFilter)
