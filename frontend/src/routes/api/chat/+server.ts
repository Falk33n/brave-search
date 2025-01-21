import { SECRET_OPENAI_KEY } from '$env/static/private';
import { chatRequestSchema } from '$lib/schemas';
import { error, json, type RequestHandler } from '@sveltejs/kit';
import OpenAI from 'openai';

const OPENAI_SYSTEM_PROMPT = {
	role: 'system',
	content:
		"You are a helpful assistant whose name is MinitronAI. Answer the user's question based on the provided context. If the context is not sufficient, respond with 'I don't know, give me more information.'. Do not make up answers.",
} as const;

const openai = new OpenAI({ apiKey: SECRET_OPENAI_KEY });

export const POST: RequestHandler = async ({ request }) => {
	try {
		const parsedRequest = chatRequestSchema.safeParse({
			chatHistory: await request.json(),
		});

		if (!parsedRequest.success) {
			throw error(400, `${parsedRequest.error.errors}`);
		}

		const { chatHistory } = parsedRequest.data;

		const openaiResponse = await openai.chat.completions.create({
			model: 'o1',
			messages: [OPENAI_SYSTEM_PROMPT, ...chatHistory],
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
