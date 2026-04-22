import streamlit.components.v1 as components


def render_loading(rage_level: int, height: int = 350):
    """Render an animated loading chicken scribbling at a desk with cycling messages."""

    if rage_level == 4:
        messages_js = """[
            "SUMMONING THE LETTER FROM THE DEPTHS...",
            "THE CHICKEN HAS ENTERED RAGE MODE...",
            "TYPING WITH FURY... AND TINY WINGS...",
            "THIS ONE'S GONNA HURT...",
            "CHANNELING PURE DEMONIC ENERGY...",
            "THE FLAMES ARE GETTING HIGHER..."
        ]"""
        msg_color = "#D32F2F"
    else:
        messages_js = """[
            "The chicken is thinking really hard...",
            "Scribbling furiously...",
            "Finding the perfect words to destroy them...",
            "Almost done... just adding extra sass...",
            "Consulting the ancient texts of pettiness...",
            "The chicken has strong feelings about this..."
        ]"""
        msg_color = "#1A1A1A"

    html = f"""
    <div style="text-align:center;padding:2rem;font-family:'Gaegu',cursive;">
        <svg viewBox="0 0 250 200" width="250" height="200" xmlns="http://www.w3.org/2000/svg">
            <!-- Desk -->
            <rect x="60" y="150" width="130" height="10" rx="2" fill="#8B6914" stroke="#1A1A1A" stroke-width="2.5"/>
            <line x1="75" y1="160" x2="75" y2="195" stroke="#1A1A1A" stroke-width="3"/>
            <line x1="175" y1="160" x2="175" y2="195" stroke="#1A1A1A" stroke-width="3"/>

            <!-- Paper on desk -->
            <rect x="90" y="135" width="45" height="20" rx="1" fill="#FFF8DC" stroke="#1A1A1A" stroke-width="1.5" transform="rotate(-3 112 145)"/>
            <line x1="95" y1="141" x2="125" y2="140" stroke="#ccc" stroke-width="1"/>
            <line x1="95" y1="146" x2="120" y2="145" stroke="#ccc" stroke-width="1"/>

            <!-- Flying paper -->
            <rect x="155" y="120" width="30" height="20" rx="1" fill="#FFF8DC" stroke="#1A1A1A" stroke-width="1" transform="rotate(15 170 130)" opacity="0.7">
                <animateTransform attributeName="transform" type="translate" values="0,0;20,-40;40,-80" dur="2s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="0.7;0.5;0" dur="2s" repeatCount="indefinite"/>
            </rect>

            <!-- Chicken body (simplified) -->
            <ellipse cx="125" cy="120" rx="35" ry="35" fill="#FFD700" stroke="#1A1A1A" stroke-width="3"/>
            <!-- Head -->
            <circle cx="125" cy="80" r="22" fill="#FFD700" stroke="#1A1A1A" stroke-width="3"/>
            <!-- Comb -->
            <path d="M115 60 Q118 48 121 60 Q124 46 127 60 Q130 50 133 60" fill="#FF4444" stroke="#1A1A1A" stroke-width="2"/>
            <!-- Eyes (focused on paper) -->
            <circle cx="118" cy="78" r="5" fill="white" stroke="#1A1A1A" stroke-width="2"/>
            <circle cx="132" cy="78" r="5" fill="white" stroke="#1A1A1A" stroke-width="2"/>
            <circle cx="119" cy="80" r="2.5" fill="#1A1A1A"/>
            <circle cx="133" cy="80" r="2.5" fill="#1A1A1A"/>
            <!-- Beak -->
            <path d="M121 88 L125 96 L129 88 Z" fill="#FF8C00" stroke="#1A1A1A" stroke-width="2"/>

            <!-- Wing + quill (animated) -->
            <g>
                <animateTransform attributeName="transform" type="rotate" values="-5 100 130;5 100 130;-5 100 130" dur="0.4s" repeatCount="indefinite"/>
                <path d="M95 115 Q75 120 80 135" fill="#FFD700" stroke="#1A1A1A" stroke-width="2.5"/>
                <line x1="80" y1="130" x2="90" y2="140" stroke="#8B4513" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M90 140 L95 148 L87 145 Z" fill="#1A1A1A" opacity="0.8"/>
            </g>
        </svg>

        <div id="loading-msg" style="font-family:'Schoolbell',cursive;font-size:1.3rem;color:{msg_color};margin-top:0.5rem;min-height:2rem;">
        </div>
    </div>

    <script>
    (function() {{
        const messages = {messages_js};
        let idx = 0;
        const el = document.getElementById('loading-msg');
        if (el) {{
            el.textContent = messages[0];
            setInterval(function() {{
                idx = (idx + 1) % messages.length;
                el.style.opacity = 0;
                setTimeout(function() {{
                    el.textContent = messages[idx];
                    el.style.opacity = 1;
                }}, 300);
            }}, 2000);
        }}
    }})();
    </script>

    <style>
        html, body {{
            background: transparent !important;
            margin: 0;
            padding: 0;
        }}
        #loading-msg {{ transition: opacity 0.3s ease; }}
    </style>
    """

    components.html(html, height=height)
