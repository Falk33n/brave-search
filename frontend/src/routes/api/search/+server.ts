import { SECRET_BACKEND_HOST, SECRET_BACKEND_PORT } from '$env/static/private';
import { searchRequestSchema } from '$lib/schemas';
import { BAD_REQUEST, INTERNAL_SERVER_ERROR, OK } from '$lib/server/constants';
import { error, json, type RequestHandler } from '@sveltejs/kit';

type SearchProps = Zod.infer<typeof searchRequestSchema>;

async function parseRequest(request: Request): Promise<SearchProps> {
	const jsonRequest: SearchProps = await request.json();
	const parsedRequest = searchRequestSchema.safeParse({
		...jsonRequest,
	});

	if (!parsedRequest.success) {
		const requestErrors = parsedRequest.error.errors;
		error(BAD_REQUEST, `Error parsing request: ${requestErrors}`);
	}

	return parsedRequest.data;
}

const BACKEND_BASE_URL = `http://${SECRET_BACKEND_HOST}:${SECRET_BACKEND_PORT}`;

async function fetchBackend({ searchParams, chatHistory }: SearchProps) {
	const response = await fetch(`${BACKEND_BASE_URL}/search`, {
		body: JSON.stringify({ query: searchParams.query, chatHistory }),
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
	});

	if (!response.ok) {
		error(
			INTERNAL_SERVER_ERROR,
			`Error fetching brave data: ${response.statusText}`,
		);
	}

	return response;
}

export const POST: RequestHandler = async ({ request }) => {
	const { searchParams, chatHistory } = await parseRequest(request);
	const response = await fetchBackend({ searchParams, chatHistory });
	const responseData = await response.json();
	return json({ role: 'assistant', content: responseData }, { status: OK });
};
