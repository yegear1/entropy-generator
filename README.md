# YeHub Entropy Generator

Enterprise-grade cryptographic key synthesis, built with SvelteKit.

![YeHub Entropy](https://raw.githubusercontent.com/yegear1/entropy-generator/main/preview.png)

## Overview

YeHub Entropy is a highly customizable, client-server password and passphrase generator designed to be secure and beautiful. It uses Svelte 5 for a highly reactive and performant frontend, and a SvelteKit API endpoint for securely generating entropy via Web Crypto APIs.

### Features
- **Password Generation**: Highly customizable (length, uppercase, lowercase, numbers, symbols, and emojis).
- **Passphrase Generation**: Uses EFF Diceware-style lists in English and Portuguese.
- **Entropy Meter**: Real-time measurement of brute-force resistance (measured in bits).
- **Beautiful UI**: Modern aesthetics featuring skeleton loaders, animated cooldowns, and an interactive background canvas.

## Architecture

This project was built entirely with Node.js and SvelteKit:
- **Frontend** (`src/routes/+page.svelte`): Uses Svelte 5 runes (`$state`, `$derived`) for fluid UI state management.
- **Background** (`src/lib/components/EntropyCanvas.svelte`): Extracted canvas orchestration that responds to mouse distance and repels particles.
- **Backend APIs** (`src/routes/api/v1/generate/...`):
  - `/password`: Serves cryptographically secure passwords based on selected character pools.
  - `/passphrase`: Reads raw dictionary files (`.txt`) via Vite text imports and returns secure multi-word passphrases.

## Getting Started

To run this project locally:

1. **Install dependencies**
   ```sh
   npm install
   ```

2. **Start the development server**
   ```sh
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173/`.

### Building for Production

To create an optimized production version of your app:
```sh
npm run build
```
You can preview the built app using `npm run preview`.

## License
MIT License.
