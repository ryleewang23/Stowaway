import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
            :root {
                --ink: #183247;
                --muted: #66798a;
                --accent: #4f8fb3;
                --accent-dark: #2f6f95;
                --accent-soft: #edf7fb;
                --surface: rgba(255, 255, 255, 0.94);
                --border: rgba(69, 105, 130, 0.16);
                --shadow: 0 12px 34px rgba(35, 70, 94, 0.08);
            }

            /* Remove Streamlit chrome for a more app-like appearance. */
            header[data-testid="stHeader"] {
                display: none;
            }

            #MainMenu,
            footer {
                visibility: hidden;
            }

            .stApp {
                background:
                    radial-gradient(
                        circle at 92% 4%,
                        rgba(126, 195, 219, 0.17),
                        transparent 25rem
                    ),
                    radial-gradient(
                        circle at 5% 55%,
                        rgba(182, 222, 234, 0.13),
                        transparent 24rem
                    ),
                    linear-gradient(
                        180deg,
                        #fbfdfe 0%,
                        #f5fafc 100%
                    );
                color: var(--ink);
            }

            .block-container {
                max-width: 980px;
                padding-top: 1.25rem;
                padding-bottom: 4rem;
            }

            .hero-card {
                padding: 1.25rem 1.4rem;
                border: 1px solid var(--border);
                border-radius: 24px;
                background:
                    linear-gradient(
                        135deg,
                        rgba(255, 255, 255, 0.98),
                        rgba(239, 248, 252, 0.96)
                    );
                box-shadow: var(--shadow);
                margin-bottom: 1rem;
            }

            .brand-row {
                display: flex;
                align-items: center;
                gap: 0.85rem;
            }

            .brand-mark {
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                width: auto;
                height: auto;
                background: none;
                box-shadow: none;
                border: none;
                padding: 0;
                margin-right: .3rem;
            }

            .hero-title {
                color: var(--ink);
                font-size: clamp(1.65rem, 5vw, 2.25rem);
                font-weight: 800;
                line-height: 1;
                letter-spacing: -0.035em;
            }

            .hero-subtitle {
                color: var(--muted);
                font-size: 0.92rem;
                margin-top: 0.28rem;
            }

            .hero-tagline {
                color: var(--ink);
                font-size: 0.95rem;
                line-height: 1.5;
                margin-top: 1rem;
                max-width: 43rem;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-color: var(--border);
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.74);
                box-shadow: 0 8px 26px rgba(35, 70, 94, 0.04);
            }

            .summary-card {
                padding: 1rem 1.05rem;
                border-radius: 16px;
                border: 1px solid var(--border);
                background: var(--surface);
                box-shadow: 0 6px 20px rgba(35, 70, 94, 0.04);
                margin-bottom: 0.8rem;
            }

            .tip-card {
                padding: 0.82rem 0.95rem;
                border-radius: 14px;
                background: var(--accent-soft);
                border: 1px solid var(--border);
                margin-bottom: 0.5rem;
                color: var(--ink);
            }

            .item-reason {
                color: var(--muted);
                font-size: 0.8rem;
                line-height: 1.35;
                margin-top: -0.22rem;
            }

            .source-badge {
                display: inline-block;
                border-radius: 999px;
                background: var(--accent-soft);
                color: var(--accent-dark);
                font-size: 0.64rem;
                font-weight: 750;
                padding: 0.11rem 0.4rem;
                margin-left: 0.35rem;
                vertical-align: middle;
            }

            div[data-testid="stMetric"] {
                border: 1px solid var(--border);
                background: var(--surface);
                border-radius: 16px;
                padding: 0.75rem 0.85rem;
                box-shadow: 0 6px 20px rgba(35, 70, 94, 0.04);
            }

            div[data-testid="stExpander"] {
                border: 1px solid var(--border);
                border-radius: 16px;
                overflow: hidden;
                background: var(--surface);
                box-shadow: 0 5px 16px rgba(35, 70, 94, 0.035);
            }

            .stButton > button,
            .stDownloadButton > button,
            a[data-testid="stLinkButton"] {
                border-radius: 12px !important;
                min-height: 2.65rem;
                transition:
                    transform 0.15s ease,
                    box-shadow 0.15s ease;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover,
            a[data-testid="stLinkButton"]:hover {
                transform: translateY(-1px);
                box-shadow:
                    0 7px 18px rgba(35, 70, 94, 0.10);
            }

            div[data-testid="stProgress"] > div {
                border-radius: 999px;
                overflow: hidden;
            }

            input,
            textarea,
            [data-baseweb="select"] > div {
                border-radius: 12px !important;
            }

            img {
                border-radius: 18px;
            }

            @media (max-width: 640px) {
                .block-container {
                    padding-left: 0.72rem;
                    padding-right: 0.72rem;
                    padding-top: 0.72rem;
                }

                .hero-card {
                    padding: 1rem;
                    border-radius: 19px;
                }

                .brand-mark {
                    width: 42px;
                    height: 42px;
                    border-radius: 13px;
                }

                .hero-tagline {
                    font-size: 0.88rem;
                }

                div[data-testid="stHorizontalBlock"] {
                    gap: 0.45rem;
                }

                button,
                input,
                textarea {
                    font-size: 16px !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )
