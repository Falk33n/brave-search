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
		"You are a helpful assistant named MinitronAI. You are tasked with analyzing a query made to a ChromaDB collection. Your job is to: 1. Analyze the Query: Carefully review the user's query and understand its intent and context. 2. Retrieve Relevant Information: Using the results from the ChromaDB collection, identify and extract the most relevant data points or sections that address the query. 3. Present Results as Markdown: Format the response as a Markdown document, including a clear visualization of the relevant results. Use headings, lists, tables, or code blocks as necessary to organize the information effectively. 4. Explain the Query: Provide a clear explanation of how the query was interpreted and how the results were chosen. Ensure the explanation is concise yet thorough, so the user understands the reasoning behind the response. If the query or results lack sufficient information to provide a detailed answer, respond with: 'I don't know, give me more information or refine the query.' Focus on presenting accurate and clearly structured information based on the query and collection results.",
} as const;

const openai = new OpenAI({ apiKey: SECRET_OPENAI_KEY });

type Metadata = {
	url: string;
	title: string;
	word_count: number;
	last_crawled: string;
	depth: number;
};

type ChromaDBQueryResponse = {
	ids: string[];
	metadatas: Metadata[];
	documents: string[];
};

function formatChromaDBResults(
	queryResponseData: ChromaDBQueryResponse,
): string {
	const { ids, metadatas, documents } = queryResponseData;

	let formattedResults = `### Retrieved Documents\n\n`;

	if (documents && documents.length > 0) {
		formattedResults += documents
			.map((doc: string, index: number) => {
				const id = ids?.[index] || 'Unknown ID';
				const metadata = metadatas?.[index]
					? JSON.stringify(metadatas[index], null, 2)
					: 'No metadata';

				return (
					`#### Document ${index + 1} (ID: ${id})\n\n` +
					`**Content:**\n\`\`\`\n${doc}\n\`\`\`\n\n` +
					`**Metadata:**\n\`\`\`json\n${metadata}\n\`\`\`\n`
				);
			})
			.join('\n');
	} else {
		formattedResults += '_No documents retrieved._\n';
	}

	return formattedResults;
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
			throw error(400, `No index url provided`);
		}

		const queryResponse = await fetch(
			`http://${SECRET_BACKEND_HOST}:${SECRET_BACKEND_PORT}/query`,
			{
				body: JSON.stringify({
					url: indexUrl,
					query: chatHistory[chatHistory.length - 1].content,
				}),
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
			},
		);

		if (!queryResponse.ok) {
			throw error(500, 'Error fetching query data');
		}

		const queryResponseData = await queryResponse.json();

		const openaiResponse = await openai.chat.completions.create({
			model: 'gpt-4o-mini',
			messages: [
				OPENAI_SYSTEM_PROMPT,
				...chatHistory.slice(0, -1),
				{
					role: 'user',
					content: `The context was: "${chatHistory[chatHistory.length - 1].content}", Here is the content retrieved from the database query in Markdown format: ${formatChromaDBResults(queryResponseData)}
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
		console.log(e);
		throw error(500, `Error: ${e}`);
	}
};
