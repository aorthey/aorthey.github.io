module Jekyll
  class GitCommitCountGenerator < Generator
    safe true

    def generate(site)
      commit_count = `git rev-list --all --count`.strip
      site.data['commit_count'] = commit_count
      last_commit_date = `git log -1 --format=%cd --date=short`.strip
      site.data['last_commit_date'] = last_commit_date
      puts "Commit count #{commit_count}, date #{last_commit_date}"
    end
  end
end
