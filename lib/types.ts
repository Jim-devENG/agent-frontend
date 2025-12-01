/**
 * Shared TypeScript types for the frontend application
 */

/**
 * Result of email enrichment operation
 * All properties are optional to handle partial data from various enrichment sources
 */
export interface EnrichmentResult {
  email?: string
  name?: string
  company?: string
  title?: string
  success?: boolean
  confidence?: number
  source?: string
  domain?: string
  error?: string
}

