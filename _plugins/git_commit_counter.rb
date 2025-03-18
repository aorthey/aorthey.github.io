module Jekyll
  class GitCommitCountGenerator < Generator
    safe true

    def generate(site)
      require 'net/http'
      require 'json'

      repo = "aorthey/aorthey.github.io"
      uri = URI("https://api.github.com/repos/#{repo}/commits")

      # Set up HTTP request with headers
      http = Net::HTTP.new(uri.host, uri.port)
      http.use_ssl = true
      request = Net::HTTP::Get.new(uri.request_uri)
      request['Accept'] = 'application/vnd.github.v3+json'
      request['User-Agent'] = 'Jekyll-Git-Commit-Count-Generator'

      # Make the request and parse response
      response = http.request(request)

      if response.code == "200"
        commits = JSON.parse(response.body)
        site.data['commit_count'] = commits.length
        site.data['last_commit_date'] = commits.first['commit']['committer']['date'].split('T').first
        puts "Commit count: #{site.data['commit_count']}, last commit date: #{site.data['last_commit_date']}"
      else
        puts "Failed to fetch commits: #{response.code} - #{response.message}"
        site.data['commit_count'] = 0
        site.data['last_commit_date'] = "N/A"
      end
    rescue StandardError => e
      puts "Error fetching Git commits: #{e.message}"
      site.data['commit_count'] = 'X'
      site.data['last_commit_date'] = "N/A"
    end
  end
end
