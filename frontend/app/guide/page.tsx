'use client'

import { BookOpen, Search, Globe, Users, Mail, Settings, Zap, AtSign, Activity, CheckCircle2, AlertCircle, Info } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function GuidePage() {
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (!token) {
      router.push('/login')
      return
    }
  }, [router])

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg shadow-sm border-b border-gray-200/50 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-black flex items-center">
                <BookOpen className="w-5 h-5 mr-2" />
                User Guide
              </h1>
              <p className="text-gray-600 mt-0.5 text-xs">
                Complete guide on how to use the Art Outreach Scraper
              </p>
            </div>
            <button
              onClick={() => router.push('/')}
              className="px-3 py-1.5 bg-olive-600 hover:bg-olive-700 text-white rounded-md transition-colors text-sm"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="space-y-6">
          {/* Introduction */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <Info className="w-5 h-5 mr-2 text-olive-600" />
              Introduction
            </h2>
            <p className="text-sm text-gray-700 leading-relaxed">
              The Art Outreach Scraper is an automated system that discovers websites and social media profiles,
              extracts contact information (emails, phone numbers, social links), and helps you build a database
              of potential outreach targets. The system runs automatically every 15 minutes, but you can also trigger
              manual searches anytime.
            </p>
          </section>

          {/* Getting Started */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <Zap className="w-5 h-5 mr-2 text-olive-600" />
              Getting Started
            </h2>
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <strong>1. Login:</strong> Use your credentials to access the dashboard. If you don't have credentials,
                  contact your administrator.
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <strong>2. Check Automation Status:</strong> Look at the System Status bar at the top to see if
                  automation is running. It shows "Automation Active" when enabled.
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <strong>3. View Statistics:</strong> The Overview tab shows your key metrics: leads collected,
                  emails extracted, websites scraped, and outreach sent.
                </div>
              </div>
            </div>
          </section>

          {/* Website Discovery */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <Search className="w-5 h-5 mr-2 text-olive-600" />
              Website Discovery & Search
            </h2>
            <div className="space-y-3 text-sm text-gray-700">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Automatic Search</h3>
                <p className="mb-2">
                  The system automatically searches for websites every <strong>15 minutes</strong>. It discovers:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Websites in selected locations (USA, Canada, Europe, etc.)</li>
                  <li>Social media profiles (Instagram, TikTok)</li>
                  <li>Small websites with ~100k organic visitors</li>
                  <li>Sites with good domain authority and page ranking</li>
                </ul>
              </div>
              
              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2">Manual Search</h3>
                <p className="mb-2">
                  You can trigger a manual search anytime, even when automation is ON:
                </p>
                <ol className="list-decimal list-inside space-y-1 ml-2">
                  <li>Go to the <strong>Overview</strong> tab</li>
                  <li>Find the <strong>"Website Discovery"</strong> section</li>
                  <li>Select a <strong>Location</strong> (optional - leave empty for all locations)</li>
                  <li>Select <strong>Categories</strong> (optional - leave empty for all categories)</li>
                  <li>Click <strong>"Search Now (Manual)"</strong> button</li>
                </ol>
                <div className="mt-2 p-2 bg-olive-50 border border-olive-200 rounded-md">
                  <p className="text-xs text-olive-800">
                    <strong>Note:</strong> Manual searches work independently of the 15-minute automatic schedule.
                    You can run multiple manual searches in between automatic runs.
                  </p>
                </div>
              </div>

              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2">Location-Based Search</h3>
                <p className="mb-2">Available locations:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong>United States</strong> - USA-based websites and social profiles</li>
                  <li><strong>Canada</strong> - Canadian websites and social profiles</li>
                  <li><strong>London, UK</strong> - UK-based websites and social profiles</li>
                  <li><strong>Germany</strong> - German websites and social profiles</li>
                  <li><strong>France</strong> - French websites and social profiles</li>
                  <li><strong>Europe (General)</strong> - All European countries</li>
                </ul>
              </div>

              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2">Search Categories</h3>
                <p className="mb-2">The system searches for websites in these categories:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><strong>Home Decor</strong> - Interior design, home decoration blogs</li>
                  <li><strong>Holiday</strong> - Holiday planning, seasonal content</li>
                  <li><strong>Parenting</strong> - Parenting blogs, family lifestyle</li>
                  <li><strong>Audio Visuals</strong> - Home theater, audio equipment reviews</li>
                  <li><strong>Gift Guides</strong> - Gift recommendation websites</li>
                  <li><strong>Tech Innovation</strong> - Technology blogs, innovation news</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Viewing Data */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <Globe className="w-5 h-5 mr-2 text-olive-600" />
              Viewing Your Data
            </h2>
            <div className="space-y-3 text-sm text-gray-700">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <Globe className="w-4 h-4 mr-1" />
                  Websites Tab
                </h3>
                <p className="mb-2">
                  View all discovered and scraped websites. You can:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Toggle between <strong>"Discovered"</strong> and <strong>"Scraped"</strong> views</li>
                  <li>Filter by category, source, and scraped status</li>
                  <li>See website quality metrics (domain authority, traffic, etc.)</li>
                  <li>Extract contacts for specific websites</li>
                </ul>
              </div>

              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <Users className="w-4 h-4 mr-1" />
                  Leads Tab
                </h3>
                <p className="mb-2">
                  View all collected leads with contact information:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Filter by category</li>
                  <li>See contact names, emails, phone numbers</li>
                  <li>View associated websites and social media links</li>
                  <li>Export data for outreach campaigns</li>
                </ul>
              </div>

              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <AtSign className="w-4 h-4 mr-1" />
                  Scraped Emails Tab
                </h3>
                <p className="mb-2">
                  Dedicated view for all extracted email addresses:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>See all emails found during scraping</li>
                  <li>View contact names and associated websites</li>
                  <li>Filter and search through your email database</li>
                  <li>See when emails were extracted</li>
                </ul>
              </div>

              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <Mail className="w-4 h-4 mr-1" />
                  Outreach Emails Tab
                </h3>
                <p className="mb-2">
                  Track your email outreach campaigns:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>View sent emails and their status</li>
                  <li>See pending emails waiting to be sent</li>
                  <li>Track email delivery and responses</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Email Extraction */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <AtSign className="w-5 h-5 mr-2 text-olive-600" />
              Email Extraction
            </h2>
            <div className="space-y-3 text-sm text-gray-700">
              <p>
                The system uses multiple techniques to find emails:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li><strong>HTML Parsing</strong> - Extracts emails from page content</li>
                <li><strong>Footer/Header Extraction</strong> - Finds contact info in common locations</li>
                <li><strong>Contact Page Crawling</strong> - Checks 50+ common contact page paths</li>
                <li><strong>Form Extraction</strong> - Finds emails in contact forms</li>
                <li><strong>JavaScript Rendering</strong> - Uses Playwright for JS-heavy sites</li>
                <li><strong>Hunter.io API</strong> - Finds emails not visible on the website (if configured)</li>
              </ul>
              <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-xs text-blue-800">
                  <strong>Tip:</strong> The system automatically extracts contacts after scraping each website.
                  No manual action needed!
                </p>
              </div>
            </div>
          </section>

          {/* Manual Scraping */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <Search className="w-5 h-5 mr-2 text-olive-600" />
              Manual URL Scraping
            </h2>
            <div className="space-y-3 text-sm text-gray-700">
              <p>
                You can manually scrape a specific URL:
              </p>
              <ol className="list-decimal list-inside space-y-1 ml-2">
                <li>Go to the <strong>Overview</strong> tab</li>
                <li>Find the <strong>"Scrape Website"</strong> section</li>
                <li>Enter a URL (e.g., <code className="bg-gray-100 px-1 rounded">https://example.com</code>)</li>
                <li>Click <strong>"Scrape"</strong></li>
                <li>The system will scrape the website and extract contacts automatically</li>
              </ol>
            </div>
          </section>

          {/* Automation Settings */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <Settings className="w-5 h-5 mr-2 text-olive-600" />
              Automation Settings
            </h2>
            <div className="space-y-3 text-sm text-gray-700">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Search Interval</h3>
                <p className="mb-2">
                  The default search interval is <strong>15 minutes</strong>. The system will automatically:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Discover new websites every 15 minutes</li>
                  <li>Scrape discovered websites</li>
                  <li>Extract contacts from scraped websites</li>
                </ul>
              </div>
              
              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2">Turning Automation On/Off</h3>
                <p className="mb-2">
                  Go to the <strong>Settings</strong> tab to:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Enable or disable automation</li>
                  <li>Change search interval (minimum 10 seconds)</li>
                  <li>Configure email sending mode (automatic or manual)</li>
                </ul>
                <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
                  <p className="text-xs text-yellow-800">
                    <strong>Note:</strong> Even when automation is OFF, you can still trigger manual searches.
                    Automation only controls the automatic 15-minute schedule.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Monitoring */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <Activity className="w-5 h-5 mr-2 text-olive-600" />
              Monitoring & Activity
            </h2>
            <div className="space-y-3 text-sm text-gray-700">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">System Status Bar</h3>
                <p className="mb-2">
                  The status bar at the top shows:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Automation status (ON/OFF)</li>
                  <li>Current search activity</li>
                  <li>Time until next automatic search</li>
                  <li>Active and completed jobs</li>
                </ul>
              </div>

              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2">Activity Feed</h3>
                <p className="mb-2">
                  The Activity Feed on the Overview tab shows real-time updates:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Website discovery events</li>
                  <li>Scraping progress</li>
                  <li>Contact extraction results</li>
                  <li>Errors and warnings</li>
                </ul>
              </div>

              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2">Jobs Tab</h3>
                <p className="mb-2">
                  View detailed status of background jobs:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Website discovery jobs</li>
                  <li>Scraping jobs</li>
                  <li>Contact extraction jobs</li>
                  <li>Email generation and sending jobs</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Tips & Best Practices */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <CheckCircle2 className="w-5 h-5 mr-2 text-olive-600" />
              Tips & Best Practices
            </h2>
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Use Location Filters:</strong> When searching manually, select a specific location
                  to get more targeted results for that region.
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Category Selection:</strong> Select specific categories to focus on your niche.
                  Leave empty to search all categories.
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Monitor Activity Feed:</strong> Keep an eye on the Activity Feed to see what the
                  system is doing in real-time.
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Check Scraped Emails Tab:</strong> Regularly check the Scraped Emails tab to see
                  newly extracted email addresses.
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Manual Searches:</strong> Use manual searches when you want immediate results or
                  to test specific locations/categories.
                </div>
              </div>
            </div>
          </section>

          {/* Troubleshooting */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 text-red-600" />
              Troubleshooting
            </h2>
            <div className="space-y-3 text-sm text-gray-700">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Backend Not Connected</h3>
                <p className="mb-2">
                  If you see "Backend not connected":
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Check if the backend server is running</li>
                  <li>Verify your API URL is correct</li>
                  <li>Check your internet connection</li>
                </ul>
              </div>

              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2">No Websites Being Discovered</h3>
                <p className="mb-2">
                  If no websites are being discovered:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Check the Activity Feed for error messages</li>
                  <li>Verify automation is enabled in Settings</li>
                  <li>Try a manual search to test the system</li>
                  <li>Check the Jobs tab for failed jobs</li>
                </ul>
              </div>

              <div className="border-t pt-3 mt-3">
                <h3 className="font-semibold text-gray-900 mb-2">No Emails Extracted</h3>
                <p className="mb-2">
                  If emails aren't being extracted:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Check if websites are being scraped successfully</li>
                  <li>Some websites may not have visible contact information</li>
                  <li>Hunter.io integration can find hidden emails (if configured)</li>
                  <li>Check the Activity Feed for extraction logs</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Support */}
          <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3">Need Help?</h2>
            <p className="text-sm text-gray-700">
              If you encounter issues or have questions, check the Activity Feed and Jobs tab for detailed
              error messages. For technical support, contact your system administrator.
            </p>
          </section>
        </div>
      </main>
    </div>
  )
}

