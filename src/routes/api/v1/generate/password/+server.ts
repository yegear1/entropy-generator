import { json } from '@sveltejs/kit';

export function GET({ url }) {
    const length = Number(url.searchParams.get('length')) || 24;
    const use_upper = url.searchParams.get('use_upper') === 'true';
    const use_lower = url.searchParams.get('use_lower') === 'true';
    const use_digits = url.searchParams.get('use_digits') === 'true';
    const use_specials = url.searchParams.get('use_specials') === 'true';
    const use_emojis = url.searchParams.get('use_emojis') === 'true';

    let chars = '';
    if (use_upper) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (use_lower) chars += 'abcdefghijklmnopqrstuvwxyz';
    if (use_digits) chars += '0123456789';
    if (use_specials) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';
    if (use_emojis) chars += '🚀👽🔥🤖🌟💎🛡️🔐';
    if (!chars) chars = 'abcdefghijklmnopqrstuvwxyz'; // fallback

    let password = '';
    const charArray = Array.from(chars); 
    
    const array = new Uint32Array(length);
    crypto.getRandomValues(array);
    for (let i = 0; i < array.length; i++) {
        password += charArray[array[i] % charArray.length];
    }

    return json({ password });
}
