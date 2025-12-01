/**
 * Shared TypeScript types for the frontend application
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

