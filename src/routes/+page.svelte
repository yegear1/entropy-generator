<script lang="ts">
    import { onMount } from 'svelte';
    import EntropyCanvas from '$lib/components/EntropyCanvas.svelte';

    let activeMode = $state<'password' | 'passphrase'>('password');
    let isGenerating = $state(false);
    let output = $state('Initializing...');
    let isCopied = $state(false);
    let showEntropyInfo = $state(false);

    // Password Settings
    let sliderValue = $state(500);
    const SLIDER_MAX = 1000;
    const LOG_MIN = 9;
    const LOG_MAX = 128;
    
    let length = $derived(Math.round(LOG_MIN * Math.pow(LOG_MAX / LOG_MIN, sliderValue / SLIDER_MAX)));
    
    let useUpper = $state(true);
    let useLower = $state(true);
    let useDigits = $state(true);
    let useSpecials = $state(true);
    let useEmojis = $state(false);

    // Passphrase Settings
    let wordCount = $state(6);
    let language = $state<'en' | 'pt'>('en');

    // Entropy calculation
    let bits = $derived.by(() => {
        if (activeMode === 'password') {
            let poolSize = 0;
            if (useUpper) poolSize += 26;
            if (useLower) poolSize += 26;
            if (useDigits) poolSize += 10;
            if (useSpecials) poolSize += 32;
            if (useEmojis) poolSize += 3000;
            return poolSize > 0 ? Math.round(length * Math.log2(poolSize)) : 0;
        } else {
            return Math.round(wordCount * Math.log2(7776));
        }
    });

    let entropyLabel = $derived(
        bits < 50 ? 'Weak' :
        bits < 80 ? 'Fair' :
        bits < 128 ? 'Strong' : 'Military 🔒'
    );
    
    let entropyColorClass = $derived(
        bits < 50 ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]' :
        bits < 80 ? 'bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.4)]' :
        bits < 128 ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]' :
        'bg-cyan-400 shadow-[0_0_12px_rgba(34,211,238,0.5)]'
    );
    
    let entropyTextClass = $derived(
        bits < 50 ? 'text-red-400' :
        bits < 80 ? 'text-yellow-400' :
        bits < 128 ? 'text-emerald-400' :
        'text-cyan-400'
    );
    
    let entropyWidthPct = $derived(Math.min(100, Math.round((bits / 256) * 100)));
    let entropyWidth = $derived(bits < 50 ? Math.max(entropyWidthPct, 8) : entropyWidthPct);

    // Cooldown State
    let isCoolingDown = $state(false);
    let cooldownWidth = $state(0);
    let cooldownTransitionDuration = $state(0);
    const COOLDOWN_MS = 1500;

    async function generateEntropy() {
        if (isGenerating || isCoolingDown) return;
        
        isGenerating = true;
        try {
            let url = '';
            if (activeMode === 'password') {
                const params = new URLSearchParams({
                    length: length.toString(),
                    use_upper: useUpper.toString(),
                    use_lower: useLower.toString(),
                    use_digits: useDigits.toString(),
                    use_specials: useSpecials.toString(),
                    use_emojis: useEmojis.toString()
                });
                url = `/api/v1/generate/password?${params.toString()}`;
            } else {
                const params = new URLSearchParams({
                    words: wordCount.toString(),
                    language: language
                });
                url = `/api/v1/generate/passphrase?${params.toString()}`;
            }

            const response = await fetch(url);
            const data = await response.json();
            
            output = activeMode === 'password' ? data.password : data.passphrase;
        } catch (e) {
            console.error("API error", e);
            output = "Error generating entropy";
        } finally {
            isGenerating = false;
            startCooldown();
        }
    }

    function startCooldown() {
        isCoolingDown = true;
        cooldownTransitionDuration = 0;
        cooldownWidth = 100;
        
        // Force reflow for the transition
        setTimeout(() => {
            cooldownTransitionDuration = COOLDOWN_MS;
            cooldownWidth = 0;
            
            setTimeout(() => {
                isCoolingDown = false;
            }, COOLDOWN_MS);
        }, 10);
    }

    async function copyToClipboard() {
        if (!output || isGenerating || output.includes('Error')) return;
        try {
            await navigator.clipboard.writeText(output);
            isCopied = true;
            setTimeout(() => { isCopied = false; }, 2000);
        } catch (e) {
            console.error('Clipboard error', e);
        }
    }

    // Helper functions for slider tick marks
    const passwordTicks = [12, 16, 24, 32, 64, 128].map(val => ({
        val,
        pct: ((Math.log(val / LOG_MIN) / Math.log(LOG_MAX / LOG_MIN)) * SLIDER_MAX / SLIDER_MAX) * 100
    }));

    const passphraseTicks = [5, 8, 16, 24, 32].map(val => ({
        val,
        pct: ((val - 5) / (32 - 5)) * 100
    }));

    onMount(() => {
        sliderValue = Math.round((Math.log(24 / LOG_MIN) / Math.log(LOG_MAX / LOG_MIN)) * SLIDER_MAX);
        generateEntropy();
    });
</script>

<svelte:head>
    <title>YeHub Entropy</title>
    <script src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
</svelte:head>

<div class="bg-neutral-950 text-neutral-300 min-h-screen flex flex-col antialiased selection:bg-neutral-800 selection:text-white global-font">
    
    <EntropyCanvas />
    
    <main class="flex-1 w-full max-w-2xl mx-auto px-4 py-16 flex flex-col gap-10 relative z-10">
        
        <!-- Header -->
        <header class="flex flex-col items-center text-center gap-3 relative">
            <div class="h-10 w-10 bg-white rounded-lg flex items-center justify-center text-neutral-950 text-sm font-semibold tracking-tighter shadow-[0_0_15px_rgba(255,255,255,0.1)]">
                YH
            </div>
            <div class="space-y-1">
                <h1 class="text-2xl font-medium tracking-tight text-white">Entropy Generator</h1>
                <p class="text-sm text-neutral-500">Enterprise-grade cryptographic key synthesis.</p>
            </div>
            <a href="https://github.com/yegear1/entropy-generator" target="_blank" rel="noopener noreferrer" class="absolute top-0 right-0 p-2 rounded-lg text-neutral-600 hover:text-white hover:bg-neutral-800/50 transition-all" aria-label="View source code on GitHub">
                <iconify-icon icon="mdi:github" class="text-xl"></iconify-icon>
            </a>
        </header>

        <!-- Main Interface -->
        <div class="flex flex-col gap-6">
            
            <!-- Output Display -->
            <div class="relative group rounded-xl bg-neutral-900/80 backdrop-blur-sm border border-neutral-800 p-8 shadow-2xl overflow-hidden flex flex-col items-center justify-center min-h-[8rem]">
                <div class="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none"></div>
                
                {#if isGenerating}
                <!-- Skeleton Loader -->
                <div class="w-full flex flex-col items-center gap-3 z-10">
                    <div class="skeleton-block w-3/4"></div>
                    <div class="skeleton-block w-1/2"></div>
                </div>
                {:else}
                <!-- Actual Output -->
                <div class="font-mono text-2xl text-white break-all text-center leading-relaxed z-10 transition-opacity duration-200">
                    {output}
                </div>
                {/if}
                
                <button onclick={copyToClipboard} class="absolute top-4 right-4 p-2 rounded-md bg-neutral-800/0 hover:bg-neutral-800 text-neutral-400 hover:text-white transition-all z-20 flex items-center justify-center group/btn" aria-label="Copy to clipboard">
                    {#if isCopied}
                        <iconify-icon icon="solar:check-circle-linear" stroke-width="1.5" class="text-lg text-green-400"></iconify-icon>
                    {:else}
                        <iconify-icon icon="solar:copy-linear" stroke-width="1.5" class="text-lg transition-transform group-hover/btn:scale-110"></iconify-icon>
                    {/if}
                </button>
            </div>

            <!-- Entropy Meter -->
            <div>
                <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-2">
                        <iconify-icon icon="solar:shield-check-linear" class="text-neutral-500 text-sm"></iconify-icon>
                        <span class="text-xs font-medium text-neutral-500 uppercase tracking-wider">Entropy Strength</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-mono {entropyTextClass}">{bits} bits — {entropyLabel}</span>
                        <button onclick={() => showEntropyInfo = !showEntropyInfo} class="text-neutral-600 hover:text-neutral-300 transition-colors" aria-label="How is entropy calculated?">
                            <iconify-icon icon="solar:info-circle-linear" class="text-sm"></iconify-icon>
                        </button>
                    </div>
                </div>
                <div class="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-500 ease-out {entropyColorClass}" style="width: {entropyWidth}%"></div>
                </div>
                <!-- Entropy Formula Explanation (collapsible) -->
                {#if showEntropyInfo}
                <div class="mt-3 p-4 bg-neutral-900/80 border border-neutral-800 rounded-lg text-xs text-neutral-400 space-y-2.5 animate-[fadeIn_0.2s_ease-out]">
                    <div class="flex items-center gap-2 text-neutral-300 font-medium text-sm">
                        <iconify-icon icon="solar:calculator-linear" class="text-base"></iconify-icon>
                        How entropy is calculated
                    </div>
                    <div class="space-y-1.5 font-mono text-[0.7rem] leading-relaxed">
                        <p><span class="text-white">Password:</span> E = L × log₂(R)</p>
                        <p class="text-neutral-500">L = length, R = pool size (unique characters)</p>
                        <p class="text-neutral-500">R = uppercase(26) + lowercase(26) + digits(10) + symbols(32) + emojis(~3000)</p>
                        <p class="mt-2"><span class="text-white">Passphrase:</span> E = W × log₂(7776)</p>
                        <p class="text-neutral-500">W = word count, 7776 = EFF Diceware wordlist size</p>
                    </div>
                    <div class="border-t border-neutral-800 pt-2 space-y-1">
                        <p class="text-neutral-500">&lt; 50 bits → <span class="text-red-400">Weak</span> (brute-forceable)</p>
                        <p class="text-neutral-500">50–79 bits → <span class="text-yellow-400">Fair</span> (limited protection)</p>
                        <p class="text-neutral-500">80–127 bits → <span class="text-emerald-400">Strong</span> (secure for most uses)</p>
                        <p class="text-neutral-500">≥ 128 bits → <span class="text-cyan-400">Military</span> (quantum-resistant tier)</p>
                    </div>
                </div>
                {/if}
            </div>

            <!-- Configuration Card -->
            <div class="bg-neutral-900/50 backdrop-blur-md rounded-xl border border-neutral-800 overflow-hidden">
                
                <!-- Tab Navigation -->
                <div class="flex p-1 bg-neutral-900/50 border-b border-neutral-800">
                    <button onclick={() => activeMode = 'password'} class="flex-1 py-2 text-sm font-medium rounded-lg transition-all duration-200 {activeMode === 'password' ? 'bg-neutral-800 text-white shadow-sm' : 'text-neutral-400 hover:text-neutral-200'}">Password</button>
                    <button onclick={() => activeMode = 'passphrase'} class="flex-1 py-2 text-sm font-medium rounded-lg transition-all duration-200 {activeMode === 'passphrase' ? 'bg-neutral-800 text-white shadow-sm' : 'text-neutral-400 hover:text-neutral-200'}">Passphrase</button>
                </div>

                <div class="p-6">
                    {#if activeMode === 'password'}
                    <!-- Password View -->
                    <div class="flex flex-col gap-8 animate-[fadeIn_0.2s_ease-out]">
                        
                        <!-- Length Slider (logarithmic) -->
                        <div class="flex flex-col gap-2">
                            <div class="flex justify-between items-center text-sm">
                                <span class="font-medium text-neutral-200">Length</span>
                                <span class="text-neutral-400 font-mono text-xs bg-neutral-950 border border-neutral-800 px-2 py-1 rounded-md min-w-[2.5rem] text-center">{length}</span>
                            </div>
                            <input bind:value={sliderValue} type="range" min="0" max="1000" class="w-full custom-range">
                            <div class="slider-ticks">
                                {#each passwordTicks as tick}
                                <div class="slider-tick" style="left: {tick.pct}%">
                                    <div class="slider-tick-line"></div>
                                    <span class="slider-tick-label">{tick.val}</span>
                                </div>
                                {/each}
                            </div>
                        </div>

                        <!-- Options Grid -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-y-5 gap-x-8">
                            
                            <!-- Toggle Checkboxes -->
                            <label class="flex items-center justify-between cursor-pointer group">
                                <span class="text-sm font-medium text-neutral-400 group-hover:text-neutral-200 transition-colors">Uppercase (A-Z)</span>
                                <div class="relative flex items-center">
                                    <input type="checkbox" bind:checked={useUpper} class="sr-only peer">
                                    <div class="w-8 h-4 bg-neutral-800 rounded-full peer peer-checked:bg-white/90 transition-colors duration-200"></div>
                                    <div class="absolute left-[2px] bg-neutral-400 peer-checked:bg-neutral-950 w-3 h-3 rounded-full transition-transform duration-200 peer-checked:translate-x-4"></div>
                                </div>
                            </label>

                            <label class="flex items-center justify-between cursor-pointer group">
                                <span class="text-sm font-medium text-neutral-400 group-hover:text-neutral-200 transition-colors">Lowercase (a-z)</span>
                                <div class="relative flex items-center">
                                    <input type="checkbox" bind:checked={useLower} class="sr-only peer">
                                    <div class="w-8 h-4 bg-neutral-800 rounded-full peer peer-checked:bg-white/90 transition-colors duration-200"></div>
                                    <div class="absolute left-[2px] bg-neutral-400 peer-checked:bg-neutral-950 w-3 h-3 rounded-full transition-transform duration-200 peer-checked:translate-x-4"></div>
                                </div>
                            </label>

                            <label class="flex items-center justify-between cursor-pointer group">
                                <span class="text-sm font-medium text-neutral-400 group-hover:text-neutral-200 transition-colors">Numbers (0-9)</span>
                                <div class="relative flex items-center">
                                    <input type="checkbox" bind:checked={useDigits} class="sr-only peer">
                                    <div class="w-8 h-4 bg-neutral-800 rounded-full peer peer-checked:bg-white/90 transition-colors duration-200"></div>
                                    <div class="absolute left-[2px] bg-neutral-400 peer-checked:bg-neutral-950 w-3 h-3 rounded-full transition-transform duration-200 peer-checked:translate-x-4"></div>
                                </div>
                            </label>

                            <label class="flex items-center justify-between cursor-pointer group">
                                <span class="text-sm font-medium text-neutral-400 group-hover:text-neutral-200 transition-colors">Symbols (!@#$)</span>
                                <div class="relative flex items-center">
                                    <input type="checkbox" bind:checked={useSpecials} class="sr-only peer">
                                    <div class="w-8 h-4 bg-neutral-800 rounded-full peer peer-checked:bg-white/90 transition-colors duration-200"></div>
                                    <div class="absolute left-[2px] bg-neutral-400 peer-checked:bg-neutral-950 w-3 h-3 rounded-full transition-transform duration-200 peer-checked:translate-x-4"></div>
                                </div>
                            </label>

                            <div class="col-span-1 sm:col-span-2 pt-2 border-t border-neutral-800/50">
                                <label class="flex flex-col gap-1.5 cursor-pointer group">
                                    <div class="flex items-center justify-between">
                                        <span class="text-sm font-medium text-neutral-400 group-hover:text-neutral-200 transition-colors">Include Emojis (🚀👽🔥)</span>
                                        <div class="relative flex items-center">
                                            <input type="checkbox" bind:checked={useEmojis} class="sr-only peer">
                                            <div class="w-8 h-4 bg-neutral-800 rounded-full peer peer-checked:bg-white/90 transition-colors duration-200"></div>
                                            <div class="absolute left-[2px] bg-neutral-400 peer-checked:bg-neutral-950 w-3 h-3 rounded-full transition-transform duration-200 peer-checked:translate-x-4"></div>
                                        </div>
                                    </div>
                                    <span class="text-xs text-neutral-500">High entropy, but might not be supported by all websites.</span>
                                </label>
                            </div>

                        </div>
                    </div>
                    {:else}
                    <!-- Passphrase View -->
                    <div class="flex flex-col gap-8 animate-[fadeIn_0.2s_ease-out]">
                        
                        <!-- Words Slider -->
                        <div class="flex flex-col gap-2">
                            <div class="flex justify-between items-center text-sm">
                                <span class="font-medium text-neutral-200">Word Count</span>
                                <span class="text-neutral-400 font-mono text-xs bg-neutral-950 border border-neutral-800 px-2 py-1 rounded-md min-w-[2.5rem] text-center">{wordCount}</span>
                            </div>
                            <input bind:value={wordCount} type="range" min="5" max="32" class="w-full custom-range">
                            <div class="slider-ticks">
                                {#each passphraseTicks as tick}
                                <div class="slider-tick" style="left: {tick.pct}%">
                                    <div class="slider-tick-line"></div>
                                    <span class="slider-tick-label">{tick.val}</span>
                                </div>
                                {/each}
                            </div>
                        </div>

                        <!-- Language Selector -->
                        <div class="flex flex-col gap-3">
                            <span class="text-sm font-medium text-neutral-200">Dictionary</span>
                            <div class="grid grid-cols-2 gap-3">
                                <label class="cursor-pointer">
                                    <input type="radio" bind:group={language} value="en" class="sr-only peer">
                                    <div class="px-4 py-2.5 text-sm text-center font-medium rounded-lg border border-neutral-800 bg-neutral-950 text-neutral-500 peer-checked:border-neutral-500 peer-checked:text-neutral-200 hover:bg-neutral-900 transition-all">English</div>
                                </label>
                                <label class="cursor-pointer">
                                    <input type="radio" bind:group={language} value="pt" class="sr-only peer">
                                    <div class="px-4 py-2.5 text-sm text-center font-medium rounded-lg border border-neutral-800 bg-neutral-950 text-neutral-500 peer-checked:border-neutral-500 peer-checked:text-neutral-200 hover:bg-neutral-900 transition-all">Portuguese</div>
                                </label>
                            </div>
                        </div>

                    </div>
                    {/if}
                </div>
            </div>

            <!-- Generate CTA -->
            <button onclick={generateEntropy} disabled={isGenerating || isCoolingDown} class="relative w-full py-3.5 px-4 bg-white text-neutral-950 font-medium text-sm rounded-xl hover:bg-neutral-200 hover:scale-[1.01] active:scale-[0.99] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(255,255,255,0.05)] overflow-hidden">
                <iconify-icon icon="solar:magic-stick-3-linear" stroke-width="1.5" class="text-lg"></iconify-icon>
                <span>Generate Entropy</span>
                <div class="btn-cooldown-bar" style="width: {cooldownWidth}%; transition: {cooldownTransitionDuration > 0 ? `width ${cooldownTransitionDuration}ms linear` : 'none'}"></div>
            </button>

        </div>
    </main>
</div>

<style>
    .global-font {
        font-family: 'Inter', sans-serif;
    }
    .font-mono {
        font-family: 'JetBrains Mono', monospace;
    }

    /* Custom Range Slider */
    .custom-range {
        -webkit-appearance: none;
        appearance: none;
        background: transparent;
    }
    .custom-range::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        height: 1rem;
        width: 1rem;
        border-radius: 50%;
        background: #ffffff;
        cursor: pointer;
        margin-top: -0.375rem;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.1s;
        position: relative;
        z-index: 2;
    }
    .custom-range::-webkit-slider-thumb:hover {
        transform: scale(1.1);
    }
    .custom-range::-webkit-slider-runnable-track {
        width: 100%;
        height: 0.25rem;
        cursor: pointer;
        background: #262626;
        border-radius: 9999px;
    }
    .custom-range::-moz-range-thumb {
        height: 1rem;
        width: 1rem;
        border-radius: 50%;
        background: #ffffff;
        cursor: pointer;
        border: none;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.1s;
    }
    .custom-range::-moz-range-thumb:hover {
        transform: scale(1.1);
    }
    .custom-range::-moz-range-track {
        width: 100%;
        height: 0.25rem;
        cursor: pointer;
        background: #262626;
        border-radius: 9999px;
    }

    /* Skeleton Loader */
    @keyframes skeletonShimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    .skeleton-block {
        height: 1.75rem;
        border-radius: 0.5rem;
        background: linear-gradient(90deg, #262626 25%, #3a3a3a 50%, #262626 75%);
        background-size: 200% 100%;
        animation: skeletonShimmer 1.5s ease-in-out infinite;
    }

    /* Slider tick marks */
    .slider-ticks {
        position: relative;
        height: 12px;
        margin-top: 4px;
    }
    .slider-tick {
        position: absolute;
        display: flex;
        flex-direction: column;
        align-items: center;
        transform: translateX(-50%);
    }
    .slider-tick-line {
        width: 1px;
        height: 6px;
        background: #525252;
    }
    .slider-tick-label {
        font-size: 0.625rem;
        color: #737373;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 2px;
        line-height: 1;
    }

    /* Cooldown progress bar on generate button */
    .btn-cooldown-bar {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 0 0 0.75rem 0.75rem;
    }
</style>