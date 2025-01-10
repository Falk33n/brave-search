type MarkDownAndText = { type: 'markdown' | 'text'; content: string };

export function splitMarkdownAndText(content: string): MarkDownAndText[] {
	const regex = /([#*_`[\]]+.*?[#*_`[\]]+)|([^#*_`[\]]+)/g;

	const result: MarkDownAndText[] = [];
	let match;

	while ((match = regex.exec(content)) !== null) {
		if (match[1]) {
			result.push({ type: 'markdown', content: match[1].trim() });
		} else if (match[2]) {
			result.push({ type: 'text', content: match[2].trim() });
		}
	}

	return result;
}
