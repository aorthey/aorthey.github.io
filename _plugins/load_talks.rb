require 'yaml'

ALLOWED_TYPES = %w[conference visit online].freeze

module Jekyll
  class PresentationsGenerator < Generator
    safe true

    ALLOWED_TYPES = [
      "invited talk",
      "conference talk",
      "guest lecture",
    ].freeze

    def generate(site)
      yaml_file = File.join(site.source, 'assets', 'talks', 'talks.yml')
      if File.exist?(yaml_file)
        presentations = YAML.load_file(yaml_file)
        # Validate all talks
        presentations.each_with_index do |talk, index|
          verify_talk_type(talk, index)
        end
        # Store in site.data for access in templates
        site.data['talks'] ||= {}
        site.data['talks']['talks'] = presentations
      else
        Jekyll.logger.warn "PresentationsGenerator:", "Could not find assets/talks/talks.yml"
      end
    end

    def verify_talk_type(talk, index)
      return unless talk.is_a?(Hash)

      ################################################################################ 
      # Verify name
      ################################################################################ 
      name = talk['name']
      if name.nil? || name.to_s.strip.empty?
        raise ArgumentError.new(
          "Talk ##{index + 1} is missing or has empty 'name'"
        )
      end

      ################################################################################ 
      # Verify type
      ################################################################################ 
      type = talk['type']
      if type.nil? || type.to_s.strip.empty?
        raise ArgumentError.new(
          "Talk ##{index + 1} '#{name}' is missing or has empty 'type'"
        )
      end

      cleaned_type = type.to_s.strip
      unless ALLOWED_TYPES.include?(cleaned_type)
        Jekyll.logger.error(
          "PresentationsGenerator:",
          "Invalid 'type' (talk ##{index + 1}): #{type.inspect}"
        )
        Jekyll.logger.error "  Allowed values:"
        ALLOWED_TYPES.each do |allowed|
          Jekyll.logger.error "    - #{allowed}"
        end
        raise ArgumentError.new(
          "Invalid talk type (talk ##{index + 1}): #{type.inspect}"
        )
      end
      ################################################################################ 
      # Verify location
      ################################################################################ 
      location = talk['location']
      if location.nil? || location.to_s.strip.empty?
        raise ArgumentError.new(
          "Talk ##{index + 1} '#{name}' is missing or has empty 'location'"
        )
      end
      ################################################################################ 
      # Verify year
      ################################################################################ 
      year = talk['year']
      if year.nil? || year.to_s.strip.empty?
        raise ArgumentError.new(
          "Talk ##{index + 1} '#{name}' is missing or has empty 'year'"
        )
      end
      year_str = year.to_s.strip
      unless year_str.match?(/\A\d{4}\z/)   # exactly 4 digits, nothing else
        raise ArgumentError.new(
          "Talk ##{index + 1} '#{name}' has invalid 'year': #{year.inspect} — must be a 4-digit number"
        )
      end

      year = year_str.to_i
      unless year.between?(2000, 2100)
        raise ArgumentError.new(
          "Talk ##{index + 1} '#{name}' has unrealistic year: #{year} — expected 2000--2100"
        )
      end
      ################################################################################ 
      # Verify month
      ################################################################################ 
      month = talk['month']
      if month.nil? || month.to_s.strip.empty?
        raise ArgumentError.new(
          "Talk ##{index + 1} '#{name}' is missing or has empty 'month'"
        )
      end

      month_clean = month.to_s.strip
      valid_months = %w[
        January February March April May June
        July August September October November December
      ]

      unless valid_months.include?(month_clean)
        raise ArgumentError.new(
          "Talk ##{index + 1} '#{name}' has invalid 'month': #{month.inspect}\n" \
          "  Allowed: #{valid_months.join(', ')}"
        )
      end

    end
  end

  module PresentationFilter
    def sort_presentations(presentations)
      return [] unless presentations
      presentations.sort_by do |p|
        [-p['year'].to_i, -Date::MONTHNAMES.index(p['month'] || 'January')]
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::PresentationFilter)
