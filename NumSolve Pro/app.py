import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NumSolve Pro",
    page_icon="🧮",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "show_methods" not in st.session_state:
    st.session_state.show_methods = False


# ============================================================
# THEME
# ============================================================

if st.session_state.dark_mode:

    BG = """
    radial-gradient(
        circle at top left,
        rgba(37,99,235,0.20),
        transparent 35%
    ),
    linear-gradient(
        135deg,
        #020617,
        #0f172a,
        #172554
    )
    """

    TEXT = "#f8fafc"
    SUBTEXT = "#cbd5e1"
    ACCENT = "#38bdf8"

else:

    BG = """
    radial-gradient(
        circle at top left,
        rgba(59,130,246,0.15),
        transparent 35%
    ),
    linear-gradient(
        135deg,
        #f8fafc,
        #dbeafe
    )
    """

    TEXT = "#0f172a"
    SUBTEXT = "#475569"
    ACCENT = "#0284c7"


# ============================================================
# CSS
# ============================================================

st.html(
f"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,500;0,600;0,700;0,800;1,500;1,600;1,700&display=swap'
);


/* ================================
   MAIN APP
   ================================ */

.stApp {{
    background: {BG};
    background-attachment: fixed;
}}


/* ================================
   HIDE STREAMLIT UI
   ================================ */

#MainMenu {{
    visibility: hidden;
}}

header {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}


/* ================================
   MAIN CONTAINER
   ================================ */

.block-container {{
    max-width: 1250px;
    padding-top: 1rem;
    padding-bottom: 4rem;
}}


/* ================================
   HERO
   ================================ */

.hero {{
    text-align: center;

    padding: 55px 30px 45px;

    margin-top: 20px;
    margin-bottom: 30px;

    border-radius: 30px;

    background:
        rgba(255,255,255,0.035);

    border:
        1px solid rgba(96,165,250,0.20);

    box-shadow:
        0 25px 70px rgba(0,0,0,0.25);

    backdrop-filter: blur(15px);
}}


/* ================================
   ICON
   ================================ */

.hero-icon {{
    font-size: 65px;

    margin-bottom: 10px;
}}


/* ================================
   TITLE
   ================================ */

.hero-title {{
    margin: 0;

    color: {TEXT};

    font-family: Poppins, sans-serif;

    font-size: 72px;

    font-weight: 800;

    letter-spacing: -2px;
}}


.hero-title span {{
    background:
        linear-gradient(
            90deg,
            #38bdf8,
            #60a5fa,
            #818cf8
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}


/* ================================
   SUBTITLE
   ================================ */

.hero-subtitle {{
    margin-top: 18px;

    color: {ACCENT};

    font-family: Poppins, sans-serif;

    font-size: 28px;

    font-weight: 600;
}}


/* ================================
   DESCRIPTION
   ================================ */

.hero-description {{
    margin-top: 10px;

    color: {SUBTEXT};

    font-family: Poppins, sans-serif;

    font-size: 18px;

    font-style: italic;
}}


/* ================================
   BADGES
   ================================ */

.badges {{
    display: flex;

    justify-content: center;

    gap: 10px;

    flex-wrap: wrap;

    margin-top: 25px;
}}


.badge {{
    padding: 7px 15px;

    border-radius: 50px;

    background:
        rgba(56,189,248,0.08);

    border:
        1px solid
        rgba(56,189,248,0.20);

    color: {ACCENT};

    font-size: 13px;

    font-weight: 600;
}}


/* ================================
   SECTION TITLE
   ================================ */

.section-title {{
    text-align: center;

    color: {TEXT};

    font-family: Poppins, sans-serif;

    font-size: 38px;

    font-weight: 700;

    margin-top: 35px;
}}


.section-subtitle {{
    text-align: center;

    color: {SUBTEXT};

    font-size: 15px;

    margin-bottom: 30px;
}}


/* ================================
   METHOD CARD
   ================================ */

.method-card {{
    padding: 30px;

    border-radius: 22px;

    background:
        rgba(255,255,255,0.05);

    border:
        1px solid
        rgba(96,165,250,0.20);

    box-shadow:
        0 15px 45px
        rgba(0,0,0,0.20);

    transition:
        0.3s ease;
}}


.method-card:hover {{
    transform:
        translateY(-5px);

    border-color:
        rgba(56,189,248,0.55);

    box-shadow:
        0 20px 55px
        rgba(37,99,235,0.25);
}}


.method-icon {{
    font-size: 38px;
}}


.method-title {{
    color: {TEXT};

    font-size: 23px;

    font-weight: 700;

    margin-top: 10px;
}}


.method-text {{
    color: {SUBTEXT};

    font-size: 14px;

    line-height: 1.7;

    margin-top: 8px;
}}


</style>
"""
)


# ============================================================
# TOP BAR
# ============================================================

left, middle, right = st.columns([8, 1.2, 1.3])


with right:

    new_mode = st.toggle(
        "🌙 Dark",
        value=st.session_state.dark_mode
    )

    if new_mode != st.session_state.dark_mode:

        st.session_state.dark_mode = new_mode

        st.rerun()


# ============================================================
# HERO
# ============================================================

st.html(
"""
<div class="hero">

    <div class="hero-icon">
        🧮
    </div>

    <h1 class="hero-title">
        Num<span>Solve</span> Pro
    </h1>

    <div class="hero-subtitle">
        Advanced Numerical Methods Simulator
    </div>

    <div class="hero-description">
        Solve Numerical Methods Step by Step
    </div>

    <div class="badges">

        <div class="badge">
            📐 Mathematical Analysis
        </div>

        <div class="badge">
            📊 Visualization
        </div>

        <div class="badge">
            🎯 Error Analysis
        </div>

        <div class="badge">
            📚 Learning Focused
        </div>

    </div>

</div>
"""
)


# ============================================================
# GET STARTED
# ============================================================

_, center, _ = st.columns([1, 2, 1])


with center:

    if st.session_state.show_methods:

        button_text = "❌ Hide Methods"

    else:

        button_text = "🚀 Get Started"


    if st.button(
        button_text,
        use_container_width=True,
        type="primary"
    ):

        st.session_state.show_methods = (
            not st.session_state.show_methods
        )

        st.rerun()


# ============================================================
# METHODS
# ============================================================

if st.session_state.show_methods:

    st.html(
    """
    <div class="section-title">
        Numerical Methods
    </div>

    <div class="section-subtitle">
        Choose a method to begin your numerical analysis
    </div>
    """
    )


    _, card, _ = st.columns([1, 2, 1])


    with card:

        st.html(
        """
        <div class="method-card">

            <div class="method-icon">
                📈
            </div>

            <div class="method-title">
                Interpolation
            </div>

            <div class="method-text">

                Estimate unknown values between known
                data points using numerical interpolation
                techniques.

                <br><br>

                <b>Method:</b> Equal Interval

            </div>

        </div>
        """
        )


        if st.button(
            "Open Interpolation →",
            use_container_width=True
        ):

            st.switch_page(
                "pages/interpolation.py"
            )


# ============================================================
# FOOTER
# ============================================================

st.html(
f"""
<div style="
    text-align:center;
    margin-top:60px;
    padding:20px;
    color:{SUBTEXT};
    font-size:13px;
">

    <b style="color:{ACCENT};">
        NumSolve Pro
    </b>

    &nbsp;•&nbsp;

    Advanced Numerical Methods Simulator

    <br><br>

    <i>
        Learn • Calculate • Visualize • Understand
    </i>

</div>
"""
)