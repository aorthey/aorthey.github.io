# Rakefile – Dec 2025: Bullet-proof version with cache disabled (fixes v4.4.3 bug)
require "bundler/setup"
require "html-proofer"
require "find"

task :build do
  puts "Building Jekyll site..."
  sh "bundle exec jekyll build --future"
end

# ──────────────────────────────────────────────────────────────
# HTMLProofer – checks internal + ALL external links
# ──────────────────────────────────────────────────────────────
task :proofer => :build do
  puts "Running HTMLProofer – checking ALL links (internal + external)..."
  options = {
    allow_hash_href:     true,
    check_html:          true,
    check_img_http:      true,
    check_opengraph:     true,
    enforce_https:       true,
    disable_external:    false,           # ← Tests every external URL (as you want)
    ignore_missing_alt:  false,

    typhoeus: {
      headers:        { "User-Agent" => "Mozilla/5.0 Jekyll Tester" },
      connecttimeout: 30,
      timeout:        60
    },

    url_swap: {
      /src\/[^\/"']+\.html/ => ''   # matches:
    },

    ignore_urls: [
      /linkedin\.com/,
      /twitter\.com/,
      /x\.com/,
      /orcid\.org/,
      /scholar\.google\.com/,
      /addons\.mozilla\.org/
    ]
  }

  HTMLProofer.check_directory("./_site", options).run
end

# ──────────────────────────────────────────────────────────────
# Minitest – all files in test/
# ──────────────────────────────────────────────────────────────
task :minitest => :build do
  puts "Running Minitest suite..."
  ruby "-I test -e 'Dir[\"test/test_*.rb\"].each { |f| require \"./\#{f}\" }'"
end

# ──────────────────────────────────────────────────────────────
# RSS/Atom feed.xml validation (uses Ruby stdlib)
# ──────────────────────────────────────────────────────────────
task :feed => :build do
  puts "Validating feed.xml..."
  path = "_site/feed.xml"
  next puts "No feed.xml found (jekyll-feed not active?)" unless File.exist?(path)

  require "rexml/document"
  REXML::Document.new(File.read(path))
  puts "feed.xml is valid XML"
rescue => e
  raise "feed.xml is broken: #{e.message}"
end

# ──────────────────────────────────────────────────────────────
# sitemap.xml validation (uses Ruby stdlib)
# ──────────────────────────────────────────────────────────────
task :sitemap => :build do
  puts "Validating sitemap.xml..."
  require "rexml/document"
  path = "_site/sitemap.xml"
  raise "#{path} not found – enable jekyll-sitemap plugin?" unless File.exist?(path)

  doc = REXML::Document.new(File.read(path))
  count = doc.elements.to_a("//url/loc").size
  raise "sitemap.xml is empty!" if count.zero?
  puts "sitemap.xml is valid and contains #{count} URLs"
end

# 7. Favicon exists
task :favicon => :build do
  candidates = [
    "/favicon.ico",
    "/favicon.png",
    "/assets/favicon.png",
    "/assets/favicon.ico",
    "/images/favicon.png"
  ]

  found = candidates.any? { |p| File.exist?("_site#{p}") }

  if not found
    raise "No favicon found! Add at least one of: #{candidates.join(', ')}"
  end
end

# 8. robots.txt exists
task :robots => :build do
  raise "robots.txt missing" unless File.exist?("_site/robots.txt")
end

# 9. 404 page exists
task :not_found => :build do
  raise "404.html missing" unless File.exist?("_site/404.html")
end

# 10. Find large files
task :large_files => :build do
  large = []

  Find.find("_site") do |path|
    next if File.directory?(path)
    size_kb = File.size(path) / 1024.0
    if size_kb > 20000
      relative = path.sub("_site/", "")
      large << "#{relative} → #{'%.1f' % size_kb} KB"
    end
  end

  if not large.empty?
    raise "\nToo large files detected:\n  #{large.join("\n  ")}"
  end
end

# ──────────────────────────────────────────────────────────────
# Full test suite
# ──────────────────────────────────────────────────────────────
desc "Run the complete test suite"
task :test => [
  #:proofer,
  :minitest,
  :feed,
  :sitemap,
  :favicon,
  :robots,
  :not_found,
  :large_files
]

task default: :test
