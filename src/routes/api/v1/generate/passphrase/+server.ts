import { json } from '@sveltejs/kit';
import englishRaw from '$lib/data/english_wordlist.txt?raw';
import ptRaw from '$lib/data/portuguese.wordlist.txt?raw';

function parseWordlist(raw: string) {
    return raw.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => {
            const parts = line.split(/[\t ]+/);
            return parts[1] || parts[0];
        });
}

const enWords = parseWordlist(englishRaw);
const ptWords = parseWordlist(ptRaw);

export function GET({ url }) {
    const wordsCount = Number(url.searchParams.get('words')) || 6;
    const language = url.searchParams.get('language') || 'en';

    const dict = language === 'pt' ? ptWords : enWords;

    if (!dict || dict.length === 0) {
        return json({ error: 'Wordlist not loaded correctly' }, { status: 500 });
    }

    let result = [];
    // using crypto backend natively
    const array = new Uint32Array(wordsCount);
    crypto.getRandomValues(array);
    for (let i = 0; i < array.length; i++) {
        result.push(dict[array[i] % dict.length]);
    }

    return json({ passphrase: result.join('-') });
}
