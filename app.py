import random
from datetime import datetime
from io import BytesIO

import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------
PASSWORD_EXPIRY = {"KDPCW2026": None}

st.set_page_config(page_title="KDPEasy Crossword Creator", page_icon="\U0001F9E9", layout="wide")


def check_password() -> bool:
    if st.session_state.get("authed"):
        return True
    st.title("KDPEasy Crossword Creator")
    pw = st.text_input("Enter your access password", type="password")
    if pw:
        if pw in PASSWORD_EXPIRY:
            expiry = PASSWORD_EXPIRY[pw]
            if expiry is None or datetime.now() < expiry:
                st.session_state["authed"] = True
                st.rerun()
            else:
                st.error("This password has expired.")
        else:
            st.error("Incorrect password.")
    return False


# ---------------------------------------------------------------------------
# Word bank (starter set for v1 - Level 1 / Level 2, expand later to full
# Fry 1000-word tiers per project_tool9_crosswordcreator memory)
# ---------------------------------------------------------------------------
WORD_BANK = {
    "Level 1 (Easy)": [
        {"word": "SEE", "clue": "You do this with your eyes"},
        {"word": "RUN", "clue": "Move fast using your legs"},
        {"word": "JUMP", "clue": "Hop up into the air"},
        {"word": "STOP", "clue": "Opposite of go"},
        {"word": "LOOK", "clue": "Use your eyes to find something"},
        {"word": "PLAY", "clue": "Have fun with toys"},
        {"word": "HELP", "clue": "Give someone a hand"},
        {"word": "COME", "clue": "Move toward someone"},
        {"word": "MAKE", "clue": "Build or create something"},
        {"word": "GOOD", "clue": "Opposite of bad"},
        {"word": "BLUE", "clue": "Color of the sky"},
        {"word": "FUNNY", "clue": "Makes you laugh"},
        {"word": "LITTLE", "clue": "Opposite of big"},
        {"word": "YELLOW", "clue": "Color of a banana"},
        {"word": "WHERE", "clue": "Asking about a place"},
        {"word": "THREE", "clue": "The number after two"},
        {"word": "AWAY", "clue": "Not here"},
        {"word": "FIND", "clue": "Look for and discover"},
        {"word": "DOWN", "clue": "Opposite of up"},
        {"word": "BIG", "clue": "Opposite of little"},
        {"word": "RED", "clue": "Color of an apple"},
        {"word": "EAT", "clue": "Do this with food"},
        {"word": "SAY", "clue": "Speak words"},
        {"word": "RIDE", "clue": "Sit on a bike and go"},
        {"word": "SOON", "clue": "Very shortly"},
        {"word": "WENT", "clue": "Past tense of go"},
        {"word": "WANT", "clue": "Wish to have"},
        {"word": "LIKE", "clue": "Enjoy something"},
        {"word": "SAW", "clue": "Past tense of see"},
        {"word": "WELL", "clue": "In a good way"},
        {"word": "WHAT", "clue": "Asking about a thing"},
        {"word": "WITH", "clue": "Together with someone"},
        {"word": "THIS", "clue": "Points to something near"},
        {"word": "THAT", "clue": "Points to something far"},
        {"word": "THEY", "clue": "More than one person, not you or me"},
        {"word": "THERE", "clue": "Points to a place"},
        {"word": "WHO", "clue": "Asking about a person"},
        {"word": "NOW", "clue": "At this moment"},
        {"word": "OUT", "clue": "Opposite of in"},
        {"word": "NEW", "clue": "Opposite of old"},
    ],
    "Level 2 (Medium)": [
        {"word": "NEVER", "clue": "Opposite of always"},
        {"word": "ALWAYS", "clue": "Every single time"},
        {"word": "BETWEEN", "clue": "In the middle of two things"},
        {"word": "CLEAN", "clue": "Opposite of dirty"},
        {"word": "WRITE", "clue": "Use a pen to make letters"},
        {"word": "TRY", "clue": "Give it a go"},
        {"word": "THANK", "clue": "Say this when someone helps you"},
        {"word": "FAR", "clue": "Opposite of near"},
        {"word": "PICK", "clue": "Choose one"},
        {"word": "FOUND", "clue": "Past tense of find"},
        {"word": "LAUGH", "clue": "What you do when something is funny"},
        {"word": "PLEASE", "clue": "A polite word used when asking"},
        {"word": "WALK", "clue": "Move slowly on your feet"},
        {"word": "EIGHT", "clue": "The number after seven"},
        {"word": "DRINK", "clue": "Do this when you are thirsty"},
        {"word": "GROW", "clue": "To get bigger over time"},
        {"word": "FINISH", "clue": "Opposite of start"},
        {"word": "TOGETHER", "clue": "Not apart"},
        {"word": "TODAY", "clue": "This very day"},
        {"word": "SMALL", "clue": "Opposite of large"},
        {"word": "DONE", "clue": "Finished"},
        {"word": "WILL", "clue": "Going to happen in the future"},
        {"word": "LONG", "clue": "Opposite of short"},
        {"word": "BEFORE", "clue": "Earlier than"},
        {"word": "AFTER", "clue": "Later than"},
        {"word": "AROUND", "clue": "On every side of"},
        {"word": "ABOVE", "clue": "Higher than"},
        {"word": "BELOW", "clue": "Lower than"},
        {"word": "INSIDE", "clue": "Opposite of outside"},
        {"word": "OUTSIDE", "clue": "Opposite of inside"},
        {"word": "MORNING", "clue": "The start of the day"},
        {"word": "NIGHT", "clue": "When the sky is dark"},
        {"word": "FRIEND", "clue": "Someone you like to play with"},
        {"word": "HAPPY", "clue": "Feeling glad"},
        {"word": "SAD", "clue": "Feeling unhappy"},
        {"word": "ANGRY", "clue": "Feeling very upset"},
        {"word": "SLEEPY", "clue": "Feeling tired"},
        {"word": "HUNGRY", "clue": "Feeling like you need food"},
        {"word": "THIRSTY", "clue": "Feeling like you need a drink"},
        {"word": "GENTLE", "clue": "Soft and kind"},
    ],
}

TRIM_SIZES = {
    "Letter (8.5 x 11 in)": (8.5, 11.0),
    "Square (8.5 x 8.5 in)": (8.5, 8.5),
    "8 x 10 in": (8.0, 10.0),
    "6 x 9 in": (6.0, 9.0),
    "A4": (8.27, 11.69),
    "A5": (5.83, 8.27),
}


def get_word_pool(level_choice: str) -> list:
    if level_choice == "Mixed (Level 1 + 2)":
        return WORD_BANK["Level 1 (Easy)"] + WORD_BANK["Level 2 (Medium)"]
    return WORD_BANK[level_choice]


# ---------------------------------------------------------------------------
# Crossword generation engine (pure algorithm, no AI)
# ---------------------------------------------------------------------------
def _can_place(occupied, word, row, col, direction):
    if direction == "A":
        cells = [(row, col + i) for i in range(len(word))]
        before, after = (row, col - 1), (row, col + len(word))
    else:
        cells = [(row + i, col) for i in range(len(word))]
        before, after = (row - 1, col), (row + len(word), col)

    if before in occupied or after in occupied:
        return None

    intersections = 0
    for (r, c), ch in zip(cells, word):
        if (r, c) in occupied:
            if occupied[(r, c)] != ch:
                return None
            intersections += 1
        else:
            perp = [(r - 1, c), (r + 1, c)] if direction == "A" else [(r, c - 1), (r, c + 1)]
            for p in perp:
                if p in occupied:
                    return None
    return intersections


def _place_word(occupied, word, row, col, direction):
    if direction == "A":
        for i, ch in enumerate(word):
            occupied[(row, col + i)] = ch
    else:
        for i, ch in enumerate(word):
            occupied[(row + i, col)] = ch


def _attempt_layout(entries, target_count, rng):
    pool = list(entries)
    rng.shuffle(pool)
    pool.sort(key=lambda e: -len(e["word"]))

    occupied = {}
    placed = []

    first = pool[0]
    _place_word(occupied, first["word"], 0, 0, "A")
    placed.append({"word": first["word"], "clue": first["clue"], "row": 0, "col": 0, "dir": "A"})

    remaining = pool[1:]
    rng.shuffle(remaining)

    for cand in remaining:
        if len(placed) >= target_count:
            break
        word = cand["word"]
        if word in (p["word"] for p in placed):
            continue
        candidates = []
        for (r, c), ch in occupied.items():
            for i, wch in enumerate(word):
                if wch == ch:
                    candidates.append((r, c - i, "A"))
                    candidates.append((r - i, c, "D"))
        rng.shuffle(candidates)
        best = None
        for row, col, direction in candidates:
            score = _can_place(occupied, word, row, col, direction)
            if score and score >= 1:
                best = (row, col, direction)
                break
        if best:
            _place_word(occupied, word, *best)
            placed.append({"word": word, "clue": cand["clue"], "row": best[0], "col": best[1], "dir": best[2]})

    return occupied, placed


def _normalize(occupied, placed):
    rows = [r for r, _ in occupied]
    cols = [c for _, c in occupied]
    min_r, min_c = min(rows), min(cols)
    new_occupied = {(r - min_r, c - min_c): ch for (r, c), ch in occupied.items()}
    new_placed = [{**p, "row": p["row"] - min_r, "col": p["col"] - min_c} for p in placed]
    n_rows = max(rows) - min_r + 1
    n_cols = max(cols) - min_c + 1
    return new_occupied, new_placed, n_rows, n_cols


def _assign_numbers(occupied, placed, n_rows, n_cols):
    number_map = {}
    next_num = 1
    for r in range(n_rows):
        for c in range(n_cols):
            if (r, c) not in occupied:
                continue
            starts_across = (c == 0 or (r, c - 1) not in occupied) and (c + 1 < n_cols and (r, c + 1) in occupied)
            starts_down = (r == 0 or (r - 1, c) not in occupied) and (r + 1 < n_rows and (r + 1, c) in occupied)
            if starts_across or starts_down:
                number_map[(r, c)] = next_num
                next_num += 1
    for p in placed:
        p["number"] = number_map[(p["row"], p["col"])]
    return placed, number_map


def build_puzzle(word_pool, target_count, seed=None, attempts=10):
    rng = random.Random(seed)
    target_count = min(target_count, len(word_pool))
    best = None
    for _ in range(attempts):
        occupied, placed = _attempt_layout(word_pool, target_count, rng)
        if best is None or len(placed) > len(best[1]):
            best = (occupied, placed)
        if len(placed) >= target_count:
            break
    occupied, placed = best
    occupied, placed, n_rows, n_cols = _normalize(occupied, placed)
    placed, number_map = _assign_numbers(occupied, placed, n_rows, n_cols)
    return {
        "occupied": occupied,
        "placed": placed,
        "n_rows": n_rows,
        "n_cols": n_cols,
        "number_map": number_map,
    }


def build_book(word_pool, puzzle_count, words_per_puzzle, seed=None):
    rng = random.Random(seed)
    puzzles = []
    for i in range(puzzle_count):
        puzzle_seed = rng.randint(0, 10_000_000)
        puzzles.append(build_puzzle(word_pool, words_per_puzzle, seed=puzzle_seed))
    return puzzles


# ---------------------------------------------------------------------------
# On-screen preview (PIL)
# ---------------------------------------------------------------------------
def render_preview_image(puzzle, cell_px=36):
    n_rows, n_cols = puzzle["n_rows"], puzzle["n_cols"]
    occupied = puzzle["occupied"]
    number_map = puzzle["number_map"]
    img = Image.new("RGB", (n_cols * cell_px + 2, n_rows * cell_px + 2), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except Exception:
        font = ImageFont.load_default()

    for r in range(n_rows):
        for c in range(n_cols):
            if (r, c) not in occupied:
                continue
            x0, y0 = c * cell_px + 1, r * cell_px + 1
            x1, y1 = x0 + cell_px, y0 + cell_px
            draw.rectangle([x0, y0, x1, y1], outline="black", width=1)
            if (r, c) in number_map:
                draw.text((x0 + 2, y0 + 1), str(number_map[(r, c)]), fill="black", font=font)
    return img


# ---------------------------------------------------------------------------
# PDF building
# ---------------------------------------------------------------------------
MARGIN = 0.5


def _fit_cell_size(n_rows, n_cols, avail_w, avail_h):
    return min(avail_w / n_cols, avail_h / n_rows)


def draw_cover(pdf: FPDF, page_w, page_h, title, photo_bytes):
    pdf.add_page()
    if photo_bytes:
        img = Image.open(BytesIO(photo_bytes)).convert("RGB")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        pdf.image(buf, x=0, y=0, w=page_w, h=page_h)
    else:
        pdf.set_draw_color(0, 0, 0)
        pdf.rect(MARGIN, MARGIN, page_w - 2 * MARGIN, page_h - 2 * MARGIN)
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_xy(MARGIN, page_h / 2 - 0.5)
        pdf.multi_cell(page_w - 2 * MARGIN, 0.5, title, align="C")


def draw_answer_divider(pdf: FPDF, page_w, page_h):
    pdf.add_page()
    pdf.set_draw_color(0, 0, 0)
    box_w, box_h = 4.0, 1.2
    x = (page_w - box_w) / 2
    y = (page_h - box_h) / 2
    pdf.rect(x, y, box_w, box_h)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(x, y + box_h / 2 - 0.2)
    pdf.cell(box_w, 0.4, "ANSWER KEYS", align="C")


def draw_puzzle_page(pdf: FPDF, puzzle, page_w, page_h, puzzle_number):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(MARGIN, MARGIN)
    pdf.cell(page_w - 2 * MARGIN, 0.4, f"PUZZLE {puzzle_number:02d}", align="C")

    n_rows, n_cols = puzzle["n_rows"], puzzle["n_cols"]
    occupied = puzzle["occupied"]
    number_map = puzzle["number_map"]

    grid_top = MARGIN + 0.6
    avail_w = page_w - 2 * MARGIN
    avail_h = page_h * 0.5
    cell = _fit_cell_size(n_rows, n_cols, avail_w, avail_h)
    grid_w = cell * n_cols
    grid_left = MARGIN + (avail_w - grid_w) / 2

    pdf.set_line_width(0.01)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_font("Helvetica", size=max(6, min(8, cell * 18)))
    for r in range(n_rows):
        for c in range(n_cols):
            if (r, c) not in occupied:
                continue
            x = grid_left + c * cell
            y = grid_top + r * cell
            pdf.rect(x, y, cell, cell)
            if (r, c) in number_map:
                pdf.set_xy(x + 0.02, y + 0.01)
                pdf.cell(cell - 0.04, 0.12, str(number_map[(r, c)]), align="L")

    across = sorted([p for p in puzzle["placed"] if p["dir"] == "A"], key=lambda p: p["number"])
    down = sorted([p for p in puzzle["placed"] if p["dir"] == "D"], key=lambda p: p["number"])

    clue_top = grid_top + n_rows * cell + 0.3
    col_w = (page_w - 2 * MARGIN) / 2

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(MARGIN, clue_top)
    pdf.cell(col_w, 0.25, "Across")
    pdf.set_xy(MARGIN + col_w, clue_top)
    pdf.cell(col_w, 0.25, "Down")

    pdf.set_font("Helvetica", size=10)
    y = clue_top + 0.28
    for entry in across:
        pdf.set_xy(MARGIN, y)
        pdf.multi_cell(col_w - 0.1, 0.2, f"{entry['number']}. {entry['clue']}")
        y = max(y + 0.2, pdf.get_y())
    y_down = clue_top + 0.28
    for entry in down:
        pdf.set_xy(MARGIN + col_w, y_down)
        pdf.multi_cell(col_w - 0.1, 0.2, f"{entry['number']}. {entry['clue']}")
        y_down = max(y_down + 0.2, pdf.get_y())

    bank_top = max(y, y_down) + 0.2
    bank_words = sorted(p["word"] for p in puzzle["placed"])
    bank_text = "   ".join(bank_words)
    pdf.set_draw_color(0, 0, 0)
    pdf.rect(MARGIN, bank_top, page_w - 2 * MARGIN, 0.5)
    pdf.set_font("Helvetica", size=10)
    pdf.set_xy(MARGIN + 0.1, bank_top + 0.15)
    pdf.multi_cell(page_w - 2 * MARGIN - 0.2, 0.2, bank_text, align="C")


def draw_answer_grid_page(pdf: FPDF, puzzles, start_index, page_w, page_h):
    pdf.add_page()
    box_w = (page_w - 3 * MARGIN) / 2
    box_h = (page_h - 3 * MARGIN) / 2
    positions = [
        (MARGIN, MARGIN),
        (MARGIN * 2 + box_w, MARGIN),
        (MARGIN, MARGIN * 2 + box_h),
        (MARGIN * 2 + box_w, MARGIN * 2 + box_h),
    ]
    group = puzzles[start_index:start_index + 4]
    for idx, puzzle in enumerate(group):
        x, y = positions[idx]
        pdf.rect(x, y, box_w, box_h)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_xy(x, y + 0.1)
        pdf.cell(box_w, 0.25, f"PUZZLE {start_index + idx + 1:02d}", align="C")

        across = sorted([p for p in puzzle["placed"] if p["dir"] == "A"], key=lambda p: p["number"])
        down = sorted([p for p in puzzle["placed"] if p["dir"] == "D"], key=lambda p: p["number"])

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_xy(x + 0.15, y + 0.45)
        pdf.cell(box_w - 0.3, 0.18, "Across")
        cy = y + 0.65
        pdf.set_font("Helvetica", size=9)
        for entry in across:
            pdf.set_xy(x + 0.15, cy)
            pdf.cell(box_w - 0.3, 0.15, f"{entry['number']}.{entry['word'].title()}")
            cy += 0.15

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_xy(x + 0.15, cy + 0.05)
        pdf.cell(box_w - 0.3, 0.18, "Down")
        cy += 0.23
        pdf.set_font("Helvetica", size=9)
        for entry in down:
            pdf.set_xy(x + 0.15, cy)
            pdf.cell(box_w - 0.3, 0.15, f"{entry['number']}.{entry['word'].title()}")
            cy += 0.15


def build_crossword_pdf(puzzles, page_w, page_h, title, include_cover, photo_bytes, include_answers):
    pdf = FPDF(unit="in", format=(page_w, page_h))
    pdf.set_auto_page_break(False)

    if include_cover:
        draw_cover(pdf, page_w, page_h, title, photo_bytes)

    for i, puzzle in enumerate(puzzles):
        draw_puzzle_page(pdf, puzzle, page_w, page_h, i + 1)

    if include_answers:
        draw_answer_divider(pdf, page_w, page_h)
        for i in range(0, len(puzzles), 4):
            draw_answer_grid_page(pdf, puzzles, i, page_w, page_h)

    out = pdf.output()
    return bytes(out)


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
def main():
    if not check_password():
        st.stop()

    st.title("KDPEasy Crossword Creator")
    st.caption("Sight Words Crossword books, generated instantly - no AI, no prompts, no ChatGPT step.")

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Settings")
        level_choice = st.selectbox("Word level", list(WORD_BANK.keys()) + ["Mixed (Level 1 + 2)"])
        words_per_puzzle = st.slider("Words per puzzle", min_value=5, max_value=12, value=8)
        puzzle_count = st.number_input("Number of puzzles in this book", min_value=1, max_value=50, value=10)
        trim_label = st.selectbox("Page size (KDP trim)", list(TRIM_SIZES.keys()))
        include_answers = st.checkbox("Include answer key section", value=True)
        include_cover = st.checkbox("Include a cover page", value=True)
        photo_bytes = None
        if include_cover:
            uploaded = st.file_uploader("Cover photo (optional - leave empty for a plain text cover)", type=["png", "jpg", "jpeg"])
            if uploaded:
                photo_bytes = uploaded.read()

        book_title = "SIGHT WORDS CROSSWORD PUZZLES"

        generate = st.button("Generate Book", type="primary")

    word_pool = get_word_pool(level_choice)
    max_possible = len(word_pool)
    if words_per_puzzle > max_possible:
        with left:
            st.warning(f"Only {max_possible} words available at this level; using all of them per puzzle.")

    with right:
        st.subheader("Preview")
        preview_puzzle = build_puzzle(word_pool, words_per_puzzle, seed=42)
        preview_img = render_preview_image(preview_puzzle)
        st.image(preview_img, caption="Sample puzzle layout (regenerates with each book)")
        st.write(f"Grid size: {preview_puzzle['n_rows']} x {preview_puzzle['n_cols']}, "
                 f"{len(preview_puzzle['placed'])} words placed")

    if generate:
        page_w, page_h = TRIM_SIZES[trim_label]
        with st.spinner("Generating your book..."):
            puzzles = build_book(word_pool, int(puzzle_count), words_per_puzzle)
            pdf_bytes = build_crossword_pdf(
                puzzles, page_w, page_h, book_title, include_cover, photo_bytes, include_answers
            )
        st.success(f"Book ready - {len(puzzles)} puzzles.")
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="KDPEasy_Sight_Words_Crossword_Book.pdf",
            mime="application/pdf",
        )


if __name__ == "__main__":
    main()
