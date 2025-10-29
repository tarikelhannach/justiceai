-- Migration: Add OCR fields to documents table
-- Date: 2025-10-14
-- Description: Add fields for OCR processing metadata

-- Add OCR-related columns to documents table
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS ocr_confidence INTEGER,
ADD COLUMN IF NOT EXISTS ocr_language VARCHAR(10),
ADD COLUMN IF NOT EXISTS is_searchable BOOLEAN DEFAULT FALSE;

-- Create index for searchable documents
CREATE INDEX IF NOT EXISTS idx_documents_searchable ON documents(is_searchable) WHERE is_searchable = TRUE;

-- Create index for OCR language for filtering
CREATE INDEX IF NOT EXISTS idx_documents_ocr_language ON documents(ocr_language) WHERE ocr_language IS NOT NULL;

-- Update existing documents with default values
UPDATE documents 
SET is_searchable = FALSE 
WHERE is_searchable IS NULL;

-- Add comment
COMMENT ON COLUMN documents.ocr_confidence IS 'OCR confidence score (0-100) for extracted text quality';
COMMENT ON COLUMN documents.ocr_language IS 'Detected language code (ar, fr, es, en) from OCR processing';
COMMENT ON COLUMN documents.is_searchable IS 'Whether document text has been extracted and is searchable';
