import { searchParamsSchema } from '$lib/schemas';
import { z } from 'zod';

export const chatSchema = z.object({
	role: z.enum(['user', 'assistant', 'system'], {
		message: 'Role must be either "user", "assistant" or "system".',
	}),
	content: z
		.string({
			message: 'Content must be a string.',
		})
		.nonempty({ message: 'Content must not be a empty string.' }),
});

export type Chat = Zod.infer<typeof chatSchema>;

export const chatHistorySchema = z.array(chatSchema);

export type ChatHistory = Zod.infer<typeof chatHistorySchema>;

export const chatRequestSchema = z.object({
	searchParams: searchParamsSchema.optional(),
	chatHistory: chatHistorySchema,
	indexUrl: z.string().url('Index URL is not valid.').optional(),
});

export type ChatRequest = Zod.infer<typeof chatRequestSchema>;
