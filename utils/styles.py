def load_css():
    return """
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }

    .stApp {
        background-color: #F5F7FB;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #052B5B 0%, #021D3A 100%);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
    """