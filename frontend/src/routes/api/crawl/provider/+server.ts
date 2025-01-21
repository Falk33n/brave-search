import {
	SECRET_BACKEND_HOST,
	SECRET_BACKEND_PORT,
	SECRET_OPENAI_KEY,
} from '$env/static/private';
import { chatRequestSchema, type Chat } from '$lib/schemas';
import { error, json, type RequestHandler } from '@sveltejs/kit';
import OpenAI from 'openai';

const OPENAI_SYSTEM_PROMPT_RELEVANCE = {
	role: 'system',
	content: `You are provided with a context and a list of URLs. From this list, choose the one that best matches the context. Only return a single URL from the list. If none of the URLs match, return 'DIVE_DEEPER'.`,
} as const;

const openai = new OpenAI({ apiKey: SECRET_OPENAI_KEY });

async function crawlAndValidateUrls(
	currentUrl: string,
	context: string,
	level: number,
	maxDepth: number = 3,
): Promise<string | null> {
	if (level > maxDepth) {
		return null;
	}

	const crawlUrlsResponse = await fetch(
		`http://${SECRET_BACKEND_HOST}:${SECRET_BACKEND_PORT}/crawl/urls`,
		{
			body: JSON.stringify({ url: currentUrl }),
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
		},
	);

	if (!crawlUrlsResponse.ok) {
		throw error(500, 'Error fetching crawl URLs data');
	}

	const urls: string[] = await crawlUrlsResponse.json();

	const relevanceResponse = await openai.chat.completions.create({
		model: 'gpt-3.5-turbo',
		messages: [
			OPENAI_SYSTEM_PROMPT_RELEVANCE,
			{
				role: 'user',
				content: `Context: ${context} Available URLs: ${urls.join(', ')}`,
			},
		],
	});

	const chosenUrl = relevanceResponse.choices[0]?.message?.content;

	if (chosenUrl === 'DIVE_DEEPER') {
		for (const url of urls) {
			const result = await crawlAndValidateUrls(
				url,
				context,
				level + 1,
				maxDepth,
			);

			if (result) return result;
		}

		return null;
	}

	if (chosenUrl && urls.includes(chosenUrl)) {
		return chosenUrl;
	}

	return null;
}

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
			throw error(400, 'Index URL is required');
		}

		const contextWithoutUrls = chatHistory[
			chatHistory.length - 1
		].content.replace(/https?:\/\/[^\s]+/g, '');

		const relevantUrl = await crawlAndValidateUrls(
			indexUrl,
			contextWithoutUrls,
			0,
		);

		if (!relevantUrl) {
			throw error(404, 'No relevant URL found even after multiple levels.');
		}

		const baseUrl = new URL(request.url).origin;

		const crawlPageResponse = await fetch(`${baseUrl}/api/crawl`, {
			body: JSON.stringify({ chatHistory, indexUrl: relevantUrl }),
			headers: { 'Content-Type': 'application/json' },
			method: 'POST',
		});

		if (!crawlPageResponse.ok) {
			throw error(500, 'Error fetching crawl data');
		}

		const crawlPageData: Chat = await crawlPageResponse.json();

		return json(crawlPageData, { status: 200 });
	} catch (e) {
		throw error(500, `Error: ${e}`);
	}
};
