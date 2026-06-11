require 'pdf-reader'
require 'date'

module Jekyll
  class PdfMetadataGenerator < Generator
    safe true
    priority :high

    def generate(site)
      pdf_documents = []

      # Iterate over all PDF files in /assets/documents/
      Dir.glob(File.join(site.source, 'assets/documents', '*.pdf')).each do |file|
        begin
          filename = File.basename(file, '.pdf')
          reader = PDF::Reader.new(file)
          info = reader.info

          # Get the raw date string from metadata
          raw_date = info[:Date]&.to_s || File.mtime(file).strftime('%Y-%m-%d')

          # Attempt to parse the date for sorting
          sorting_date = begin
            DateTime.parse(raw_date).to_time.utc
          rescue
            File.mtime(file)
          end

          # Extract metadata, providing defaults if not present
          metadata = {
            'filename' => "/assets/documents/#{filename}.pdf",
            'author' => info[:Author] || 'Unknown',
            'title' => info[:Title] || File.basename(file, '.pdf'),
            'description' => info[:Subject] || '',
            'date' => raw_date,
            'sorting_date' => sorting_date.strftime('%Y-%m-%d %H:%M:%S UTC')
          }

          pdf_documents << metadata
        rescue => e
          Jekyll.logger.warn "PDF Metadata: Error processing #{file}: #{e.message}"
        end
      end

      # Sort entries by sorting_date in reverse order (latest first)
      pdf_documents.sort_by! { |note| DateTime.parse(note['sorting_date']) }.reverse!

      # Store the metadata in site.data['pdf-documents']
      site.data['pdf-documents'] = pdf_documents
    end
  end
end
