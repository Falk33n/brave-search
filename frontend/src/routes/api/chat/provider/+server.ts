import { SECRET_OPENAI_KEY } from '$env/static/private';
import { chatRequestSchema, type Chat } from '$lib/schemas';
import { error, json, type RequestHandler } from '@sveltejs/kit';
import OpenAI from 'openai';

const OPENAI_SYSTEM_PROMPT = {
	role: 'system',
	content:
		'Analyze the following query and determine how to respond: 1. If the user has provided a URL (e.g., "https://...") and the query suggests the user wants information from that specific URL, respond with "crawl". 2. If the query requires retrieving information from the web, but no specific URL is mentioned, respond with "search". 3. If the query can be answered with existing knowledge or prior content without needing a web search or crawl, respond with "chat".',
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

		const { searchParams, chatHistory, indexUrl } = parsedRequest.data;

		const searchOrChatOrCrawlResponse = await openai.chat.completions.create({
			model: 'gpt-3.5-turbo',
			messages: [OPENAI_SYSTEM_PROMPT, chatHistory[chatHistory.length - 1]],
		});

		if (!searchOrChatOrCrawlResponse.choices[0].message.content) {
			throw error(500, 'Error fetching OpenAI data');
		}

		const openaiResponse =
			searchOrChatOrCrawlResponse.choices[0].message.content
				.toLowerCase()
				.trim();

		if (
			openaiResponse !== 'search' &&
			openaiResponse !== 'chat' &&
			openaiResponse !== 'crawl'
		) {
			throw error(500, 'Error fetching OpenAI data');
		}

		const baseUrl = new URL(request.url).origin;
		let responseData: Chat | undefined;

		if (openaiResponse === 'chat') {
			const chatResponse = await fetch(`${baseUrl}/api/chat`, {
				body: JSON.stringify(chatHistory),
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
			});

			if (!chatResponse.ok) {
				throw error(
					500,
					'Error fetching chat response from /api/chat endpoint',
				);
			}

			responseData = { ...(await chatResponse.json()) };
		} else if (openaiResponse === 'search') {
			if (!searchParams) {
				throw error(400, 'Bad request for /api/search endpoint');
			}

			const searchResponse = await fetch(`${baseUrl}/api/search`, {
				body: JSON.stringify({
					searchParams,
					chatHistory,
				}),
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
			});

			if (!searchResponse.ok) {
				throw error(
					500,
					'Error fetching chat response from /api/search endpoint',
				);
			}

			responseData = { ...(await searchResponse.json()) };
		} else if (openaiResponse === 'crawl') {
			if (!indexUrl) {
				throw error(400, 'Bad request for /api/crawl/provider endpoint');
			}

			const crawlResponse = await fetch(`${baseUrl}/api/crawl/provider`, {
				body: JSON.stringify({
					chatHistory,
					indexUrl,
				}),
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
			});

			if (!crawlResponse.ok) {
				throw error(
					500,
					'Error fetching chat response from /api/crawl/provider endpoint',
				);
			}

			responseData = { ...(await crawlResponse.json()) };
		}

		if (!responseData) {
			throw error(500, 'Error fetching response data from OpenAI API');
		}

		return json({ ...responseData }, { status: 200 });
	} catch (error) {
		return json(error, { status: 500 });
	}
};
