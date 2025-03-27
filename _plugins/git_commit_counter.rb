module Jekyll
  class GitCommitCountGenerator < Generator
    safe true

    def generate(site)
      default_commit_count = 42
      current_date = Time.now.strftime("%Y-%m-%d")

      begin
        # Attempt to get commit count by shell command (works if running locally with git)
        if Dir.exist?('.git')
          commit_count = `git rev-list --all --count`.strip.to_i
          last_commit_date = `git log -1 --format=%cd --date=short`.strip

          if commit_count > 0 && !last_commit_date.empty?
            site.data['commit_count'] = commit_count
            site.data['last_commit_date'] = last_commit_date
          else
            # Fallback 1: Use hardcoded count and current date
            site.data['commit_count'] = default_commit_count
            site.data['last_commit_date'] = current_date
          end
        else
          # Fallback 2: If no git repo available, use hardcoded count and current date
          site.data['commit_count'] = default_commit_count
          site.data['last_commit_date'] = current_date
        end

        puts "Commit count: #{site.data['commit_count']}, last commit date: #{site.data['last_commit_date']}"
      rescue StandardError => e
        puts "Error processing Git commits: #{e.message}"
        # Fallback 3: Final fallback for any errors
        site.data['commit_count'] = 'X'  # Indicates unknown count
        site.data['last_commit_date'] = 'N/A'
      end
    end
  end
end
