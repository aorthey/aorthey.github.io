require 'yaml'

module Jekyll
  class StudentsGenerator < Generator
    safe true

    def generate(site)
      yaml_file = File.join(site.source, 'assets', 'students', 'students.yml')
      if File.exist?(yaml_file)
        students = YAML.load_file(yaml_file)
        site.data['students'] ||= {}
        site.data['students']['students'] = students['students']
      else
        Jekyll.logger.warn "StudentsGenerator:", "Could not find students.yml"
      end
    end
  end

  module StudentFilter
    def sort_students(students)
      return [] unless students
      students.sort_by do |s|
        [-s['year'].to_i]
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::StudentFilter)
