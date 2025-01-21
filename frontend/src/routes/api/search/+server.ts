import { SECRET_BACKEND_HOST } from '$env/static/private';
import { chatRequestSchema } from '$lib/schemas';
import { error, json, type RequestHandler } from '@sveltejs/kit';

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

		const braveResponse = await fetch(`${SECRET_BACKEND_HOST}/search`, {
			body: JSON.stringify({ query: searchParams.query, chatHistory }),
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
		});

		if (!braveResponse.ok) {
			throw error(
				500,
				`Error fetching brave data: ${braveResponse.statusText}`,
			);
		}

		return json(
			{ role: 'assistant', content: await braveResponse.json() },
			{ status: 200 },
		);
	} catch (e) {
		throw error(500, `Error: ${e}`);
	}
};
