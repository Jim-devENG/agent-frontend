/**
 * Shared TypeScript types for the frontend application
 */

/**
 * Result of email enrichment operation.
 *
 * The backend may return partial data, so we normalize everything into this shape:
 * - Core fields are always present on the object
 * - Values may be null when unknown / not provided
 */
export interface EnrichmentResult {
  email: string | null
  name: string | null
  company: string | null
  confidence: number | null
  domain: string

  /**
   * Backwards‑compatible / auxiliary fields
   */
  title?: string | null
  success?: boolean
  source?: string | null
  error?: string | null
}
