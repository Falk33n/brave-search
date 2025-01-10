import { SECRET_BRAVE_KEY, SECRET_OPENAI_KEY } from '$env/static/private';
import { chatRequestSchema } from '$lib/schemas';
import { getSearchParamsConfig } from '$lib/server/utils';
import { error, json, type RequestHandler } from '@sveltejs/kit';
import OpenAI from 'openai';

const BRAVE_HEADERS = {
	'Accept': 'application/json',
	'Accept-Encoding': 'gzip',
	'X-Subscription-Token': SECRET_BRAVE_KEY,
};

const OPENAI_SYSTEM_PROMPT = {
	role: 'system',
	content:
		"You are a helpful assistant whose name is MinitronAI. You are tasked with analyzing search results and providing meaningful insights or answers. Based on the user's query and the provided results: 1. Summarize the most relevant information. 2. Highlight any useful links. 3. Provide additional suggestions or insights if necessary.",
} as const;

const openai = new OpenAI({ apiKey: SECRET_OPENAI_KEY });

export const POST: RequestHandler = async ({ request }) => {
	try {
		const parsedRequest = chatRequestSchema.safeParse({
			...(await request.json()),
		});

		if (!parsedRequest.success) {
			throw error(400, `${parsedRequest.error.errors}`);
		}

		const { searchParams, chatHistory } = parsedRequest.data;

		if (!searchParams) {
			throw error(500, 'No search params provided');
		}

		const configuredSearchParams = getSearchParamsConfig(searchParams);
		const urlSearchParams = new URLSearchParams(configuredSearchParams);
		const braveUrl = `https://api.search.brave.com/res/v1/web/search?${urlSearchParams.toString()}`;

		const braveResponse = await fetch(braveUrl, {
			method: 'GET',
			headers: BRAVE_HEADERS,
		});

		if (!braveResponse.ok) {
			throw error(
				500,
				`Error fetching brave data: ${braveResponse.statusText}`,
			);
		}

		const searchResults = await braveResponse.json();

		const openaiResponse = await openai.chat.completions.create({
			model: 'gpt-4o-mini',
			messages: [
				OPENAI_SYSTEM_PROMPT,
				...chatHistory.slice(0, -1),
				{
					role: 'user',
					content: `The search query was: "${searchParams.query}". Here are the search results in JSON format: ${JSON.stringify(searchResults)}`,
				},
			],
		});

		if (!openaiResponse.choices[0].message.content) {
			throw error(500, 'Error fetching OpenAI data');
		}

		return json(
			{
				role: 'assistant',
				content: openaiResponse.choices[0].message.content,
			},
			{ status: 200 },
		);
	} catch (e) {
		throw error(500, `Error: ${e}`);
	}
};
