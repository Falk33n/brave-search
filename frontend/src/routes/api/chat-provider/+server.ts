import { SECRET_OPENAI_KEY } from '$env/static/private';
import { chatRequestSchema, type Chat } from '$lib/schemas';
import { error, json, type RequestHandler } from '@sveltejs/kit';
import OpenAI from 'openai';

const OPENAI_SYSTEM_PROMPT = {
	role: 'system',
	content:
		'Determine if the following query requires a web search or can be answered directly. Respond only with "search" or "chat".',
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

		const searchOrChatResponse = await openai.chat.completions.create({
			model: 'gpt-3.5-turbo',
			messages: [OPENAI_SYSTEM_PROMPT, chatHistory[chatHistory.length - 1]],
		});

		if (!searchOrChatResponse.choices[0].message.content) {
			throw error(500, 'Error fetching OpenAI data');
		}

		const isChat =
			searchOrChatResponse.choices[0].message.content.toLowerCase().trim() ===
			'chat';

		let responseData: Chat | undefined;

		const baseUrl = new URL(request.url).origin;

		if (isChat) {
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
		} else {
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
		}

		if (!responseData) {
			throw error(500, 'Error fetching response data from OpenAI API');
		}

		return json({ ...responseData }, { status: 200 });
	} catch (error) {
		return json(error, { status: 500 });
	}
};
