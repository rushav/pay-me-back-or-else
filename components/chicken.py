import streamlit.components.v1 as components


def render_chicken(rage_level: int, height: int = 420):
    """Render the chicken mascot with mouse-tracking eyes. Expression changes with rage level."""

    rage_extras = {
        1: {
            "body_fill": "#FFD700",
            "face_tint": "",
            "extras_svg": """
                <!-- Halo -->
                <ellipse cx="150" cy="48" rx="30" ry="8" fill="none" stroke="#FFD700" stroke-width="3" stroke-dasharray="4,3"/>
                <ellipse cx="150" cy="45" rx="28" ry="7" fill="none" stroke="#FFF176" stroke-width="2"/>
                <!-- Pink cheeks -->
                <circle cx="122" cy="115" r="10" fill="#FFB6C1" opacity="0.6"/>
                <circle cx="178" cy="115" r="10" fill="#FFB6C1" opacity="0.6"/>
                <!-- Smile -->
                <path d="M135 125 Q150 140 165 125" fill="none" stroke="#1A1A1A" stroke-width="3" stroke-linecap="round"/>
                <!-- Heart -->
                <path d="M195 80 C195 75 200 70 205 75 C210 70 215 75 215 80 C215 90 205 95 205 95 C205 95 195 90 195 80Z" fill="#FF6B6B" stroke="#1A1A1A" stroke-width="1.5"/>
                <!-- Quill in wing -->
                <line x1="95" y1="180" x2="70" y2="130" stroke="#8B4513" stroke-width="3" stroke-linecap="round"/>
                <path d="M70 130 L60 115 L75 120 Z" fill="#1A1A1A"/>
            """,
            "beak_path": "M140 118 L150 132 L160 118 Z",
            "eyebrow_svg": "",
        },
        2: {
            "body_fill": "#FFD700",
            "face_tint": "",
            "extras_svg": """
                <!-- Speech bubble "..." -->
                <rect x="185" y="60" width="55" height="30" rx="10" fill="white" stroke="#1A1A1A" stroke-width="2" stroke-dasharray="3,2"/>
                <circle cx="200" cy="75" r="3" fill="#1A1A1A"/>
                <circle cx="212" cy="75" r="3" fill="#1A1A1A"/>
                <circle cx="224" cy="75" r="3" fill="#1A1A1A"/>
                <!-- Quill tapping -->
                <line x1="92" y1="185" x2="68" y2="135" stroke="#8B4513" stroke-width="3" stroke-linecap="round">
                    <animateTransform attributeName="transform" type="rotate" values="-2 92 185;2 92 185;-2 92 185" dur="0.5s" repeatCount="indefinite"/>
                </line>
                <path d="M68 135 L58 120 L73 125 Z" fill="#1A1A1A">
                    <animateTransform attributeName="transform" type="rotate" values="-2 92 185;2 92 185;-2 92 185" dur="0.5s" repeatCount="indefinite"/>
                </path>
            """,
            "beak_path": "M138 118 L150 135 L162 118 Z",
            "eyebrow_svg": """
                <!-- One raised eyebrow -->
                <line x1="160" y1="85" x2="180" y2="82" stroke="#1A1A1A" stroke-width="3" stroke-linecap="round"/>
            """,
        },
        3: {
            "body_fill": "#FFD700",
            "face_tint": '<circle cx="150" cy="110" r="45" fill="#FF6B6B" opacity="0.2"/>',
            "extras_svg": """
                <!-- Steam lines -->
                <path d="M110 55 Q105 40 110 25" fill="none" stroke="#999" stroke-width="2.5" stroke-linecap="round" opacity="0.7">
                    <animate attributeName="d" values="M110 55 Q105 40 110 25;M110 55 Q115 40 110 25;M110 55 Q105 40 110 25" dur="1s" repeatCount="indefinite"/>
                </path>
                <path d="M190 55 Q195 40 190 25" fill="none" stroke="#999" stroke-width="2.5" stroke-linecap="round" opacity="0.7">
                    <animate attributeName="d" values="M190 55 Q195 40 190 25;M190 55 Q185 40 190 25;M190 55 Q195 40 190 25" dur="1s" repeatCount="indefinite"/>
                </path>
                <!-- Sweat drops -->
                <ellipse cx="100" cy="95" rx="4" ry="6" fill="#87CEEB" opacity="0.7"/>
                <ellipse cx="200" cy="90" rx="3" ry="5" fill="#87CEEB" opacity="0.7"/>
                <!-- Quill gripped tight -->
                <line x1="90" y1="178" x2="60" y2="125" stroke="#8B4513" stroke-width="4" stroke-linecap="round"/>
                <path d="M60 125 L48 108 L65 115 Z" fill="#1A1A1A"/>
                <!-- Ruffled feathers -->
                <path d="M90 150 L75 140 L80 155" fill="none" stroke="#1A1A1A" stroke-width="2"/>
                <path d="M210 150 L225 140 L220 155" fill="none" stroke="#1A1A1A" stroke-width="2"/>
                <path d="M85 170 L68 165 L75 178" fill="none" stroke="#1A1A1A" stroke-width="2"/>
            """,
            "beak_path": "M136 118 L150 136 L164 118 Z",
            "eyebrow_svg": """
                <line x1="123" y1="82" x2="140" y2="88" stroke="#1A1A1A" stroke-width="3.5" stroke-linecap="round"/>
                <line x1="160" y1="88" x2="177" y2="82" stroke="#1A1A1A" stroke-width="3.5" stroke-linecap="round"/>
            """,
        },
        4: {
            "body_fill": "#CC9900",
            "face_tint": '<circle cx="150" cy="110" r="50" fill="#8B0000" opacity="0.25"/>',
            "extras_svg": """
                <!-- Devil horns -->
                <path d="M118 62 L105 30 L120 50" fill="#8B0000" stroke="#1A1A1A" stroke-width="2.5"/>
                <path d="M182 62 L195 30 L180 50" fill="#8B0000" stroke="#1A1A1A" stroke-width="2.5"/>
                <!-- Pitchfork -->
                <line x1="88" y1="185" x2="55" y2="110" stroke="#8B0000" stroke-width="4" stroke-linecap="round"/>
                <path d="M42 100 L55 110 L68 100 M42 100 L42 85 M55 110 L55 82 M68 100 L68 85" fill="none" stroke="#8B0000" stroke-width="3" stroke-linecap="round"/>
                <!-- Flames around chicken -->
                <path d="M70 220 Q65 195 75 210 Q70 185 82 200 Q78 180 90 200" fill="none" stroke="#FF4500" stroke-width="2.5" opacity="0.8">
                    <animate attributeName="d" values="M70 220 Q65 195 75 210 Q70 185 82 200 Q78 180 90 200;M70 220 Q62 190 78 208 Q72 182 85 198 Q80 175 92 198;M70 220 Q65 195 75 210 Q70 185 82 200 Q78 180 90 200" dur="0.8s" repeatCount="indefinite"/>
                </path>
                <path d="M210 220 Q215 195 205 210 Q210 185 198 200 Q202 180 190 200" fill="none" stroke="#FF4500" stroke-width="2.5" opacity="0.8">
                    <animate attributeName="d" values="M210 220 Q215 195 205 210 Q210 185 198 200 Q202 180 190 200;M210 220 Q218 190 202 208 Q212 182 195 198 Q200 175 188 198;M210 220 Q215 195 205 210 Q210 185 198 200 Q202 180 190 200" dur="0.8s" repeatCount="indefinite"/>
                </path>
                <!-- IOU pile -->
                <rect x="115" y="280" width="70" height="15" rx="2" fill="#FFF8DC" stroke="#1A1A1A" stroke-width="1.5" transform="rotate(-5 150 287)"/>
                <rect x="120" y="272" width="65" height="14" rx="2" fill="#FFF8DC" stroke="#1A1A1A" stroke-width="1.5" transform="rotate(3 152 279)"/>
                <text x="130" y="290" font-family="'Rock Salt', cursive" font-size="8" fill="#8B0000" transform="rotate(-5 150 287)">IOU IOU</text>
                <!-- Fire feathers -->
                <path d="M95 155 L78 148 L82 160" fill="#FF4500" stroke="#1A1A1A" stroke-width="1.5" opacity="0.8"/>
                <path d="M205 155 L222 148 L218 160" fill="#FF4500" stroke="#1A1A1A" stroke-width="1.5" opacity="0.8"/>
            """,
            "beak_path": "M134 118 L150 140 L166 118 Z",
            "eyebrow_svg": """
                <line x1="120" y1="80" x2="140" y2="88" stroke="#8B0000" stroke-width="4" stroke-linecap="round"/>
                <line x1="160" y1="88" x2="180" y2="80" stroke="#8B0000" stroke-width="4" stroke-linecap="round"/>
            """,
        },
    }

    cfg = rage_extras[rage_level]

    pupil_html = ""
    if rage_level == 4:
        pupil_html = """
            <circle class="pupil left-pupil" cx="135" cy="100" r="6" fill="#FF4500"/>
            <circle class="pupil-glow left-pupil" cx="135" cy="100" r="3" fill="#FFFF00" opacity="0.8"/>
            <circle class="pupil right-pupil" cx="165" cy="100" r="6" fill="#FF4500"/>
            <circle class="pupil-glow right-pupil" cx="165" cy="100" r="3" fill="#FFFF00" opacity="0.8"/>
        """
    else:
        pupil_html = """
            <circle class="pupil left-pupil" cx="135" cy="100" r="5" fill="#1A1A1A"/>
            <circle class="pupil right-pupil" cx="165" cy="100" r="5" fill="#1A1A1A"/>
        """

    html = f"""
    <div id="chicken-container" style="width:100%;display:flex;justify-content:center;align-items:center;min-height:{height}px;">
    <svg viewBox="50 15 200 300" width="280" height="{height}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;">
        <!-- Body -->
        <ellipse cx="150" cy="190" rx="65" ry="75" fill="{cfg['body_fill']}" stroke="#1A1A1A" stroke-width="3.5"/>

        <!-- Belly -->
        <ellipse cx="150" cy="205" rx="40" ry="45" fill="#FFF8DC" stroke="#1A1A1A" stroke-width="2" opacity="0.7"/>

        <!-- Face tint -->
        {cfg['face_tint']}

        <!-- Head -->
        <circle cx="150" cy="95" r="45" fill="{cfg['body_fill']}" stroke="#1A1A1A" stroke-width="3.5"/>

        <!-- Comb -->
        <path d="M130 55 Q135 35 140 55 Q145 30 150 55 Q155 35 160 55 Q165 40 170 55" fill="#FF4444" stroke="#1A1A1A" stroke-width="2.5"/>

        <!-- Eye whites -->
        <ellipse cx="135" cy="98" rx="14" ry="15" fill="white" stroke="#1A1A1A" stroke-width="2.5"/>
        <ellipse cx="165" cy="98" rx="14" ry="15" fill="white" stroke="#1A1A1A" stroke-width="2.5"/>

        <!-- Pupils (move with mouse) -->
        {pupil_html}

        <!-- Eyebrows -->
        {cfg['eyebrow_svg']}

        <!-- Beak -->
        <path d="{cfg['beak_path']}" fill="#FF8C00" stroke="#1A1A1A" stroke-width="2.5" stroke-linejoin="round"/>

        <!-- Wattle -->
        <ellipse cx="150" cy="133" rx="6" ry="9" fill="#FF4444" stroke="#1A1A1A" stroke-width="2"/>

        <!-- Wings -->
        <path d="M85 175 Q60 185 70 210 Q75 225 90 220" fill="{cfg['body_fill']}" stroke="#1A1A1A" stroke-width="3" fill-opacity="0.9"/>
        <path d="M215 175 Q240 185 230 210 Q225 225 210 220" fill="{cfg['body_fill']}" stroke="#1A1A1A" stroke-width="3" fill-opacity="0.9"/>

        <!-- Legs -->
        <line x1="130" y1="260" x2="125" y2="290" stroke="#FF8C00" stroke-width="4" stroke-linecap="round"/>
        <line x1="170" y1="260" x2="175" y2="290" stroke="#FF8C00" stroke-width="4" stroke-linecap="round"/>
        <!-- Feet -->
        <path d="M110 290 L125 290 L130 290 L140 290" fill="none" stroke="#FF8C00" stroke-width="3.5" stroke-linecap="round"/>
        <path d="M160 290 L175 290 L180 290 L190 290" fill="none" stroke="#FF8C00" stroke-width="3.5" stroke-linecap="round"/>

        <!-- Rage-specific extras -->
        {cfg['extras_svg']}
    </svg>
    </div>

    <script>
    (function() {{
        const container = document.getElementById('chicken-container');
        const leftPupils = container.querySelectorAll('.left-pupil');
        const rightPupils = container.querySelectorAll('.right-pupil');
        const leftEyeCenter = {{ x: 135, y: 100 }};
        const rightEyeCenter = {{ x: 165, y: 100 }};
        const maxRadius = 8;

        function movePupils(pupils, eyeCenter, mouseX, mouseY) {{
            const svg = container.querySelector('svg');
            if (!svg) return;
            const rect = svg.getBoundingClientRect();
            const svgWidth = 200;
            const svgHeight = 300;
            const scaleX = svgWidth / rect.width;
            const scaleY = svgHeight / rect.height;
            const localX = (mouseX - rect.left) * scaleX + 50;
            const localY = (mouseY - rect.top) * scaleY + 15;

            const dx = localX - eyeCenter.x;
            const dy = localY - eyeCenter.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const clampedDist = Math.min(dist, maxRadius);
            const angle = Math.atan2(dy, dx);
            const moveX = Math.cos(angle) * clampedDist;
            const moveY = Math.sin(angle) * clampedDist;

            pupils.forEach(p => {{
                p.setAttribute('cx', eyeCenter.x + moveX);
                p.setAttribute('cy', eyeCenter.y + moveY);
            }});
        }}

        window.addEventListener('mousemove', function(e) {{
            movePupils(leftPupils, leftEyeCenter, e.clientX, e.clientY);
            movePupils(rightPupils, rightEyeCenter, e.clientX, e.clientY);
        }});

        // Also listen inside parent frames
        try {{
            if (window.parent && window.parent !== window) {{
                window.parent.addEventListener('mousemove', function(e) {{
                    movePupils(leftPupils, leftEyeCenter, e.clientX, e.clientY);
                    movePupils(rightPupils, rightEyeCenter, e.clientX, e.clientY);
                }});
            }}
        }} catch(err) {{}}
    }})();
    </script>

    <style>
        html, body {{
            background: transparent !important;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
        .pupil, .pupil-glow {{
            transition: cx 0.1s ease-out, cy 0.1s ease-out;
        }}
    </style>
    """

    components.html(html, height=height)
