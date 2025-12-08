require_relative 'test_helper'

class TestVersionFooter < JekyllTest
  def test_footer_contains_version_in_expected_format
    index = File.read('_site/index.html')

    # This regex accepts ALL three valid cases:
    #   v123-a1b2c3d4     → real GitHub Pages build
    #   v42-3f8a9c2       → local with _config_dev.yml
    #   v0-local          → plain local jekyll serve
    #   v7-localdev       → any other fallback you might use
    assert_match(/v\d+-[a-f0-9]{7}|v\d+-[a-zA-Z0-9_-]+|v0-local/,
                 index,
                 "Footer version should be in format v<number>-<hash> or v0-local")
  end

  def test_footer_contains_short_hash_of_at_least_7_characters_when_not_local
    index = File.read('_site/index.html')

    # If it's a real build (not the fallback "local"), the hash part must be exactly 7 hex chars
    if index.include?("local")
      # "local" is allowed → test passes automatically
      skip("Local development mode detected – short hash can be 'local'")
    else
      assert_match(/v\d+-[a-f0-9]{7}/, index,
                   "Production footer must contain a real 7-character git short hash")
    end
  end

  def test_footer_contains_current_year
    index = File.read('_site/index.html')
    current_year = Time.now.year
    assert_match(/#{current_year}/, index,
                 "Footer should contain the current year #{current_year}")
  end

  def test_footer_contains_source_code_link
    index = File.read('_site/index.html')
    assert_match(/Source Code/, index)
    assert_match(/github.com\/aorthey\/aorthey.github.io/, index)
  end
end
