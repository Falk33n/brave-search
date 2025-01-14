<script
	lang="ts"
	module
>
	import type { ChatHistory } from '$lib/schemas';
	import hljs from 'highlight.js';
	import 'highlight.js/styles/default.css';
	import MarkdownIt from 'markdown-it';

	type SubmitEventWithTarget = SubmitEvent & {
		currentTarget: EventTarget & HTMLFormElement;
	};
</script>

<script lang="ts">
	let chatHistory = $state<ChatHistory>([]);
	let inputValue = $state('');
	let disabled = $state(false);

	const md = new MarkdownIt({
		highlight: function (str: string, lang: string): string {
			if (lang && hljs.getLanguage(lang)) {
				return `<pre><code class="hljs ${lang}">${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`;
			}

			return `<pre><code class="hljs">${md.utils.escapeHtml(str)}</code></pre>`;
		},
	});

	async function onsubmit(e: SubmitEventWithTarget) {
		e.preventDefault();

		const query = inputValue;
		const urlRegex = /(https?:\/\/[^\s]+)/g;
		const foundUrls = query.match(urlRegex);
		const indexUrl = foundUrls ? foundUrls[0] : undefined;

		inputValue = '';
		disabled = true;
		chatHistory.push({ role: 'user', content: query });

		try {
			const response = await fetch('/api/chat/provider', {
				body: JSON.stringify({
					searchParams: { query },
					indexUrl,
					chatHistory,
				}),
				headers: { 'Content-Type': 'application/json' },
				method: 'POST',
			});

			if (!response.ok) {
				throw new Error(`Error: ${response.statusText}`);
			}

			chatHistory.push({ ...(await response.json()) });
		} catch (error) {
			console.log(error);
		} finally {
			disabled = false;
		}
	}
</script>

<form
	onsubmit={async (e) => await onsubmit(e)}
	novalidate
	method="post"
	class="flex w-full flex-col justify-center gap-5"
>
	<input
		bind:value={inputValue}
		name="text"
		id="text"
		class="w-full rounded-md border border-neutral-300 px-6 py-1.5 outline-none"
	/>
	<button
		{disabled}
		aria-disabled={disabled}
		type="submit"
		class="w-fit rounded-md bg-blue-600 px-6 py-1.5 text-white disabled:cursor-not-allowed disabled:opacity-50"
	>
		Submit
	</button>
</form>

<div class="flex w-full flex-col justify-center gap-y-10 last:mb-48">
	{#each chatHistory as { role, content }}
		<section class="markdown-container w-full rounded-md bg-neutral-50 p-6">
			<h3 class="capitalize">{role}:</h3>
			{@html md.render(content)}
		</section>
	{/each}
	{#if disabled}
		<p class="animate-pulse p-6 text-neutral-500">Assistant is thinking...</p>
	{/if}
</div>

<style>
	:global(.markdown-container) {
		:first-child {
			margin-top: 0;
			font-size: 1.25rem;
			margin-bottom: 0.75rem;
		}
		& a {
			color: blue;
			border-radius: 5px;
			transition: color 200ms ease-in-out;
		}
		& a:visited {
			color: purple;
		}
		& a:hover {
			color: red;
		}
		& a:focus-visible {
			outline: 2px solid blue;
			outline-offset: 4px;
		}
		& a:hover,
		& a:focus-visible {
			text-decoration: underline;
			text-underline-offset: 2px;
		}
		& li {
			margin: 0.75rem 0 0.5rem;
		}
		& strong {
			font-weight: 600;
		}
		& hr {
			margin: 0.9rem;
		}
		& code {
			white-space: pre-wrap;
			background-color: blanchedalmond;
		}
	}
</style>
