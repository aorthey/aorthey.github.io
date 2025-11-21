require 'yaml'

module Jekyll
  class PresentationsGenerator < Generator
    safe true

    def generate(site)
      yaml_file = File.join(site.source, 'assets', 'talks', 'talks.yml')
      if File.exist?(yaml_file)
        presentations = YAML.load_file(yaml_file)
        # Store in site.data for access in templates
        site.data['talks'] ||= {}
        site.data['talks']['talks'] = presentations
      else
        Jekyll.logger.warn "PresentationsGenerator:", "Could not find assets/talks/talks.yml"
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
