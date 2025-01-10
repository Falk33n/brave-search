<script lang="ts">
	import '$src/app.css';
	let { children } = $props();
</script>

<div
	class="mx-auto flex min-h-screen w-[700px] flex-col items-center gap-20 pt-20"
>
	{@render children()}
</div>
