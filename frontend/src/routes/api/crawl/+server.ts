import {
	SECRET_BACKEND_HOST,
	SECRET_BACKEND_PORT,
	SECRET_OPENAI_KEY,
} from '$env/static/private';
import { chatRequestSchema } from '$lib/schemas';
import { error, json, type RequestHandler } from '@sveltejs/kit';
import OpenAI from 'openai';

const OPENAI_SYSTEM_PROMPT = {
	role: 'system',
	content:
		"You are a helpful assistant named MinitronAI. You are given a Markdown document that represents a crawled webpage. Your task is to: 1. Analyze the Markdown Content: Carefully review the provided Markdown document and understand its structure. 2. Retrieve Relevant Information: Based on the context in the user's question (provided separately), find and extract the most relevant sections of the Markdown that answer the question. 3. Highlight the Source: When returning the information, mark or reference the specific section, heading, or excerpt where the information was found. You should also provide the surrounding context to ensure the answer is clear. If the Markdown document does not contain enough information to provide a detailed answer, respond with: 'I don't know, give me more information.' Do not make up answers or infer information not directly present in the Markdown. Your focus is on extracting and presenting the relevant information as accurately as possible.",
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

		const { chatHistory, indexUrl } = parsedRequest.data;

		if (!indexUrl) {
			throw error(400, `No index url provided`);
		}

		const crawlResponse = await fetch(
			`http://${SECRET_BACKEND_HOST}:${SECRET_BACKEND_PORT}/crawl/page`,
			{
				body: JSON.stringify({ url: indexUrl }),
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
			},
		);

		if (!crawlResponse.ok) {
			throw error(500, 'Error fetching crawl data');
		}

		const crawlResponseData: { title: string; content: string } =
			await crawlResponse.json();

		const openaiResponse = await openai.chat.completions.create({
			model: 'gpt-4o-mini',
			messages: [
				OPENAI_SYSTEM_PROMPT,
				...chatHistory.slice(0, -1),
				{
					role: 'user',
					content: `The context was: "${chatHistory[chatHistory.length - 1].content}", Here is the content retrieved from the crawled webpage in Markdown format: ${crawlResponseData.content}
        `,
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
