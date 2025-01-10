import { z } from 'zod';

const allowedSearchResultFilters = [
	'discussions',
	'faq',
	'infobox',
	'news',
	'query',
	'summarizer',
	'videos',
	'web',
	'locations',
];

export const searchParamsSchema = z.object({
	query: z
		.string({
			message: 'Query must be a string.',
		})
		.nonempty({ message: 'Query must not be a empty string.' })
		.max(400, { message: 'Query must not exceed 400 characters.' })
		.refine((value) => value.trim().split(/\s+/).length <= 50, {
			message: 'Query must not exceed 50 words.',
		}),
	country: z
		.string({ message: 'Country must be a string.' })
		.nonempty({ message: 'Country must not be a empty string.' })
		.max(2, { message: 'Country must not exceed 2 characters.' })
		.default('US')
		.transform((value) => value.toUpperCase())
		.optional(),
	search_lang: z
		.string({ message: 'Country must be a string.' })
		.nonempty({ message: 'Country must not be a empty string.' })
		.min(2, { message: 'Country must exceed 2 characters.' })
		.default('en')
		.transform((value) => value.toLowerCase())
		.optional(),
	ui_lang: z
		.string({ message: 'Country must be a string.' })
		.nonempty({ message: 'Country must not be a empty string.' })
		.min(5, {
			message: 'Country must exceed 5 characters.',
		})
		.regex(/^[a-zA-Z]+-[a-zA-Z]+$/, {
			message: 'Country must have the correct format. (e.g., en-US).',
		})
		.default('en-US')
		.optional(),
	count: z
		.number({ message: 'Count must be a float or int.' })
		.max(20, {
			message: 'Count must not exceed 20 characters.',
		})
		.default(20)
		.optional(),
	offset: z
		.number({ message: 'Offset must be a float or int.' })
		.max(20, {
			message: 'Offset must not exceed 20 characters.',
		})
		.default(0)
		.optional(),
	safesearch: z
		.enum(['off', 'moderate', 'strict'], {
			message: 'Safesearch must be either "off", "moderate" or "strict".',
		})
		.default('moderate')
		.optional(),
	freshness: z
		.union(
			[
				z.enum(['past-day', 'past-week', 'past-month', 'past-year'], {
					message:
						'Freshness must be either "past-day", "past-week", "past-month" or "past-year"',
				}),
				z.string().regex(/^\d{4}-\d{2}-\d{2}to\d{4}-\d{2}-\d{2}$/, {
					message: 'Freshness must be in the format YYYY-MM-DDtoYYYY-MM-DD.',
				}),
			],
			{
				message:
					'Freshness must be either "past-day", "past-week", "past-month", "past-year" or in the format YYYY-MM-DDtoYYYY-MM-DD.',
			},
		)
		.optional(),
	text_decorations: z
		.boolean({ message: 'TextDecorations must be of type boolean.' })
		.default(true)
		.optional(),
	spellcheck: z
		.boolean({ message: 'SpellCheck must be of type boolean.' })
		.default(true)
		.optional(),
	result_filter: z
		.string({ message: 'ResultFilter must be of type string.' })
		.refine(
			(value) =>
				value
					.split(',')
					.every((filter) =>
						allowedSearchResultFilters.includes(filter.trim()),
					),
			{
				message: `ResultFilter must be a comma-separated string of valid types: ${allowedSearchResultFilters.join(
					', ',
				)}.`,
			},
		)
		.optional(),
	goggles_id: z
		.string({ message: 'GogglesId must be of type string.' })
		.optional(),
	units: z
		.enum(['metric', 'imperial'], {
			message: 'Units must be either "metric" or "imperial".',
		})
		.optional(),
	extra_snippets: z
		.boolean({ message: 'ExtraSnippets must be of type boolean.' })
		.optional(),
	summary: z
		.boolean({ message: 'Summary must be of type boolean.' })
		.optional(),
});

export type SearchParamsRequest = Zod.infer<typeof searchParamsSchema>;
