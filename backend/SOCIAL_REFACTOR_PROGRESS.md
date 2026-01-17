# Social Outreach Refactor Progress

## Goal
Refactor Social Outreach to reuse `prospects` table instead of separate `social_profiles` table.

## Completed ✅
1. ✅ Migration created: `add_social_columns_to_prospects.py`
2. ✅ Prospect model updated with social fields
3. ✅ Adapter interface created
4. ✅ Platform adapters created (stubs)
5. ✅ Status endpoint refactored to use Prospect table
6. ✅ Discovery endpoint refactored to use adapters
7. ✅ Review endpoint refactored to use Prospect table

## In Progress 🔄
8. ⏳ Drafting endpoint - needs refactor
9. ⏳ Sending endpoint - needs refactor
10. ⏳ Follow-up endpoint - needs refactor

## Remaining Tasks
11. Remove all schema checks from social endpoints
12. Update social.py endpoints to use Prospect table
13. Remove social model imports
14. Update UI to filter by source_type
15. Test end-to-end

## Key Changes
- All queries now filter: `Prospect.source_type == 'social'`
- No more `SocialProfile`, `SocialDiscoveryJob`, `SocialDraft`, `SocialMessage` tables
- Reuses existing pipeline logic with source_type filtering
- Adapter pattern for platform-specific discovery

