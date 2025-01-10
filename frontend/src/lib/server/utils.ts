import type { SearchParamsRequest } from '$lib/schemas';

export function getSearchParamsConfig(searchParams: SearchParamsRequest) {
	const {
		freshness,
		count,
		offset,
		text_decorations,
		spellcheck,
		extra_snippets,
		summary,
		...restSearchParams
	} = searchParams;

	const config: Record<string, string> = {
		q: searchParams.query,
		...(count !== undefined && { count: count.toString() }),
		...(offset !== undefined && { offset: offset.toString() }),
		...(freshness !== undefined && {
			freshness:
				freshness === 'past-day'
					? 'pd'
					: freshness === 'past-week'
						? 'pw'
						: freshness === 'past-month'
							? 'pm'
							: freshness === 'past-year'
								? 'py'
								: freshness,
		}),
		...(text_decorations !== undefined && {
			text_decorations: text_decorations ? '1' : '0',
		}),
		...(spellcheck !== undefined && { spellcheck: spellcheck ? '1' : '0' }),
		...(extra_snippets !== undefined && {
			extra_snippets: extra_snippets ? '1' : '0',
		}),
		...(summary !== undefined && { summary: summary ? '1' : '0' }),
		...restSearchParams,
	};

	return config;
}
