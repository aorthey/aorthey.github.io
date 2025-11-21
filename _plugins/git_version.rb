module Jekyll
  module GitVersionFilter
    def git_commit_count(input)
      `git rev-list --count HEAD`.strip
    end

    def git_short_hash(input)
      `git rev-parse --short HEAD`.strip
    end
  end
end
Liquid::Template.register_filter(Jekyll::GitVersionFilter)
