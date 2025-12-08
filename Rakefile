# Rakefile – Fully fixed & tested (Dec 2025)
require "bundler/setup"
require "html-proofer"
require "find"
require "bibtex"
require "English"

task :build do
  puts "Building Jekyll site..."
  sh "bundle exec jekyll build --future"
end

# ──────────────────────────────────────────────────────────────
# HTMLProofer
# ──────────────────────────────────────────────────────────────
task :proofer => :build do
  puts "Running HTMLProofer – checking all links..."
  options = {
    allow_hash_href: true,
    check_html: true,
    check_opengraph: true,
    enforce_https: true,
    disable_external: false,
    typhoeus: {
      headers: { "User-Agent" => "Mozilla/5.0 Jekyll Tester" },
      connecttimeout: 30,
      timeout: 60
    },
    ignore_urls: [
      %r{linkedin\.com},
      %r{x\.com},
      %r{twitter\.com},
      %r{orcid\.org},
      %r{scholar\.google\.com},
      %r{addons\.mozilla\.org}
    ]
  }
  HTMLProofer.check_directory("./_site", options).run
end

task :minitest => :build do
  if Dir.exist?("test") && !Dir["test/test_*.rb"].empty?
    puts "Running Minitest suite..."
    sh "ruby -I test -e 'require \"./test/test_helper\" if File.exist?(\"test/test_helper.rb\"); Dir[\"test/test_*.rb\"].each { |f| require \"./\#{f}\" }'"
  else
    puts "No Minitest files – skipping"
  end
end

# ──────────────────────────────────────────────────────────────
# Feed validation
# ──────────────────────────────────────────────────────────────
task :feed => :build do
  path = "_site/feed.xml"
  next puts "No feed.xml – skipping" unless File.exist?(path)

  puts "Validating feed.xml..."
  require "rexml/document"
  REXML::Document.new(File.read(path))
  puts "feed.xml is valid XML"
rescue => e
  raise "feed.xml is invalid: #{e.message}"
end

# ──────────────────────────────────────────────────────────────
# Sitemap validation
# ──────────────────────────────────────────────────────────────
task :sitemap => :build do
  path = "_site/sitemap.xml"
  raise "sitemap.xml missing – enable jekyll-sitemap?" unless File.exist?(path)

  puts "Validating sitemap.xml..."
  require "rexml/document"
  doc = REXML::Document.new(File.read(path))
  count = doc.elements.to_a("//url/loc").size
  raise "sitemap.xml is empty!" if count.zero?
  puts "sitemap.xml is valid (#{count} URLs)"
end

# ──────────────────────────────────────────────────────────────
# Favicon, robots.txt, 404
# ──────────────────────────────────────────────────────────────
task :favicon => :build do
  candidates = %w[/favicon.ico /favicon.png /assets/favicon.png /assets/favicon.ico /images/favicon.png]
  found = candidates.any? { |p| File.exist?("_site#{p}") }
  raise "No favicon found! Expected one of: #{candidates.join(', ')}" unless found
  puts "Favicon found"
end

task :robots => :build do
  raise "robots.txt missing" unless File.exist?("_site/robots.txt")
end

task :not_found => :build do
  raise "404.html missing" unless File.exist?("_site/404.html")
end

# ──────────────────────────────────────────────────────────────
# Large files (>20 MB)
# ──────────────────────────────────────────────────────────────
task :large_files => :build do
  large = []
  Find.find("_site") do |path|
    next if File.directory?(path)
    size_mb = File.size(path) / 1024.0 / 1024.0
    if size_mb > 20
      large << "#{path.sub('_site/', '')} → #{'%.1f' % size_mb} MB"
    end
  end

  if large.any?
    raise "Files larger than 20 MB found:\n  #{large.join("\n  ")}"
  else
    puts "No files larger than 20 MB"
  end
end

# ──────────────────────────────────────────────────────────────
# BibTeX validation (new!)
# ──────────────────────────────────────────────────────────────
task :bibtex do
  bib_dir = "assets/bib"
  unless Dir.exist?(bib_dir)
    puts "No #{bib_dir} directory – skipping BibTeX validation"
    next
  end

  puts "Validating BibTeX files in #{bib_dir}..."
  errors = []

  REQUIRED_FIELDS = {
    article:       %w[author title journal year],
    book:          %w[author editor title publisher year],
    inproceedings: %w[author title booktitle year],
    techreport:    %w[author title institution year],
    mastersthesis: %w[author title school year],
    phdthesis:     %w[author title school year],
    misc:          %w[]
  }

  Dir["#{bib_dir}/**/*.bib"].each do |file|
    begin
      bib = BibTeX.open(file, strict: true)

      bib.each do |entry|
        required = REQUIRED_FIELDS.fetch(entry.type.to_sym, [])
        missing  = required - entry.fields.keys.map(&:to_s)
        errors << "#{file} @#{entry.type}{#{entry.key}} missing fields: #{missing.join(', ')}" if missing.any?
      end
    rescue BibTeX::ParseError => e
      errors << "#{file} → parse error: #{e.message}"
    rescue => e
      errors << "#{file} → #{e.class}: #{e.message}"
    end
  end

  if errors.any?
    raise "BibTeX validation failed:\n  #{errors.join("n  ")}"
  else
    puts "#{Dir["#{bib_dir}/**/*.bib"].size} BibTeX file(s) are valid and complete"
  end
end

# ──────────────────────────────────────────────────────────────
# Full test suite
# ──────────────────────────────────────────────────────────────
desc "Run the full test suite"
task :test => [
  # :proofer,        # uncomment when you want to test external links (slow)
  :minitest,
  :feed,
  :sitemap,
  :favicon,
  :robots,
  :not_found,
  :large_files,
  :bibtex
]

task default: :test
