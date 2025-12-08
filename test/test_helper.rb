require 'minitest/autorun'
require 'jekyll'

Jekyll.logger.log_level = :error

class JekyllTest < Minitest::Test
  def site
    @site ||= begin
      config = Jekyll.configuration({
        'source'      => File.expand_path('../', __FILE__),
        'destination' => File.expand_path('../_site', __FILE__),
        'skip_config_files' => true,
      })
      Jekyll::Site.new(config)
    end
  end

  def setup
    site.process
  end
end

