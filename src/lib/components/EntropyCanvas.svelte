<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    let canvas: HTMLCanvasElement;

    // Extracted out of onMount for better performance
    const CONNECTION_DIST = 140;
    const MOUSE_RADIUS = 180;
    const MOUSE_FORCE = 0.08;
    const CHARS = '0123456789abcdef'.split('');

    class Particle {
        x!: number;
        y!: number;
        vx!: number;
        vy!: number;
        radius!: number;
        baseAlpha!: number;
        alpha!: number;
        char!: string;
        charTimer!: number;
        showChar!: boolean;
        
        private getBounds: () => { W: number, H: number }; // Declara a propriedade aqui

        constructor(getBounds: () => { W: number, H: number }) { // Remove o 'private' daqui
            this.getBounds = getBounds; // Inicializa manualmente
            this.reset();
        }

        reset() {
            const { W, H } = this.getBounds();
            this.x = Math.random() * W;
            this.y = Math.random() * H;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
            this.radius = Math.random() * 1.5 + 0.5;
            this.baseAlpha = Math.random() * 0.3 + 0.15;
            this.alpha = this.baseAlpha;
            this.char = CHARS[Math.floor(Math.random() * CHARS.length)];
            this.charTimer = Math.random() * 200;
            this.showChar = Math.random() > 0.6;
        }

        update(mouse: { x: number, y: number }) {
            const { W, H } = this.getBounds();
            const dx = this.x - mouse.x;
            const dy = this.y - mouse.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < MOUSE_RADIUS && dist > 0) {
                const force = (MOUSE_RADIUS - dist) / MOUSE_RADIUS * MOUSE_FORCE;
                this.vx += (dx / dist) * force;
                this.vy += (dy / dist) * force;
                this.alpha = Math.min(this.baseAlpha + 0.4 * (1 - dist / MOUSE_RADIUS), 0.8);
            } else {
                this.alpha += (this.baseAlpha - this.alpha) * 0.05;
            }

            this.vx *= 0.99;
            this.vy *= 0.99;
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < -20) this.x = W + 20;
            if (this.x > W + 20) this.x = -20;
            if (this.y < -20) this.y = H + 20;
            if (this.y > H + 20) this.y = -20;

            this.charTimer--;
            if (this.charTimer <= 0) {
                this.char = CHARS[Math.floor(Math.random() * CHARS.length)];
                this.charTimer = Math.random() * 120 + 40;
            }
        }

        draw(ctx: CanvasRenderingContext2D) {
            if (this.showChar) {
                ctx.font = `${9 + this.radius * 2}px 'JetBrains Mono', monospace`;
                ctx.fillStyle = `rgba(255, 255, 255, ${this.alpha * 0.7})`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.char, this.x, this.y);
            } else {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 255, 255, ${this.alpha})`;
                ctx.fill();
            }
        }
    }

    onMount(() => {
        const ctx = canvas.getContext('2d')!;
        
        let W: number, H: number;
        let mouse = { x: -9999, y: -9999 };
        const PARTICLE_COUNT = 80;
        
        let animationFrameId: number;

        function resize() {
            W = canvas.width = window.innerWidth;
            H = canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        const handleMouseMove = (e: MouseEvent) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        };
        const handleMouseLeave = () => {
            mouse.x = -9999;
            mouse.y = -9999;
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseleave', handleMouseLeave);

        const getBounds = () => ({ W, H });
        const particles = Array.from({ length: PARTICLE_COUNT }, () => new Particle(getBounds));

        function drawConnections() {
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < CONNECTION_DIST) {
                        const alpha = (1 - dist / CONNECTION_DIST) * 0.12;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(255, 255, 255, ${alpha})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }
        }

        function animate() {
            ctx.clearRect(0, 0, W, H);

            if (mouse.x > 0 && mouse.y > 0) {
                const gradient = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, MOUSE_RADIUS);
                gradient.addColorStop(0, 'rgba(255, 255, 255, 0.03)');
                gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                ctx.fillStyle = gradient;
                ctx.fillRect(mouse.x - MOUSE_RADIUS, mouse.y - MOUSE_RADIUS, MOUSE_RADIUS * 2, MOUSE_RADIUS * 2);
            }

            drawConnections();

            for (const p of particles) {
                p.update(mouse);
                p.draw(ctx);
            }

            animationFrameId = requestAnimationFrame(animate);
        }

        animate();

        return () => {
            window.removeEventListener('resize', resize);
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseleave', handleMouseLeave);
            cancelAnimationFrame(animationFrameId);
        };
    });
</script>

<canvas bind:this={canvas} class="entropy-canvas"></canvas>

<style>
    .entropy-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        pointer-events: none;
    }
</style>
